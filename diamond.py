import pygame
import settings
import game_helper


class Diamond(pygame.sprite.Sprite):
    def __init__(self, image, position, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(game_helper.calculate_ratio(-35), game_helper.calculate_ratio(-35))
