import pygame

class CAnchor:
    def __init__(self, anchor:str, point:pygame.Vector2) -> None:
        self.anchor = anchor
        self.point = point
