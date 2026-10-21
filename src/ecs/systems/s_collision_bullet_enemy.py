import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy

def system_collision_bullet_enemy(world:esper.World):
    bullets = world.get_components(CSurface, CTransform, CTagBullet)
    enemies = world.get_components(CSurface, CTransform, CTagEnemy)

    for bullet_entity, (b_s, b_t, _) in bullets:
        bullet_rect = b_s.area.copy()
        bullet_rect.topleft = b_t.pos
        for enemy_entity, (e_s, e_t, _) in enemies:
            ene_rect = e_s.area.copy()
            ene_rect.topleft = e_t.pos
            if bullet_rect.colliderect(ene_rect):
                world.delete_entity(bullet_entity)
                world.delete_entity(enemy_entity)
                break
