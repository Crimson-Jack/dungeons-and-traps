import pygame
import settings
import game_helper


class Wall(pygame.sprite.Sprite):
    def __init__(self, image, position, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(0),
                                         int(game_helper.multiply_by_tile_size_ratio(-40)))
