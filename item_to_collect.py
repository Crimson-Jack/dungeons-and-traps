import pygame
import settings
import game_helper


class ItemToCollect(pygame.sprite.Sprite):
    def __init__(self, image, position, groups, game_state):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.base_size_image = pygame.transform.scale(image, (game_helper.BASE_TILE_SIZE, game_helper.BASE_TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.game_state = game_state

    def collect(self):
        pass
