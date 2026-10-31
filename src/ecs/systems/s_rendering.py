import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_hud import CTagHud

def system_rendering(world:esper.World, screen:pygame.Surface):
    components = world.get_components(CTransform, CSurface)

    c_t:CTransform
    c_s:CSurface
    hud = []
    for entity, (c_t, c_s) in components:
        if world.has_component(entity, CTagHud):
            hud.append((c_t, c_s))
            continue
        screen.blit(c_s.surf, c_t.pos, area=c_s.area)

    for c_t, c_s in hud:
        screen.blit(c_s.surf, c_t.pos, area=c_s.area)
