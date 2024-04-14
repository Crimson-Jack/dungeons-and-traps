import pygame
import game_helper
import settings
import sprite_helper
from custom_draw_sprite import CustomDrawSprite
from enemy_with_energy import EnemyWithEnergy
from spider_tile_details import SpiderTileDetails


class SpiderEnemy(CustomDrawSprite, EnemyWithEnergy):
    def __init__(self, frames, position, groups, name, details: SpiderTileDetails, moving_obstacle_sprites):
        super().__init__(groups)

        # Base
        self.name = name
        self.damage_power = details.damage_power

        # Energy
        self.max_energy = details.energy
        self.energy = self.max_energy
        self.energy_increase_step = self.energy / 400

        # Sprite animation variables
        self.sprites = []
        self.costume_switching_thresholds = []
        # Split frames into sprites (with the state healthy) and durations
        for frame in frames:
            self.sprites.append([pygame.transform.scale(frame[0], (settings.TILE_SIZE, settings.TILE_SIZE))])
            self.costume_switching_thresholds.append(game_helper.calculate_frames(frame[1]))
        # Number of sprites == number of columns
        self.number_of_sprites = len(self.sprites)
        self.costume_step_counter = 0
        self.costume_index = 0

        # Sprites in a damage state
        self.number_of_rows = 5
        self.costume_switching_threshold_for_damaged_state = self.max_energy // self.number_of_rows
        self.sprites = sprite_helper.add_spider_sprites_in_damaged_state(self.name, self.number_of_sprites,
                                                                         self.number_of_rows, self.sprites)

        # Image
        self.image = self.sprites[0][0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Movement variables
        self.is_moving = False
        self.movement_vector = pygame.math.Vector2((0, 1))
        self.speed = details.speed
        self.min_y_position = self.rect.top
        self.max_net_length = settings.TILE_SIZE * details.net_length

        # Motion variables
        self.motion_schedule = details.motion_schedule
        self.step_counter = 0
        self.motion_index = 0
        self.motion_switching_threshold = self.motion_schedule[self.motion_index]

        # Real position is required to store the real distance, which is then cast to integer
        self.real_y_position = float(self.hit_box.y)

        # Moving obstacles
        self.moving_obstacle_sprites = moving_obstacle_sprites

        # State variables
        self.collided_with_weapon = False

    def move(self):
        # Calculate real y position
        self.real_y_position += float(self.movement_vector.y * self.speed)

        # Cast real position to integer
        self.hit_box.y = int(self.real_y_position)

        # Check collision with moving obstacles
        (collision_detected, collision_hit_box) = self.check_collision()
        if collision_detected:
            if self.movement_vector.y > 0:
                self.hit_box.bottom = collision_hit_box.top
            if self.movement_vector.y < 0:
                self.hit_box.top = collision_hit_box.bottom
                # Stop the moving
                self.is_moving = False

            # Change movement vector
            self.movement_vector.y *= -1

            # Adjust position after collision
            self.real_y_position = float(self.hit_box.y)
        else:
            # Check start position and net length
            if self.hit_box.y > self.min_y_position + self.max_net_length:
                # Change movement vector
                self.movement_vector.y *= -1
            elif self.hit_box.y < self.min_y_position:
                # Change movement vector
                self.movement_vector.y *= -1
                # Stop the moving
                self.is_moving = False

    def check_collision(self):
        is_collision_detected = False
        collision_hit_box = None

        # Moving obstacle
        for sprite in self.moving_obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                # Collision was detected
                is_collision_detected = True
                # Save collided sprite hit box
                collision_hit_box = sprite.hit_box
                break

        return is_collision_detected, collision_hit_box

    def change_motion(self):
        # Change motion only if threshold exceeded
        if self.step_counter > self.motion_switching_threshold:
            # Reset counter and increase motion index
            self.step_counter = 0
            self.motion_index += 1
            # If it's the last motion state - start from the first state (index = 0)
            if self.motion_index >= len(self.motion_schedule):
                self.motion_index = 0

            # Set a new threshold from motion schedule
            self.motion_switching_threshold = self.motion_schedule[self.motion_index]

            # Start the moving
            self.is_moving = True

        # Increase step counter
        self.step_counter += 1

    def update(self):
        if self.number_of_sprites > 1:
            self.change_costume()

        self.heal_injuries()

        if self.is_moving:
            self.move()
        else:
            self.change_motion()

        self.costume_step_counter += 1

    def custom_draw(self, game_surface, offset):
        # Draw a net (line) from the beginning to the end spider position
        start_position = pygame.Vector2((self.rect.center[0], self.min_y_position)) + offset
        end_position = pygame.Vector2(self.rect.center) + offset
        pygame.draw.line(game_surface, (215, 215, 215), start_position, end_position,
                         int(game_helper.multiply_by_tile_size_ratio(2, 1)))

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

    def heal_injuries(self):
        # Heal injuries slowly
        if self.energy < self.max_energy:
            self.energy += self.energy_increase_step

        self.image = self.sprites[self.costume_index][int(self.calculate_costume_index_for_damaged_state())]

    def decrease_energy(self, energy_decrease_step):
        self.collided_with_weapon = True

        if self.energy > 0:
            self.energy -= energy_decrease_step
            if self.energy < 0:
                self.energy = 0

        self.image = self.sprites[self.costume_index][int(self.calculate_costume_index_for_damaged_state())]

    def get_energy(self):
        return self.energy

    def calculate_costume_index_for_damaged_state(self):
        new_index = self.energy // self.costume_switching_threshold_for_damaged_state
        new_index = self.number_of_rows - new_index

        if new_index >= self.number_of_rows:
            new_index = self.number_of_rows - 1

        return new_index

    def change_costume(self):
        # Change costume only if threshold exceeded
        if self.costume_step_counter > self.costume_switching_thresholds[self.costume_index]:

            # Reset counter and increase costume index
            self.costume_step_counter = 0
            self.costume_index += 1

            # If it's the last costume - start from the first costume
            if self.costume_index >= self.number_of_sprites:
                self.costume_index = 0

            self.image = self.sprites[self.costume_index][int(self.calculate_costume_index_for_damaged_state())]

    def kill(self):
        super().kill()
        pygame.event.post(pygame.event.Event(settings.ADD_TOMBSTONE_EVENT, {"position": self.rect.topleft}))

    def get_damage_power(self):
        return self.damage_power
