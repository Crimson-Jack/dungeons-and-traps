import pygame
import settings
from src.game_helper import GameHelper
from src.tile_details.key_and_door_tile_details import KeyAndDoorTileDetails


class Door(pygame.sprite.Sprite):
    def __init__(self, image, position, groups, details: KeyAndDoorTileDetails, obstacle_map):
        super().__init__(*groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(int(GameHelper.multiply_by_tile_size_ratio(0)),
                                         int(GameHelper.multiply_by_tile_size_ratio(-40)))
        self.key_name = details.key_name
        self.obstacle_map = obstacle_map

    def kill(self):
        super().kill()

        # Reset obstacle map position
        x_tile_position, y_tile_position = self.rect[0] // settings.TILE_SIZE, self.rect[1] // settings.TILE_SIZE
        self.obstacle_map[y_tile_position][x_tile_position] = 0

        # Raise event to refresh obstacle map
        pygame.event.post(pygame.event.Event(settings.REFRESH_OBSTACLE_MAP_EVENT))
