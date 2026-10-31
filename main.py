#!/usr/bin/python3
"""Función Main"""

import asyncio
import pygame
from src.engine.game_engine import GameEngine

if __name__ == "__main__":
    engine = GameEngine()
    asyncio.run(engine.run())
