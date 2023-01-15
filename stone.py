import pygame
import settings
from moving_obstacle import MovingObstacle
import game_helper


class Stone(MovingObstacle):
    def __init__(self, image, position, groups, obstacle_map):
        super().__init__(image, position, groups, obstacle_map)
        # Note: inflate rectangle in y should have the same value as obstacles (wall)
        self.hit_box = self.rect.inflate(game_helper.calculate_ratio(-10), game_helper.calculate_ratio(-40))
        
    def move_object(self, movement_direction):
        is_blocked = super().move_object(movement_direction)

        if not is_blocked:
            self.hit_box.center = self.rect.center

        return is_blocked
