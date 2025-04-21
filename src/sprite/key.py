import pygame
import settings
from src.game_helper import GameHelper
from src.tile_details.key_and_door_tile_details import KeyAndDoorTileDetails
from src.sprite.item_to_collect import ItemToCollect


class Key(ItemToCollect):
    def __init__(self, image, position, groups, game_state, details: KeyAndDoorTileDetails):
        super().__init__(groups, game_state)

        # Sprite
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.base_size_image = pygame.transform.scale(image, (GameHelper.BASE_TILE_SIZE, GameHelper.BASE_TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(GameHelper.multiply_by_tile_size_ratio(-35),
                                         GameHelper.multiply_by_tile_size_ratio(-35))
        self.key_name = details.key_name
        self.score = details.score

    def collect(self):
        self.game_state.collect_key(self)
        super().kill()
