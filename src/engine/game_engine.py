import asyncio
import pygame
import esper

from src.create.prefab_creator import crear_spawner_enemigos, crear_cuadrado_jugador, crear_input_jugador, crear_bala, crear_texto, agregar_escudo_jugador, crear_hud_escudo
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_bullet_boundaries import system_bullet_boundaries
from src.ecs.systems.s_collision_bullet_enemy import system_collision_bullet_enemy
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_explosion_kill import system_explosion_kill
from src.ecs.systems.s_hunter_state import system_hunter_state
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_player_boundaries import system_player_boundaries
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_shield import system_shield
from src.ecs.systems.s_shield_hud import system_shield_hud
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_shield import CShield
from src.engine.service_locator import ServiceLocator

class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode(
            (self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]),
            0)
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_cfg["framerate"]
        self.delta_time = 0
        self.bg_color = pygame.Color(self.window_cfg["bg_color"]["r"],
                                     self.window_cfg["bg_color"]["g"],
                                     self.window_cfg["bg_color"]["b"])

        self.ecs_world = esper.World()
        self.is_paused = False
        self._pause_text_entity = None

    def _load_config_files(self):
        self.window_cfg = ServiceLocator.configs_service.get("assets/cfg/window.json")
        self.enemies_cfg = ServiceLocator.configs_service.get("assets/cfg/enemies.json")
        self.level_01_cfg = ServiceLocator.configs_service.get("assets/cfg/level_01.json")
        self.player_cfg = ServiceLocator.configs_service.get("assets/cfg/player.json")
        self.bullet_cfg = ServiceLocator.configs_service.get("assets/cfg/bullet.json")
        self.explosion_cfg = ServiceLocator.configs_service.get("assets/cfg/explosion.json")
        self.interface_cfg = ServiceLocator.configs_service.get("assets/cfg/interface.json")
        self.shield_cfg = ServiceLocator.configs_service.get("assets/cfg/shield.json")

    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)
        self._clean()

    def _create(self):
        self._player_entity = crear_cuadrado_jugador(self.ecs_world, self.player_cfg, self.level_01_cfg["player_spawn"])
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)

        agregar_escudo_jugador(self.ecs_world, self._player_entity, self.shield_cfg)

        crear_spawner_enemigos(self.ecs_world, self.level_01_cfg)
        crear_input_jugador(self.ecs_world)

        crear_texto(self.ecs_world, self.interface_cfg["title"]["text"],
                    self.interface_cfg["title"], self.interface_cfg, self.screen.get_rect())
        crear_texto(self.ecs_world, self.interface_cfg["instructions"]["text"],
                    self.interface_cfg["instructions"], self.interface_cfg, self.screen.get_rect())
        crear_hud_escudo(self.ecs_world, self.interface_cfg, self.screen.get_rect())

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        if self.is_paused:
            self.ecs_world._clear_dead_entities()
            return
        system_enemy_spawner(self.ecs_world, self.enemies_cfg, self.delta_time)
        system_movement(self.ecs_world, self.delta_time)

        system_player_state(self.ecs_world)
        system_hunter_state(self.ecs_world, self._player_entity, self.delta_time)

        system_player_boundaries(self.ecs_world, self.screen)
        system_screen_bounce(self.ecs_world, self.screen)
        system_bullet_boundaries(self.ecs_world, self.screen)
        system_shield(self.ecs_world, self._player_entity, self.shield_cfg,
                      self.explosion_cfg, self.delta_time)
        system_collision_player_enemy(self.ecs_world, self._player_entity, self.level_01_cfg,
                                      self.explosion_cfg)
        system_collision_bullet_enemy(self.ecs_world, self.explosion_cfg)

        system_animation(self.ecs_world, self.delta_time)
        system_explosion_kill(self.ecs_world)
        system_shield_hud(self.ecs_world, self._player_entity, self.interface_cfg)
        self.ecs_world._clear_dead_entities()

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input:CInputCommand):
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
        if c_input.name == "PAUSE" and c_input.phase == CommandPhase.START:
            self._toggle_pause()
        if c_input.name == "PLAYER_SHIELD" and not self.is_paused:
            if c_input.phase == CommandPhase.START:
                c_shield = self.ecs_world.try_component(self._player_entity, CShield)
                if c_shield is not None:
                    c_shield.requested = True
        if c_input.name == "PLAYER_FIRE" and not self.is_paused:
            if c_input.phase == CommandPhase.START:
                bullets = self.ecs_world.get_component(CTagBullet)
                if len(bullets) < self.level_01_cfg["player_spawn"]["max_bullets"]:
                    crear_bala(self.ecs_world,
                               self._player_c_t.pos,
                               pygame.Vector2(self._player_c_s.area.size),
                               pygame.Vector2(pygame.mouse.get_pos()),
                               self.bullet_cfg)

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self._pause_text_entity = crear_texto(self.ecs_world,
                                                  self.interface_cfg["paused"]["text"],
                                                  self.interface_cfg["paused"],
                                                  self.interface_cfg,
                                                  self.screen.get_rect())
        else:
            self.ecs_world.delete_entity(self._pause_text_entity)
            self._pause_text_entity = None
