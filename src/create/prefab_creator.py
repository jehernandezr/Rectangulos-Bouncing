import random
import esper
import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
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

def crear_cuadrado_enemigo(ecs_world:esper.World, pos:pygame.Vector2,
                           enemy_info:dict):
    size = pygame.Vector2(enemy_info["size"]["x"],
                          enemy_info["size"]["y"])
    col = pygame.Color(enemy_info["color"]["r"],
                       enemy_info["color"]["g"],
                       enemy_info["color"]["b"])
    vel_mag = random.uniform(enemy_info["velocity_min"],
                             enemy_info["velocity_max"])
    vel = pygame.Vector2(vel_mag, 0).rotate(random.uniform(0, 360))
    enemy_entity = crear_cuadrado(ecs_world, size, pos.copy(), vel, col)
    ecs_world.add_component(enemy_entity, CTagEnemy())

def crear_cuadrado_jugador(ecs_world:esper.World, player_info:dict,
                           player_lvl_info:dict) -> int:
    size = pygame.Vector2(player_info["size"]["x"],
                          player_info["size"]["y"])
    col = pygame.Color(player_info["color"]["r"],
                       player_info["color"]["g"],
                       player_info["color"]["b"])
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - (size.x / 2),
                         player_lvl_info["position"]["y"] - (size.y / 2))
    vel = pygame.Vector2(0, 0)
    player_entity = crear_cuadrado(ecs_world, size, pos, vel, col)
    ecs_world.add_component(player_entity, CTagPlayer())
    return player_entity

def crear_spawner_enemigos(ecs_world:esper.World, level_data:dict):
    spawner_entity = ecs_world.create_entity()
    ecs_world.add_component(spawner_entity,
                            CEnemySpawner(level_data))

def crear_input_jugador(ecs_world:esper.World):
    input_left = ecs_world.create_entity()
    input_right = ecs_world.create_entity()
    input_up = ecs_world.create_entity()
    input_down = ecs_world.create_entity()

    ecs_world.add_component(input_left,
                            CInputCommand("PLAYER_LEFT", pygame.K_LEFT))
    ecs_world.add_component(input_right,
                            CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT))
    ecs_world.add_component(input_up,
                            CInputCommand("PLAYER_UP", pygame.K_UP))
    ecs_world.add_component(input_down,
                            CInputCommand("PLAYER_DOWN", pygame.K_DOWN))
