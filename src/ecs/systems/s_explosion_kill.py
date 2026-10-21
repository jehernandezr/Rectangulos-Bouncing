import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_explosion import CTagExplosion

def system_explosion_kill(world:esper.World):
    components = world.get_components(CAnimation, CTagExplosion)
    for explosion_entity, (c_a, _) in components:
        if c_a.completed:
            world.delete_entity(explosion_entity)
