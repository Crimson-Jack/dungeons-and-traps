import pygame
from settings import *


class Diamond(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        image = pygame.image.load('img/tile_0101.png').convert_alpha()
        self.image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-35, -35)
