import esper
import pygame
from src.create.prefab_creator import crear_explosion
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_shield import CShield
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.engine.service_locator import ServiceLocator

def system_collision_player_enemy(world:esper.World, player_entity:int, level_cfg:dict,
                                  explosion_cfg:dict):
    components = world.get_components(CSurface, CTransform, CTagEnemy)
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    pl_rect = CSurface.get_area_relative(pl_s.area, pl_t.pos)

    pl_shield = world.try_component(player_entity, CShield)
    shielded = pl_shield is not None and pl_shield.is_active()

    for enemy_entity, (c_s, c_t, _) in components:
        ene_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        if ene_rect.colliderect(pl_rect):
            world.delete_entity(enemy_entity)
            crear_explosion(world, pygame.Vector2(ene_rect.center), explosion_cfg)
            if shielded:
                continue
            pl_st = world.try_component(player_entity, CPlayerState)
            if pl_st is not None and pl_st.sound_hit is not None:
                ServiceLocator.sounds_service.play(pl_st.sound_hit)
            pl_t.pos.x = level_cfg["player_spawn"]["position"]["x"] - pl_s.area.w / 2
            pl_t.pos.y = level_cfg["player_spawn"]["position"]["y"] - pl_s.area.h / 2
