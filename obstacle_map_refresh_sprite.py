import pygame


class ObstacleMapRefreshSprite(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

    def refresh_obstacle_map(self, obstacle_map, start_position):
        pass