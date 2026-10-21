import random
import esper
import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer

def crear_cuadrado(ecs_world:esper.World, size:pygame.Vector2,
                   pos:pygame.Vector2, vel:pygame.Vector2,
                   col:pygame.Color) -> int:
    cuad_entity = ecs_world.create_entity()
    ecs_world.add_component(cuad_entity,
                            CSurface(size, col))
    ecs_world.add_component(cuad_entity,
                            CTransform(pos))
    ecs_world.add_component(cuad_entity,
                            CVelocity(vel))
    return cuad_entity

def crear_sprite(ecs_world:esper.World, pos:pygame.Vector2,
                 vel:pygame.Vector2, surface:pygame.Surface) -> int:
    sprite_entity = ecs_world.create_entity()
    ecs_world.add_component(sprite_entity,
                            CTransform(pos))
    ecs_world.add_component(sprite_entity,
                            CVelocity(vel))
    ecs_world.add_component(sprite_entity,
                            CSurface.from_surface(surface))
    return sprite_entity

def crear_cuadrado_enemigo(ecs_world:esper.World, pos:pygame.Vector2,
                           enemy_info:dict):
    enemy_surface = pygame.image.load(enemy_info["image"]).convert_alpha()
    vel_mag = random.uniform(enemy_info["velocity_min"],
                             enemy_info["velocity_max"])
    vel = pygame.Vector2(vel_mag, 0).rotate(random.uniform(0, 360))
    enemy_entity = crear_sprite(ecs_world, pos.copy(), vel, enemy_surface)
    ecs_world.add_component(enemy_entity, CTagEnemy())

def crear_cuadrado_jugador(ecs_world:esper.World, player_info:dict,
                           player_lvl_info:dict) -> int:
    player_sprite = pygame.image.load(player_info["image"]).convert_alpha()
    size = player_sprite.get_size()
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - (size[0] / 2),
                         player_lvl_info["position"]["y"] - (size[1] / 2))
    vel = pygame.Vector2(0, 0)
    player_entity = crear_sprite(ecs_world, pos, vel, player_sprite)
    ecs_world.add_component(player_entity, CTagPlayer())
    return player_entity

def crear_bala(ecs_world:esper.World, player_pos:pygame.Vector2,
               player_size:pygame.Vector2, mouse_pos:pygame.Vector2,
               bullet_info:dict):
    bullet_surface = pygame.image.load(bullet_info["image"])
    size = pygame.Vector2(bullet_surface.get_size())
    player_center = player_pos + (player_size / 2)
    direction = mouse_pos - player_center
    if direction.length() == 0:
        return
    vel = direction.normalize() * bullet_info["velocity"]
    pos = player_center - (size / 2)
    bullet_entity = crear_sprite(ecs_world, pos, vel, bullet_surface)
    ecs_world.add_component(bullet_entity, CTagBullet())

def crear_spawner_enemigos(ecs_world:esper.World, level_data:dict):
    spawner_entity = ecs_world.create_entity()
    ecs_world.add_component(spawner_entity,
                            CEnemySpawner(level_data))

def crear_input_jugador(ecs_world:esper.World):
    input_left = ecs_world.create_entity()
    input_right = ecs_world.create_entity()
    input_up = ecs_world.create_entity()
    input_down = ecs_world.create_entity()
    input_fire = ecs_world.create_entity()

    ecs_world.add_component(input_left,
                            CInputCommand("PLAYER_LEFT", pygame.K_LEFT))
    ecs_world.add_component(input_right,
                            CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT))
    ecs_world.add_component(input_up,
                            CInputCommand("PLAYER_UP", pygame.K_UP))
    ecs_world.add_component(input_down,
                            CInputCommand("PLAYER_DOWN", pygame.K_DOWN))
    ecs_world.add_component(input_fire,
                            CInputCommand("PLAYER_FIRE", pygame.BUTTON_LEFT))
