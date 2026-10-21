import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_hunter_state import CHunterState, HunterState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity

def system_hunter_state(world:esper.World, player_entity:int, delta_time:float):
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    pl_center = pygame.Vector2(CSurface.get_area_relative(pl_s.area, pl_t.pos).center)

    components = world.get_components(CTransform, CVelocity, CSurface, CHunterState)
    for hunter_entity, (c_t, c_v, c_s, c_hst) in components:
        c_a = world.try_component(hunter_entity, CAnimation)
        hunter_center = pygame.Vector2(CSurface.get_area_relative(c_s.area, c_t.pos).center)
        if c_hst.state == HunterState.IDLE:
            _do_idle_state(c_v, c_a, c_hst, hunter_center, pl_center)
        elif c_hst.state == HunterState.CHASE:
            _do_chase_state(c_t, c_v, c_a, c_hst, hunter_center, pl_center)
        elif c_hst.state == HunterState.RETURN:
            _do_return_state(c_t, c_v, c_a, c_hst, delta_time)

def _do_idle_state(c_v:CVelocity, c_a:CAnimation, c_hst:CHunterState,
                   hunter_center:pygame.Vector2, pl_center:pygame.Vector2):
    _set_animation(c_a, "IDLE")
    c_v.vel.xy = (0, 0)
    if hunter_center.distance_to(pl_center) <= c_hst.distance_start_chase:
        c_hst.state = HunterState.CHASE

def _do_chase_state(c_t:CTransform, c_v:CVelocity, c_a:CAnimation, c_hst:CHunterState,
                    hunter_center:pygame.Vector2, pl_center:pygame.Vector2):
    _set_animation(c_a, "MOVE")
    direction = pl_center - hunter_center
    if direction.length_squared() > 0:
        c_v.vel = direction.normalize() * c_hst.velocity_chase
    else:
        c_v.vel.xy = (0, 0)
    if c_t.pos.distance_to(c_hst.origin) >= c_hst.distance_start_return:
        c_hst.state = HunterState.RETURN

def _do_return_state(c_t:CTransform, c_v:CVelocity, c_a:CAnimation, c_hst:CHunterState,
                     delta_time:float):
    _set_animation(c_a, "MOVE")
    direction = c_hst.origin - c_t.pos
    if direction.length() <= c_hst.velocity_return * delta_time:
        c_t.pos.xy = c_hst.origin.xy
        c_v.vel.xy = (0, 0)
        c_hst.state = HunterState.IDLE
    else:
        c_v.vel = direction.normalize() * c_hst.velocity_return

def _set_animation(c_a:CAnimation, name:str):
    if c_a is None:
        return
    for num_anim, anim_data in enumerate(c_a.animations_list):
        if anim_data.name == name:
            break
    else:
        return
    if c_a.curr_anim == num_anim:
        return
    c_a.curr_anim = num_anim
    c_a.curr_anim_time = 0
    c_a.curr_frame = c_a.animations_list[c_a.curr_anim].start
