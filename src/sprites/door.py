import pygame

from settings import Settings
from src.sprites.removable_wall import RemovableWall
from src.tile_details.key_and_door_tile_details import KeyAndDoorTileDetails


class Door(RemovableWall):
    def __init__(self, image, position, groups, details: KeyAndDoorTileDetails, obstacle_map):
        super().__init__(image, position, groups, obstacle_map)
        self.key_name = details.key_name

    def kill(self):
        super().kill()

        # Raise event to refresh obstacle map
        pygame.event.post(pygame.event.Event(Settings.REFRESH_OBSTACLE_MAP_EVENT))
