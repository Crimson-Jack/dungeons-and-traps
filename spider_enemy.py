import pygame
import game_helper
import settings
import spritesheet
from custom_draw_sprite import CustomDrawSprite
from enemy_with_energy import EnemyWithEnergy


class SpiderEnemy(CustomDrawSprite, EnemyWithEnergy):
    def __init__(self, image, position, groups, speed, net_length, motion_schedule, moving_obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Energy
        self.max_energy = 100
        self.energy = self.max_energy
        self.energy_increase_step = 0.25

        # Animation variables
        self.number_of_sprites = 5
        self.costume_switching_threshold = self.max_energy // self.number_of_sprites
        self.costume_index = 0
        self.sprites = {
            'down': []}
        self.load_all_sprites(16, 16, (int(settings.TILE_SIZE), int(settings.TILE_SIZE)), (0, 0, 0))

        # Movement variables
        self.is_moving = False
        self.movement_vector = pygame.math.Vector2((0, 1))
        self.speed = speed
        self.min_y_position = self.rect.top
        self.max_net_length = settings.TILE_SIZE * net_length

        # Motion variables
        self.motion_schedule = motion_schedule
        self.step_counter = 0
        self.motion_index = 0
        self.motion_switching_threshold = self.motion_schedule[self.motion_index]

        # Real position is required to store the real distance, which is then cast to integer
        self.real_y_position = float(self.hit_box.y)

        # Moving obstacles
        self.moving_obstacle_sprites = moving_obstacle_sprites

        # State variables
        self.collided_with_weapon = False

    def load_all_sprites(self, source_sprite_width, source_sprite_height, scale, key_color):
        # Load image with all sprite sheets
        sprite_sheet = spritesheet.SpriteSheet(
            pygame.image.load('img/spider-enemy.png').convert_alpha(),
            source_sprite_width,
            source_sprite_height,
            scale,
            key_color
        )

        # Sprites with the state: healthy
        self.sprites['down'].append(sprite_sheet.get_image(0, 0))

        # Sprites with the state: injured
        for number in range(0, self.number_of_sprites):
            self.sprites['down'].append(sprite_sheet.get_image(1, number))

    def __del__(self):
        # TODO: Implement animation
        pass

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
        self.heal_injuries()
        if self.is_moving:
            self.move()
        else:
            self.change_motion()

    def custom_draw(self, game_surface, offset):
        # Draw a net (line) from the beginning to the end spider position
        start_position = pygame.Vector2((self.rect.center[0], self.min_y_position)) + offset
        end_position = pygame.Vector2(self.rect.center) + offset
        pygame.draw.line(game_surface, (215, 215, 215), start_position, end_position, int(game_helper.multiply_by_tile_size_ratio(2, 1)))

        # Draw sprite
        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)

        # Draw an outline if it is collided
        if self.collided_with_weapon:
            outline_image = pygame.surface.Surface.copy(self.image)
            mask = pygame.mask.from_surface(self.image)
            mask_outline = mask.outline()
            pygame.draw.polygon(outline_image, (255, 255, 255), mask_outline, int(game_helper.multiply_by_tile_size_ratio(1, 1)))
            game_surface.blit(outline_image, offset_position)

            # Reset status of collided with weapon
            self.collided_with_weapon = False

    def heal_injuries(self):
        # Heal injuries slowly
        if self.energy < self.max_energy:
            self.energy += self.energy_increase_step

        new_costume_index = self.calculate_costume_index()
        if new_costume_index != self.costume_index:
            self.costume_index = int(new_costume_index)
            self.change_costume()

    def decrease_energy(self, energy_decrease_step):
        self.collided_with_weapon = True

        if self.energy > 0:
            self.energy -= energy_decrease_step
            if self.energy < 0:
                self.energy = 0

        new_costume_index = self.calculate_costume_index()
        if new_costume_index != self.costume_index:
            self.costume_index = int(new_costume_index)
            self.change_costume()

    def get_energy(self):
        return self.energy

    def calculate_costume_index(self):
        new_costume_index = self.energy // self.costume_switching_threshold
        new_costume_index = self.number_of_sprites - new_costume_index

        if new_costume_index >= self.number_of_sprites:
            new_costume_index = self.number_of_sprites - 1

        return new_costume_index

    def change_costume(self):
        self.image = self.sprites['down'][self.costume_index]
