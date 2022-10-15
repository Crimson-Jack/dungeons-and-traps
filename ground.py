import pygame
import settings


class Ground(pygame.sprite.Sprite):
    def __init__(self, image, position, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)