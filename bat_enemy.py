import pygame
import random
import game_helper
import settings
import sprite_helper
from custom_draw_sprite import CustomDrawSprite
from obstacle_map_refresh_sprite import ObstacleMapRefreshSprite
from breadth_first_search_helper import BreadthFirstSearchHelper
from enemy_with_energy import EnemyWithEnergy
from bat_tile_details import BatTileDetails


class BatEnemy(CustomDrawSprite, EnemyWithEnergy, ObstacleMapRefreshSprite):
    def __init__(self, frames, position, groups, game_state, details: BatTileDetails, name, obstacle_map,
                 moving_obstacle_sprites, hostile_force_sprites):
        super().__init__(groups)

        # Base
        self.game_state = game_state
        self.name = name
        self.damage_power = details.damage_power
        self.score = details.score

        # Energy
        self.max_energy = details.energy
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

        # Movement variables
        self.speed = details.speed
        self.movement_vector = pygame.math.Vector2(0, 0)
        self.is_moving = False
        self.start_delay = details.start_delay
        self.start_delay_counter = self.start_delay

        # Set positions on map
        self.current_position_on_map = [
            (self.rect.right // settings.TILE_SIZE) - 1,
            (self.rect.bottom // settings.TILE_SIZE) - 1
        ]
        self.new_position_on_map = list(self.current_position_on_map)

        # Track variables
        self.track = list()
        self.create_track(self.current_position_on_map, details.points_path)
        self.track_position = self.get_next_track_position()

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

    def create_track(self, starting_point, points_path):
        # Create relative track from points
        relative_track = list()
        # Add points in one direction
        for point in points_path:
            relative_track.append(point)
        # Add points in the opposite direction (reverse)
        for value in reversed(points_path):
            relative_track.append((-value[0], -value[1]))

        # Convert path from relative to absolute
        self.track.append((starting_point[0], starting_point[1]))
        for point in relative_track:
            self.track.append((self.track[-1][0] + point[0], self.track[-1][1] + point[1]))

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
            if not self.is_resting:
                self.set_next_move()
            else:
                self.start_delay_counter -= 1
                if self.start_delay_counter < 0:
                    self.is_resting = False
                    self.start_delay_counter = self.start_delay
                    self.set_next_move()

    def set_next_move(self):
        if self.check_if_all_track_positions_are_blocked():
            if self.try_to_set_random_movement_vector():
                self.is_moving = True
                self.path.clear()
        else:
            self.calculate_path()
            if self.try_to_set_movement_vector_from_path():
                self.is_moving = True

            if not self.is_moving:
                self.track_position = self.get_next_track_position()
                self.calculate_path()
                if self.try_to_set_movement_vector_from_path():
                    self.is_moving = True

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

        if self.check_collision_with_moving_obstacles():
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

                # Find out if the next move is possible
                if not self.try_to_set_movement_vector_from_path():
                    self.is_moving = False

        # Increase costume step counter
        self.costume_step_counter += 1

    def check_collision_with_moving_obstacles(self):
        is_collision_detected = False

        for sprite in self.moving_obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                is_collision_detected = True
                break

        return is_collision_detected

    def try_to_set_movement_vector_from_path(self):
        movement_vector = None

        for index, item in enumerate(self.path):
            if item == tuple(self.current_position_on_map) and index + 1 < len(self.path):
                next_position_on_map = self.path[index + 1]
                movement_vector = pygame.math.Vector2(
                    next_position_on_map[0] - self.current_position_on_map[0],
                    next_position_on_map[1] - self.current_position_on_map[1])
                break

        self.movement_vector = movement_vector
        return self.movement_vector is not None

    def try_to_set_random_movement_vector(self):
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
        return self.movement_vector is not None

    def refresh_obstacle_map(self):
        # The obstacle map has changed - regenerate lists and calculate a new path
        self.all_tiles = []
        self.obstacles = []
        self.create_all_tiles_and_obstacles_lists()
        self.calculate_path()

    def calculate_path(self):
        start_position = tuple(self.current_position_on_map)
        end_position = self.track_position

        # Get path
        is_end_reached, self.path, frontier, came_from = self.breadth_first_search_helper.search(self.all_tiles,
                                                                                                 self.obstacles,
                                                                                                 start_position,
                                                                                                 end_position)

        if is_end_reached:
            # Reverse the path (direction: from monster to player)
            self.path.reverse()
            # Add player position to the end of the path
            self.path.append(self.track_position)

        print(f"calculate_path {self.path}")

    def get_next_track_position(self):
        self.track.append(self.track[0])
        self.track.remove(self.track[0])

        print(f"get_next_track_position: {self.track}")

        return self.track[0]

    def check_if_all_track_positions_are_blocked(self):
        all_blocked = True
        track_without_current_position = list(filter(lambda point: point != tuple(self.current_position_on_map), self.track))
        for item in track_without_current_position:
            if item not in self.obstacles:
                all_blocked = False
                break

        print(f"check_if_all_track_positions_are_blocked {self.current_position_on_map} {all_blocked}")
        return all_blocked

    def decrease_energy(self, energy_decrease_step):
        self.collided_with_weapon = True
        self.is_resting = True
        self.is_moving = False

        if self.energy > 0:
            self.energy -= energy_decrease_step
            if self.energy < 0:
                self.energy = 0

        if self.energy == 0:
            self.kill()

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

    def kill(self):
        super().kill()
        self.game_state.increase_score(self.score)
        pygame.event.post(pygame.event.Event(settings.ADD_TOMBSTONE_EVENT, {"position": self.rect.topleft}))

    def get_damage_power(self):
        return self.damage_power

