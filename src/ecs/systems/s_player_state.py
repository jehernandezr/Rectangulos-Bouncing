import esper

from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_animation import CAnimation
from src.engine.service_locator import ServiceLocator

def system_player_state(world:esper.World):
    components = world.get_components(CVelocity, CAnimation, CPlayerState)
    for _, (c_v, c_a, c_pst) in components:
        if c_pst.state == PlayerState.IDLE:
            _do_idle_state(c_v, c_a, c_pst)
        elif c_pst.state == PlayerState.MOVE:
            _do_move_state(c_v, c_a, c_pst)

def _do_idle_state(c_v:CVelocity, c_a:CAnimation, c_pst:CPlayerState):
    _set_animation(c_a, "IDLE")
    if c_v.vel.magnitude_squared() > 0:
        if c_pst.sound_move is not None:
            ServiceLocator.sounds_service.play(c_pst.sound_move)
        c_pst.state = PlayerState.MOVE

def _do_move_state(c_v:CVelocity, c_a:CAnimation, c_pst:CPlayerState):
    _set_animation(c_a, "MOVE")
    if c_v.vel.magnitude_squared() <= 0:
        c_pst.state = PlayerState.IDLE

def _set_animation(c_a:CAnimation, name:str):
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
