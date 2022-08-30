import pygame
import settings


class GameState:
    def __init__(self):
        self.diamonds = 0

    def add_diamond(self):
        self.diamonds += 1
        pygame.event.post(pygame.event.Event(settings.ADD_DIAMOND_EVENT))