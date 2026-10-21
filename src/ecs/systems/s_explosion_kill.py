import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_explosion import CTagExplosion

def system_explosion_kill(world:esper.World):
    components = world.get_component(CTagExplosion)
    for explosion_entity, _ in components:
        c_a = world.try_component(explosion_entity, CAnimation)
        if c_a is None or c_a.completed:
            world.delete_entity(explosion_entity)
