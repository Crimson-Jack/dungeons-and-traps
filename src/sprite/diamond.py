import pygame
import settings
import game_helper
from src.tile_details.diamond_tile_details import DiamondTileDetails
from src.sprite.item_to_collect import ItemToCollect


class Diamond(ItemToCollect):
    def __init__(self, image, position, groups, game_state, details: DiamondTileDetails):
        super().__init__(groups, game_state)

        # Sprite
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.base_size_image = pygame.transform.scale(image, (game_helper.BASE_TILE_SIZE, game_helper.BASE_TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(-35),
                                         game_helper.multiply_by_tile_size_ratio(-35))

        self.score = details.score

    def collect(self):
        self.game_state.collect_diamond(self)
        super().kill()
