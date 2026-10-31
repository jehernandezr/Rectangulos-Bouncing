import random
import esper
import pygame

from src.ecs.components.c_anchor import CAnchor
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_hunter_state import CHunterState
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_explosion import CTagExplosion
from src.ecs.components.tags.c_tag_hud import CTagHud
from src.ecs.components.tags.c_tag_hunter import CTagHunter
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.engine.service_locator import ServiceLocator

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

def crear_animacion(ecs_world:esper.World, entity:int, entity_info:dict):
    if "animations" not in entity_info:
        return
    c_s = ecs_world.component_for_entity(entity, CSurface)
    c_a = CAnimation(entity_info["animations"])
    c_a.curr_anim_time = c_a.animations_list[c_a.curr_anim].framerate
    c_s.area.w = c_s.surf.get_width() / c_a.number_frames
    c_s.area.x = c_s.area.w * c_a.curr_frame
    ecs_world.add_component(entity, c_a)

def tamano_cuadro(surface:pygame.Surface, entity_info:dict) -> pygame.Vector2:
    number_frames = 1
    if "animations" in entity_info:
        number_frames = entity_info["animations"]["number_frames"]
    return pygame.Vector2(surface.get_width() / number_frames,
                          surface.get_height())

def crear_cuadrado_enemigo(ecs_world:esper.World, pos:pygame.Vector2,
                           enemy_info:dict):
    enemy_surface = ServiceLocator.images_service.get(enemy_info["image"])
    vel_mag = random.uniform(enemy_info["velocity_min"],
                             enemy_info["velocity_max"])
    vel = pygame.Vector2(vel_mag, 0).rotate(random.uniform(0, 360))
    enemy_entity = crear_sprite(ecs_world, pos.copy(), vel, enemy_surface)
    crear_animacion(ecs_world, enemy_entity, enemy_info)
    ecs_world.add_component(enemy_entity, CTagEnemy())
    ServiceLocator.sounds_service.play(enemy_info["sound"])

def crear_cuadrado_hunter(ecs_world:esper.World, pos:pygame.Vector2,
                          hunter_info:dict):
    hunter_surface = ServiceLocator.images_service.get(hunter_info["image"])
    vel = pygame.Vector2(0, 0)
    hunter_entity = crear_sprite(ecs_world, pos.copy(), vel, hunter_surface)
    crear_animacion(ecs_world, hunter_entity, hunter_info)
    ecs_world.add_component(hunter_entity, CTagEnemy())
    ecs_world.add_component(hunter_entity, CTagHunter())
    ecs_world.add_component(hunter_entity,
                            CHunterState(pos, hunter_info))

def crear_explosion(ecs_world:esper.World, center:pygame.Vector2,
                    explosion_info:dict):
    explosion_surface = ServiceLocator.images_service.get(explosion_info["image"])
    size = tamano_cuadro(explosion_surface, explosion_info)
    pos = center - (size / 2)
    vel = pygame.Vector2(0, 0)
    explosion_entity = crear_sprite(ecs_world, pos, vel, explosion_surface)
    crear_animacion(ecs_world, explosion_entity, explosion_info)
    ecs_world.add_component(explosion_entity, CTagExplosion())
    ServiceLocator.sounds_service.play(explosion_info["sound"])

def crear_cuadrado_jugador(ecs_world:esper.World, player_info:dict,
                           player_lvl_info:dict) -> int:
    player_sprite = ServiceLocator.images_service.get(player_info["image"])
    size = tamano_cuadro(player_sprite, player_info)
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - (size.x / 2),
                         player_lvl_info["position"]["y"] - (size.y / 2))
    vel = pygame.Vector2(0, 0)
    player_entity = crear_sprite(ecs_world, pos, vel, player_sprite)
    ecs_world.add_component(player_entity, CTagPlayer())
    crear_animacion(ecs_world, player_entity, player_info)
    ecs_world.add_component(player_entity,
                            CPlayerState(player_info))
    return player_entity

def crear_bala(ecs_world:esper.World, player_pos:pygame.Vector2,
               player_size:pygame.Vector2, mouse_pos:pygame.Vector2,
               bullet_info:dict):
    bullet_surface = ServiceLocator.images_service.get(bullet_info["image"])
    size = tamano_cuadro(bullet_surface, bullet_info)
    player_center = player_pos + (player_size / 2)
    direction = mouse_pos - player_center
    if direction.length() == 0:
        return
    vel = direction.normalize() * bullet_info["velocity"]
    pos = player_center - (size / 2)
    bullet_entity = crear_sprite(ecs_world, pos, vel, bullet_surface)
    crear_animacion(ecs_world, bullet_entity, bullet_info)
    ecs_world.add_component(bullet_entity, CTagBullet())
    ServiceLocator.sounds_service.play(bullet_info["sound"])

def punto_en_pantalla(screen_rect:pygame.Rect, position_info:dict) -> pygame.Vector2:
    anchor_point = pygame.Vector2(getattr(screen_rect, position_info["anchor"]))
    return anchor_point + pygame.Vector2(position_info["offset"]["x"],
                                         position_info["offset"]["y"])

def crear_texto(ecs_world:esper.World, text:str, text_info:dict,
                interface_info:dict, screen_rect:pygame.Rect) -> int:
    font_path = text_info.get("font", interface_info["font"])
    font = ServiceLocator.fonts_service.get(font_path, text_info["size"])
    color = pygame.Color(text_info["color"]["r"],
                         text_info["color"]["g"],
                         text_info["color"]["b"])
    c_s = CSurface.from_text(text, font, color)
    c_anchor = CAnchor(text_info["position"]["anchor"],
                       punto_en_pantalla(screen_rect, text_info["position"]))
    text_rect = c_s.area.copy()
    setattr(text_rect, c_anchor.anchor, c_anchor.point)
    text_entity = ecs_world.create_entity()
    ecs_world.add_component(text_entity, CTransform(pygame.Vector2(text_rect.topleft)))
    ecs_world.add_component(text_entity, c_s)
    ecs_world.add_component(text_entity, c_anchor)
    ecs_world.add_component(text_entity, CTagHud())
    return text_entity

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
    input_pause = ecs_world.create_entity()

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
    ecs_world.add_component(input_pause,
                            CInputCommand("PAUSE", pygame.K_p))
