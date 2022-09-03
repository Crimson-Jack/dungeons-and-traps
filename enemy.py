import pygame
import settings


class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

    def custom_draw(self):
        pass
