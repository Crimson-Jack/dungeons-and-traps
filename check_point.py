import pygame
import settings
import game_helper
from item_to_collect import ItemToCollect


class CheckPoint(ItemToCollect):
    def __init__(self, image, position, groups, game_state):
        super().__init__(groups, game_state)

        # Sprite
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(-20),
                                         game_helper.multiply_by_tile_size_ratio(-20))

    def collect(self):
        self.game_state.collect_check_point(self.rect.topleft)
        super().kill()
