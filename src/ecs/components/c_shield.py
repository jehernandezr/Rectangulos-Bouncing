class CShield:
    def __init__(self, shield_info:dict) -> None:
        self.duration = shield_info["duration"]
        self.cooldown = shield_info["cooldown"]
        self.radius = shield_info["radius"]
        self.blink_time = shield_info["blink_time"]
        self.sound_ready = shield_info.get("sound_ready")
        self.time_active = 0.0
        self.time_cooldown = 0.0
        self.requested = False
        self.shield_entity = None

    def is_active(self) -> bool:
        return self.time_active > 0

    def is_ready(self) -> bool:
        return self.time_active <= 0 and self.time_cooldown <= 0
