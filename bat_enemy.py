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

        # Path variables
        self.track = list()
        self.create_track(self.current_position_on_map, details.points_path)
        print(self.track)

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
        self.is_moving = True

    def move(self):
        # Increase costume step counter
        self.costume_step_counter += 1

    # def calculate_path_to_player(self):
    #     start_position = tuple(self.current_position_on_map)
    #     end_position = self.game_state.player_tile_position
    #
    #     # Get path
    #     is_end_reached, self.path, frontier, came_from = self.breadth_first_search_helper.search(self.all_tiles,
    #                                                                                              self.obstacles,
    #                                                                                              start_position,
    #                                                                                              end_position)
    #
    #     if is_end_reached:
    #         # Reverse the path (direction: from monster to player)
    #         self.path.reverse()
    #         # Add player position to the end of the path
    #         self.path.append(self.game_state.player_tile_position)

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

