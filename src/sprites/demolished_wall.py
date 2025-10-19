import pygame

from settings import Settings
from src.sprites.removable_wall import RemovableWall


class DemolishedWall(RemovableWall):
    def __init__(self, image, position, groups, obstacle_map):
        super().__init__(image, position, groups, obstacle_map)

    def kill(self):
        super().kill()

        # Raise event to show vanishing point
        pygame.event.post(pygame.event.Event(Settings.ADD_VANISHING_POINT_EVENT, {"position": self.rect.topleft}))
