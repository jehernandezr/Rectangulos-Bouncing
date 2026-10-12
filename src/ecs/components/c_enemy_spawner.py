import pygame

class SpawnEventData:
    def __init__(self, event_data:dict) -> None:
        self.time:float = event_data["time"]
        self.enemy_type:str = event_data["enemy_type"]
        self.position = pygame.Vector2(event_data["position"]["x"],
                                       event_data["position"]["y"])
        self.triggered = False

class CEnemySpawner:
    def __init__(self, level_data:dict) -> None:
        self.current_time:float = 0
        self.spawn_event_data:list[SpawnEventData] = []
        for event_data in level_data["enemy_spawn_events"]:
            self.spawn_event_data.append(SpawnEventData(event_data))
