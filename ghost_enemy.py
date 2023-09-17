import pygame
import game_helper
import settings
from obstacle_map_refresh_sprite import ObstacleMapRefreshSprite


class GhostEnemy(pygame.sprite.Sprite, ObstacleMapRefreshSprite):
    def __init__(self, frames, position, groups, speed, obstacle_map):
        super().__init__(groups)

        # Sprite animation variables
        self.sprites = []
        self.costume_switching_thresholds = []
        # Split frames into sprites and durations
        for frame in frames:
            self.sprites.append(pygame.transform.scale(frame[0], (settings.TILE_SIZE, settings.TILE_SIZE)))
            self.costume_switching_thresholds.append(game_helper.calculate_frames(frame[1]))
        self.number_of_sprites = len(self.sprites)
        self.costume_step_counter = 0
        self.costume_index = 0

        # Image
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Movement variables
        self.speed = speed
        self.default_movement_vector = pygame.math.Vector2((1, 0))
        self.movement_vector = pygame.math.Vector2(self.default_movement_vector)
        self.obstacle_map = obstacle_map

        # Set positions on map
        self.current_position_on_map = [
            (self.rect.right // settings.TILE_SIZE) - 1,
            (self.rect.bottom // settings.TILE_SIZE) - 1
        ]
        self.new_position_on_map = list(self.current_position_on_map)

        # Set is_moving flag
        self.is_moving = self.check_can_move((self.current_position_on_map[0], self.current_position_on_map[1]))
        # Set movement vector
        if self.is_moving:
            self.set_movement_vector()

        # Real position is required to store the real distance, which is then cast to integer
        self.real_x_position = float(self.hit_box.x)
        self.real_y_position = float(self.hit_box.y)

    def __del__(self):
        # TODO: Implement animation
        pass

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

            self.set_movement_vector()

        # Increase costume step counter
        self.costume_step_counter += 1

    def set_movement_vector(self):
        # Start position is current position
        start_position = (self.current_position_on_map[0], self.current_position_on_map[1])
        self.movement_vector = self.get_wall_follower_movement_vector(start_position, self.movement_vector)

    def check_can_move(self, position):
        # If all neighbours are obstacles - stop the movement
        tile_top = self.obstacle_map[position[1] - 1][position[0]]
        tile_bottom = self.obstacle_map[position[1] + 1][position[0]]
        tile_left = self.obstacle_map[position[1]][position[0] - 1]
        tile_right = self.obstacle_map[position[1]][position[0] + 1]
        if tile_top and tile_bottom and tile_left and tile_right:
            return False
        else:
            return True

    def get_wall_follower_movement_vector(self, position, movement_vector):
        # Result vector
        result_vector = None
        is_end_of_movement = False

        while not is_end_of_movement:
            next_position = [int(position[0] + movement_vector.x), int(position[1] + movement_vector.y)]

            # If Right
            if movement_vector == pygame.math.Vector2(1, 0):
                current_position_top = [next_position[0] - 1, next_position[1] - 1]
                previous_position_top = [next_position[0] - 2, next_position[1] - 1]
            # If Up
            elif movement_vector == pygame.math.Vector2(0, -1):
                current_position_top = [next_position[0] - 1, next_position[1] + 1]
                previous_position_top = [next_position[0] - 1, next_position[1] + 2]
            # Elif left
            elif movement_vector == pygame.math.Vector2(-1, 0):
                current_position_top = [next_position[0] + 1, next_position[1] + 1]
                previous_position_top = [next_position[0] + 2, next_position[1] + 1]
            # Elif down
            elif movement_vector == pygame.math.Vector2(0, 1):
                current_position_top = [next_position[0] + 1, next_position[1] - 1]
                previous_position_top = [next_position[0] + 1, next_position[1] - 2]

            if self.obstacle_map[previous_position_top[1]][previous_position_top[0]] \
                    and not self.obstacle_map[current_position_top[1]][current_position_top[0]]:
                # [ppt]   [   ]
                # [   ]   [ x ]
                vector = pygame.math.Vector2(movement_vector)
                movement_vector = pygame.math.Vector2.rotate(vector, -90)
                result_vector = movement_vector
                is_end_of_movement = True
            elif self.obstacle_map[next_position[1]][next_position[0]]:
                # [ x ]   [np ]
                # Turn 90 degree
                vector = pygame.math.Vector2(movement_vector)
                movement_vector = pygame.math.Vector2.rotate(vector, 90)
                result_vector = movement_vector
            elif not self.obstacle_map[next_position[1]][next_position[0]]:
                # [ x ]   [   ]
                result_vector = movement_vector
                is_end_of_movement = True

        return result_vector

    def update(self):
        if self.number_of_sprites > 1:
            self.change_costume()
        if self.is_moving:
            self.move()

    def refresh_obstacle_map(self):
        # Get the last moving state
        previous_moving_state = self.is_moving

        # Start position is current position
        start_position = (self.current_position_on_map[0], self.current_position_on_map[1])
        # Check current moving state
        self.is_moving = self.check_can_move(start_position)

        if not previous_moving_state and self.is_moving:
            # Start moving
            self.movement_vector = self.get_wall_follower_movement_vector(start_position, self.default_movement_vector)

    def change_costume(self):
        # Change costume only if threshold exceeded
        if self.costume_step_counter > self.costume_switching_thresholds[self.costume_index]:

            # Reset counter and increase costume index
            self.costume_step_counter = 0
            self.costume_index += 1

            # If it's the last costume - start from the second costume (index = 1)
            if self.costume_index >= self.number_of_sprites:
                self.costume_index = 0

            # Set new image
            self.image = self.sprites[self.costume_index]
