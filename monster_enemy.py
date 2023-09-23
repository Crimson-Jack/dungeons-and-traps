import pygame
import game_helper
import settings
from obstacle_map_refresh_sprite import ObstacleMapRefreshSprite
from enemy_with_brain import EnemyWithBrain
from breadth_first_search_helper import BreadthFirstSearchHelper


class MonsterEnemy(pygame.sprite.Sprite, EnemyWithBrain, ObstacleMapRefreshSprite):
    def __init__(self, image, position, groups, obstacle_map, game_state, moving_obstacle_sprites):
        super().__init__(groups)

        # Image
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Obstacle map
        self.obstacle_map = obstacle_map

        # Game state
        self.game_state = game_state

        # Movement variables
        self.speed = 10
        self.movement_vector = pygame.math.Vector2(0, 0)
        self.is_moving = False
        self.start_delay = 1
        self.start_delay_counter = self.start_delay

        # Set positions on map
        self.current_position_on_map = [
            (self.rect.right // settings.TILE_SIZE) - 1,
            (self.rect.bottom // settings.TILE_SIZE) - 1
        ]
        self.new_position_on_map = list(self.current_position_on_map)

        # Path variables
        self.all_tiles = []
        self.obstacles = []
        self.create_all_tiles_and_obstacles_lists()
        self.breadth_first_search_helper = BreadthFirstSearchHelper()
        self.path = None

        # Real position is required to store the real distance, which is then cast to integer
        self.real_x_position = float(self.hit_box.x)
        self.real_y_position = float(self.hit_box.y)

        # Moving obstacles
        self.moving_obstacle_sprites = moving_obstacle_sprites

    def create_all_tiles_and_obstacles_lists(self):
        for x in range(len(self.obstacle_map)):
            for y in range(len(self.obstacle_map[x])):
                self.all_tiles.append((y, x))
                if self.obstacle_map[x][y] > 0:
                    self.obstacles.append((y, x))

    def update(self):
        if self.is_moving:
            self.move()
        else:
            self.start_delay_counter -= 1
            if self.start_delay_counter < 0:
                # Reset counter
                self.start_delay_counter = self.start_delay
                # If the vector is found, the movement is on
                self.set_movement_vector()
                if self.movement_vector:
                    self.is_moving = True

    def move(self):
        # Calculate real y position
        self.real_x_position += float(self.movement_vector.x * self.speed)
        self.real_y_position += float(self.movement_vector.y * self.speed)

        if self.check_collision():
            # Collision with moving obstacle sprites was detected
            # Monster must be moved to the last valid position (using current map position)
            self.hit_box.x = self.current_position_on_map[0] * settings.TILE_SIZE
            self.hit_box.y = self.current_position_on_map[1] * settings.TILE_SIZE

            # Adjust position after collision
            self.real_x_position = float(self.hit_box.x)
            self.real_y_position = float(self.hit_box.y)

            # Stop moving and early return
            self.is_moving = False
            return

        # Cast real position to integer
        self.hit_box.x = int(self.real_x_position)
        self.hit_box.y = int(self.real_y_position)

        # Adjust offset
        # This is necessary for offsets that are not TILE_SIZE dividers
        x_remainder = self.rect.right % settings.TILE_SIZE
        y_remainder = self.rect.bottom % settings.TILE_SIZE

        if x_remainder < self.speed:
            # TODO: Calculate value based on the direction
            self.hit_box.x = self.hit_box.x - x_remainder

        if y_remainder < self.speed:
            # TODO: Calculate value based on the direction
            self.hit_box.y = self.hit_box.y - y_remainder

        # Adjust position
        self.real_x_position = self.hit_box.x
        self.real_y_position = self.hit_box.y

        # Recognize the moment when monster moves to a new area
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

            # If the vector is not found, recalculate the path and set a new vector
            if not self.movement_vector:
                self.calculate_path_to_player()
                self.set_movement_vector()

                # If the vector is still not found, the movement is off
                if not self.movement_vector:
                    self.is_moving = False

    def check_collision(self):
        is_collision_detected = False

        # Moving obstacle
        for sprite in self.moving_obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                # Collision was detected
                is_collision_detected = True
                break

        return is_collision_detected

    def set_movement_vector(self):
        movement_vector = None

        for index, item in enumerate(self.path):
            if item == tuple(self.current_position_on_map) and index + 1 < len(self.path):
                next_position_on_map = self.path[index + 1]
                movement_vector = pygame.math.Vector2(
                    next_position_on_map[0] - self.current_position_on_map[0],
                    next_position_on_map[1] - self.current_position_on_map[1])
                break

        self.movement_vector = movement_vector

    def refresh_obstacle_map(self):
        # The obstacle map has changed - regenerate lists and calculate a new path
        self.all_tiles = []
        self.obstacles = []
        self.create_all_tiles_and_obstacles_lists()
        self.calculate_path_to_player()

    def set_player_tile_position(self):
        # Calculate a new path
        self.calculate_path_to_player()

    def calculate_path_to_player(self):
        start_position = tuple(self.current_position_on_map)
        end_position = self.game_state.player_tile_position

        # Get path
        is_end_reached, self.path, frontier, came_from = self.breadth_first_search_helper.search(self.all_tiles,
                                                                                                 self.obstacles,
                                                                                                 start_position,
                                                                                                 end_position)

        # Reverse the path (direction: from monster to player)
        self.path.reverse()
        # Add player position to the end of the path
        self.path.append(self.game_state.player_tile_position)
