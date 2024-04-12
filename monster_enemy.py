import pygame
import random
import game_helper
import settings
import sprite_helper
from custom_draw_sprite import CustomDrawSprite
from obstacle_map_refresh_sprite import ObstacleMapRefreshSprite
from enemy_with_brain import EnemyWithBrain
from breadth_first_search_helper import BreadthFirstSearchHelper
from enemy_with_energy import EnemyWithEnergy


class MonsterEnemy(CustomDrawSprite, EnemyWithBrain, EnemyWithEnergy, ObstacleMapRefreshSprite):
    def __init__(self, frames, position, groups, name, speed, start_delay, energy, obstacle_map, game_state,
                 moving_obstacle_sprites):
        super().__init__(groups)

        # Base
        self.name = name

        # Energy
        self.max_energy = energy
        self.energy = self.max_energy

        # Sprite animation variables
        self.sprites = []
        self.costume_switching_thresholds = []
        # Split frames into sprites and durations
        for frame in frames:
            self.sprites.append(pygame.transform.scale(frame[0], (settings.TILE_SIZE, settings.TILE_SIZE)))
            self.costume_switching_thresholds.append(game_helper.calculate_frames(frame[1]))
        # Number of sprites == number of columns
        self.number_of_sprites = len(self.sprites)
        self.costume_step_counter = 0
        self.costume_index = 0

        # Sprite in a damage state
        self.sprite_in_damage_state = sprite_helper.get_monster_sprite_in_damaged_state(self.name)

        # Image
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Obstacle map
        self.obstacle_map = obstacle_map

        # Game state
        self.game_state = game_state

        # Movement variables
        self.speed = speed
        self.movement_vector = pygame.math.Vector2(0, 0)
        self.is_moving = False
        self.start_delay = start_delay
        self.start_delay_counter = self.start_delay
        self.range = 10

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
        self.path = []

        # Real position is required to store the real distance, which is then cast to integer
        self.real_x_position = float(self.hit_box.x)
        self.real_y_position = float(self.hit_box.y)

        # Moving obstacles
        self.moving_obstacle_sprites = moving_obstacle_sprites

        # State variables
        self.collided_with_weapon = False
        self.is_resting = False

    def create_all_tiles_and_obstacles_lists(self):
        for x in range(len(self.obstacle_map)):
            for y in range(len(self.obstacle_map[x])):
                self.all_tiles.append((y, x))
                if self.obstacle_map[x][y] > 0:
                    self.obstacles.append((y, x))

    def update(self):
        if self.number_of_sprites > 1:
            self.change_costume()
        if self.is_moving:
            self.move()
        else:
            self.start_delay_counter -= 1
            if self.start_delay_counter < 0:
                # Reset counter
                self.start_delay_counter = self.start_delay
                # Try to find a vector from path
                self.set_movement_vector()
                if self.movement_vector:
                    # If a vector is found, the movement is on
                    self.is_moving = True
                    self.is_resting = False
                else:
                    # Otherwise, try moving randomly (if is allowed)
                    self.set_random_movement_vector()
                    if self.movement_vector:
                        # If a random vector is found, the movement is on
                        self.is_moving = True
                        self.is_resting = False
                        # The path is not relevant in the random movement
                        self.path.clear()

    def move(self):
        # Calculate real y position
        self.real_x_position += float(self.movement_vector.x * self.speed)
        self.real_y_position += float(self.movement_vector.y * self.speed)

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

        if self.check_collision():
            # Collision with moving obstacle sprites was detected
            # Monster must be moved to the last valid position (using current map position)
            self.hit_box.x = self.current_position_on_map[0] * settings.TILE_SIZE
            self.hit_box.y = self.current_position_on_map[1] * settings.TILE_SIZE

            # Adjust real position after collision
            self.real_x_position = float(self.hit_box.x)
            self.real_y_position = float(self.hit_box.y)

            # Stop moving and early return
            self.is_moving = False
        else:
            # Recognize the moment when monster moves to a new area
            # In this case TILE_SIZE is a divisor of "right" or "bottom"
            if self.rect.right % settings.TILE_SIZE == 0:
                self.new_position_on_map[0] = (self.rect.right // settings.TILE_SIZE) - 1

            if self.rect.bottom % settings.TILE_SIZE == 0:
                self.new_position_on_map[1] = (self.rect.bottom // settings.TILE_SIZE) - 1

            # If position was changed, change position and determine new direction
            if self.current_position_on_map != self.new_position_on_map:
                # Adjust real position
                self.real_x_position = self.hit_box.x
                self.real_y_position = self.hit_box.y

                # Change current position (x or y or both)
                if self.current_position_on_map[0] != self.new_position_on_map[0]:
                    self.current_position_on_map[0] = self.new_position_on_map[0]
                if self.current_position_on_map[1] != self.new_position_on_map[1]:
                    self.current_position_on_map[1] = self.new_position_on_map[1]

                self.set_movement_vector()

                # If the vector is not found, recalculate the path and set a new vector
                if not self.movement_vector:
                    if self.is_player_in_range():
                        self.calculate_path_to_player()
                        self.set_movement_vector()

                    # If the vector is still not found, the movement is off
                    if not self.movement_vector:
                        self.is_moving = False

        # Increase costume step counter
        self.costume_step_counter += 1

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

        if self.is_player_in_range():
            for index, item in enumerate(self.path):
                if item == tuple(self.current_position_on_map) and index + 1 < len(self.path):
                    next_position_on_map = self.path[index + 1]
                    movement_vector = pygame.math.Vector2(
                        next_position_on_map[0] - self.current_position_on_map[0],
                        next_position_on_map[1] - self.current_position_on_map[1])
                    break

        self.movement_vector = movement_vector

    def set_random_movement_vector(self):
        movement_vector = None

        # Find the first empty tile nearby the monster
        possible_vectors = [
            pygame.math.Vector2(-1, 0),
            pygame.math.Vector2(1, 0),
            pygame.math.Vector2(0, -1),
            pygame.math.Vector2(0, 1),
        ]

        possible_vectors_length = len(possible_vectors)

        while possible_vectors_length > 0:
            random_value = random.randint(0, possible_vectors_length-1)
            verified_tile = (
                int(self.current_position_on_map[0] + possible_vectors[random_value][0]),
                int(self.current_position_on_map[1] + possible_vectors[random_value][1])
            )

            if verified_tile in self.obstacles:
                # Chose another tile
                possible_vectors.remove(possible_vectors[random_value])
                possible_vectors_length -= 1
            else:
                # The vector has been found and the tile is empty
                movement_vector = possible_vectors[random_value]
                break

        self.movement_vector = movement_vector

    def refresh_obstacle_map(self):
        # The obstacle map has changed - regenerate lists and calculate a new path
        self.all_tiles = []
        self.obstacles = []
        self.create_all_tiles_and_obstacles_lists()
        if self.is_player_in_range():
            self.calculate_path_to_player()

    def set_player_tile_position(self):
        # Player has changed position - calculate a new path
        if self.is_player_in_range():
            self.calculate_path_to_player()

    def calculate_path_to_player(self):
        start_position = tuple(self.current_position_on_map)
        end_position = self.game_state.player_tile_position

        # Get path
        is_end_reached, self.path, frontier, came_from = self.breadth_first_search_helper.search(self.all_tiles,
                                                                                                 self.obstacles,
                                                                                                 start_position,
                                                                                                 end_position)

        if is_end_reached:
            # Reverse the path (direction: from monster to player)
            self.path.reverse()
            # Add player position to the end of the path
            self.path.append(self.game_state.player_tile_position)

    def decrease_energy(self, energy_decrease_step):
        self.collided_with_weapon = True
        self.is_resting = True
        self.is_moving = False

        if self.energy > 0:
            self.energy -= energy_decrease_step
            if self.energy < 0:
                self.energy = 0

    def get_energy(self):
        return self.energy

    def custom_draw(self, game_surface, offset):
        # Draw sprite
        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)

        # Draw an outline if it is collided
        if self.collided_with_weapon:
            outline_image = pygame.surface.Surface.copy(self.image)
            mask = pygame.mask.from_surface(self.image)
            mask_outline = mask.outline()
            pygame.draw.polygon(outline_image, (255, 255, 255), mask_outline,
                                int(game_helper.multiply_by_tile_size_ratio(1, 1)))
            game_surface.blit(outline_image, offset_position)

            # Reset status of collided with weapon
            self.collided_with_weapon = False

    def change_costume(self):
        if self.is_resting:
            self.image = self.sprite_in_damage_state

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

    def is_player_in_range(self):
        monster_tile_position = tuple(self.current_position_on_map)
        player_tile_position = self.game_state.player_tile_position

        distance = abs(monster_tile_position[0] - player_tile_position[0]), abs(
            monster_tile_position[1] - player_tile_position[1])

        return distance[0] < self.range and distance[1] < self.range

    def kill(self):
        super().kill()
        pygame.event.post(pygame.event.Event(settings.ADD_TOMBSTONE_EVENT, {"position": self.rect.topleft}))
