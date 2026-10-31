from enum import Enum

class CPlayerState:
    def __init__(self, player_info:dict) -> None:
        self.state = PlayerState.IDLE
        self.sound_move = player_info.get("sound_move")
        self.sound_hit = player_info.get("sound_hit")

class PlayerState(Enum):
    IDLE = 0
    MOVE = 1
