import esper
import pygame

from src.create.prefab_creator import crear_escudo, crear_explosion
from src.ecs.components.c_shield import CShield
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.engine.service_locator import ServiceLocator

def system_shield(world:esper.World, player_entity:int, shield_cfg:dict,
                  explosion_cfg:dict, delta_time:float):
    c_sh = world.try_component(player_entity, CShield)
    if c_sh is None:
        return
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    pl_center = pygame.Vector2(CSurface.get_area_relative(pl_s.area, pl_t.pos).center)

    if c_sh.requested:
        c_sh.requested = False
        if c_sh.is_ready():
            c_sh.time_active = c_sh.duration
            c_sh.shield_entity = crear_escudo(world, pl_center, shield_cfg)

    if c_sh.is_active():
        c_sh.time_active -= delta_time
        _follow_player(world, c_sh, pl_center)
        _destroy_near_enemies(world, c_sh, pl_center, explosion_cfg)
        if not c_sh.is_active():
            world.delete_entity(c_sh.shield_entity)
            c_sh.shield_entity = None
            c_sh.time_active = 0.0
            c_sh.time_cooldown = c_sh.cooldown
    elif c_sh.time_cooldown > 0:
        c_sh.time_cooldown -= delta_time
        if c_sh.time_cooldown <= 0:
            c_sh.time_cooldown = 0.0
            if c_sh.sound_ready is not None:
                ServiceLocator.sounds_service.play(c_sh.sound_ready)

def _follow_player(world:esper.World, c_sh:CShield, pl_center:pygame.Vector2):
    sh_t = world.component_for_entity(c_sh.shield_entity, CTransform)
    sh_s = world.component_for_entity(c_sh.shield_entity, CSurface)
    sh_t.pos.xy = pl_center - pygame.Vector2(sh_s.area.size) / 2
    if c_sh.time_active < c_sh.blink_time:
        visible = int(c_sh.time_active * 16) % 2 == 0
        sh_s.surf.set_alpha(255 if visible else 70)

def _destroy_near_enemies(world:esper.World, c_sh:CShield, pl_center:pygame.Vector2,
                          explosion_cfg:dict):
    components = world.get_components(CTransform, CSurface, CTagEnemy)
    for enemy_entity, (c_t, c_s, _) in components:
        ene_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        reach = c_sh.radius + max(ene_rect.w, ene_rect.h) / 2
        if pl_center.distance_to(ene_rect.center) <= reach:
            world.delete_entity(enemy_entity, immediate=True)
            crear_explosion(world, pygame.Vector2(ene_rect.center), explosion_cfg)
