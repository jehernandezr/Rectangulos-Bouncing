import esper
import pygame

from src.create.prefab_creator import crear_explosion
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy

def system_collision_bullet_enemy(world:esper.World, explosion_cfg:dict):
    bullets = world.get_components(CSurface, CTransform, CTagBullet)
    enemies = world.get_components(CSurface, CTransform, CTagEnemy)
    destroyed = set()

    for bullet_entity, (b_s, b_t, _) in bullets:
        bullet_rect = b_s.area.copy()
        bullet_rect.topleft = b_t.pos
        for enemy_entity, (e_s, e_t, _) in enemies:
            if enemy_entity in destroyed:
                continue
            ene_rect = CSurface.get_area_relative(e_s.area, e_t.pos)
            if bullet_rect.colliderect(ene_rect):
                world.delete_entity(bullet_entity)
                world.delete_entity(enemy_entity)
                destroyed.add(enemy_entity)
                crear_explosion(world, pygame.Vector2(ene_rect.center), explosion_cfg)
                break
