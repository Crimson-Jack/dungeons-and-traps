import pygame
import settings
import game_helper
from obstacle_map_refresh_sprite import ObstacleMapRefreshSprite


class GhostEnemy(ObstacleMapRefreshSprite):
    def __init__(self, image, position, groups, speed, obstacle_map, start_position):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        self.is_moving = True
        self.movement_vector = pygame.math.Vector2((1, 0))

        # Left hand wall follower path
        self.wall_follower_path = []
        self.refresh_obstacle_map(obstacle_map, start_position)
        self.movement_index = -1

        # Create movement variables
        self.speed = speed
        self.current_position_on_map = [
            (self.rect.right // settings.TILE_SIZE) - 1,
            (self.rect.bottom // settings.TILE_SIZE) - 1
        ]
        self.new_position_on_map = list(self.current_position_on_map)
        self.set_new_direction()

        # Real position is required to store the real distance, which is then cast to integer
        self.real_x_position = float(self.hit_box.x)
        self.real_y_position = float(self.hit_box.y)

    def move(self):
        # Calculate real y position
        self.real_x_position += float(self.movement_vector.x * self.speed)
        self.real_y_position += float(self.movement_vector.y * self.speed)

        # Cast real position to integer
        self.hit_box.x = int(self.real_x_position)
        self.hit_box.y = int(self.real_y_position)

        # Set the movement offset
        self.rect.center = self.hit_box.center

        # Adjust offset
        # This is necessary for offsets that are not TILE_SIZE dividers
        x_remainder = self.rect.right % settings.TILE_SIZE
        y_remainder = self.rect.bottom % settings.TILE_SIZE

        if x_remainder < self.speed:
            self.hit_box.x = self.hit_box.x - x_remainder
            self.rect.center = self.hit_box.center

        if y_remainder < self.speed:
            self.hit_box.y = self.hit_box.y - y_remainder
            self.rect.center = self.hit_box.center

        # Recognize the moment when ghost moves to a new area
        # In this case TILE_SIZE is a divisor of "right" or "bottom"
        if self.rect.right % settings.TILE_SIZE == 0:
            self.new_position_on_map[0] = (self.rect.right // settings.TILE_SIZE) - 1

        if self.rect.bottom % settings.TILE_SIZE == 0:
            self.new_position_on_map[1] = (self.rect.bottom // settings.TILE_SIZE) - 1

        # If position was changed, change position and determine new direction
        if self.current_position_on_map != self.new_position_on_map:
            # Change current position (x or y or both)
            if self.current_position_on_map[0] != self.new_position_on_map[0]:
                self.current_position_on_map[0] = self.new_position_on_map[0]
            if self.current_position_on_map[1] != self.new_position_on_map[1]:
                self.current_position_on_map[1] = self.new_position_on_map[1]
            print(f'pos on the map: {self.current_position_on_map[0]} {self.current_position_on_map[1]}')
            self.set_new_direction()

    def set_new_direction(self):
        # Determine new direction
        # Get previous position from the path
        previous_position = self.wall_follower_path[self.movement_index]

        # Increase movement index in the path
        if self.movement_index < len(self.wall_follower_path) - 1:
            # Move to the next index
            self.movement_index += 1
        else:
            # Reset index - the loop is closed - start from the beginning
            self.movement_index = 0

        # Get next position from the path
        next_position = self.wall_follower_path[self.movement_index]

        # Calculate new movement vector based on previous and next position
        self.movement_vector.x = next_position[0] - previous_position[0]
        self.movement_vector.y = next_position[1] - previous_position[1]

    def update(self):
        if self.is_moving:
            self.move()

    def refresh_obstacle_map(self, obstacle_map, start_position=None):
        # Start position is current position
        if start_position is None:
            start_position = (self.current_position_on_map[0], self.current_position_on_map[1])

        # Generate a new path
        self.wall_follower_path = game_helper.get_wall_follower_path(obstacle_map, start_position, self.movement_vector)
        self.movement_index = 0

        # Can move only when is more than 1 tiles in path
        if len(self.wall_follower_path) > 1:
            self.is_moving = True
            print('Ghost starts moving')
        else:
            self.is_moving = False
            # TODO: Reset movement vector, based on the opening - how to do this?
            print('Ghost stops moving')

        # TODO: Remove after tests
        settings.wall_follower_path = self.wall_follower_path

