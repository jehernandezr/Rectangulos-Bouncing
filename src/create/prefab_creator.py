import random
import esper
import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity

def crear_cuadrado(ecs_world:esper.World, size:pygame.Vector2,
                   pos:pygame.Vector2, vel:pygame.Vector2,
                   col:pygame.Color):
    cuad_entity = ecs_world.create_entity()
    ecs_world.add_component(cuad_entity,
                            CSurface(size, col))
    ecs_world.add_component(cuad_entity,
                            CTransform(pos))
    ecs_world.add_component(cuad_entity,
                            CVelocity(vel))

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
    crear_cuadrado(ecs_world, size, pos.copy(), vel, col)

def crear_cuadrado_jugador(ecs_world:esper.World, player_info:dict,
                           player_lvl_info:dict):
    size = pygame.Vector2(player_info["size"]["x"],
                          player_info["size"]["y"])
    col = pygame.Color(player_info["color"]["r"],
                       player_info["color"]["g"],
                       player_info["color"]["b"])
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - (size.x / 2),
                         player_lvl_info["position"]["y"] - (size.y / 2))
    vel = pygame.Vector2(0, 0)
    crear_cuadrado(ecs_world, size, pos, vel, col)

def crear_spawner_enemigos(ecs_world:esper.World, level_data:dict):
    spawner_entity = ecs_world.create_entity()
    ecs_world.add_component(spawner_entity,
                            CEnemySpawner(level_data))
