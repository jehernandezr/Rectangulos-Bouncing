import esper
import pygame

from src.ecs.components.c_anchor import CAnchor
from src.ecs.components.c_shield import CShield
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_shield_bar import CTagShieldBar
from src.ecs.components.tags.c_tag_shield_text import CTagShieldText
from src.engine.service_locator import ServiceLocator

def system_shield_hud(world:esper.World, player_entity:int, interface_cfg:dict):
    c_sh = world.try_component(player_entity, CShield)
    if c_sh is None:
        return

    if c_sh.is_active():
        state = "active"
        fraction = c_sh.time_active / c_sh.duration
        text = f'{interface_cfg["shield_status"]["text_active"]} {c_sh.time_active:.1f}'
    elif c_sh.time_cooldown > 0:
        state = "charging"
        fraction = 1 - c_sh.time_cooldown / c_sh.cooldown
        text = f'{interface_cfg["shield_status"]["text_charging"]} {c_sh.time_cooldown:.1f}'
    else:
        state = "ready"
        fraction = 1.0
        text = interface_cfg["shield_status"]["text_ready"]

    _update_text(world, interface_cfg, state, text)
    _update_bar(world, interface_cfg["shield_bar"], state, fraction)

def _color(info:dict, state:str) -> pygame.Color:
    color = info["color_" + state]
    return pygame.Color(color["r"], color["g"], color["b"])

def _update_text(world:esper.World, interface_cfg:dict, state:str, text:str):
    status_info = interface_cfg["shield_status"]
    font_path = status_info.get("font", interface_cfg["font"])
    font = ServiceLocator.fonts_service.get(font_path, status_info["size"])
    components = world.get_components(CTransform, CSurface, CAnchor, CTagShieldText)
    for _, (c_t, c_s, c_anchor, _) in components:
        new_surface = CSurface.from_text(text, font, _color(status_info, state))
        c_s.surf = new_surface.surf
        c_s.area = new_surface.area
        text_rect = c_s.area.copy()
        setattr(text_rect, c_anchor.anchor, c_anchor.point)
        c_t.pos.xy = text_rect.topleft

def _update_bar(world:esper.World, bar_info:dict, state:str, fraction:float):
    components = world.get_components(CSurface, CTagShieldBar)
    for _, (c_s, _) in components:
        c_s.surf.fill(_color(bar_info, "back"))
        fill_rect = c_s.surf.get_rect()
        fill_rect.w = round(fill_rect.w * max(0.0, min(1.0, fraction)))
        c_s.surf.fill(_color(bar_info, state), fill_rect)
