import pygame
import settings
import game_helper
from item_to_collect import ItemToCollect


class Spell(ItemToCollect):
    def __init__(self, image, position, groups, game_state):
        super().__init__(groups, game_state)

        # Sprite
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(-10),
                                         game_helper.multiply_by_tile_size_ratio(-10))
