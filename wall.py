import pygame
from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        image = pygame.image.load('img/tile_0014.png').convert_alpha()
        self.image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -10)