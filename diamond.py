import pygame
import settings


class Diamond(pygame.sprite.Sprite):
    def __init__(self, position, groups):
        super().__init__(groups)
        image = pygame.image.load('img/tile_0101.png').convert_alpha()
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(-35, -35)
