import pygame
import settings
import game_helper


class Powerup(pygame.sprite.Sprite):
    def __init__(self, image, position, groups, game_state):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.base_size_image = pygame.transform.scale(image, (game_helper.BASE_TILE_SIZE, game_helper.BASE_TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(-25),
                                         game_helper.multiply_by_tile_size_ratio(-25))
        self.game_state = game_state

    def activate(self):
        pass

