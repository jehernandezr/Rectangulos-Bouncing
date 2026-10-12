import esper

from src.create.prefab_creator import crear_cuadrado_enemigo
from src.ecs.components.c_enemy_spawner import CEnemySpawner

def system_enemy_spawner(world:esper.World, enemies_data:dict, delta_time:float):
    components = world.get_component(CEnemySpawner)

    c_spw:CEnemySpawner
    for entity, c_spw in components:
        c_spw.current_time += delta_time
        for spw_evt in c_spw.spawn_event_data:
            if not spw_evt.triggered and c_spw.current_time >= spw_evt.time:
                spw_evt.triggered = True
                crear_cuadrado_enemigo(world,
                                       spw_evt.position,
                                       enemies_data[spw_evt.enemy_type])
