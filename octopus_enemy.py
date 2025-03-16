import pygame
import game_helper
import settings
from custom_draw_sprite import CustomDrawSprite


class OctopusEnemy(CustomDrawSprite):
    def __init__(self, frames, position, rotation, groups):
        super().__init__(groups)

        # Base
        self.damage_power = 30

        # Sprite animation variables
        self.sprites = []
        self.costume_switching_thresholds = []
        # Split frames into sprites and durations
        for frame in frames:
            self.sprites.append(pygame.transform.rotate(pygame.transform.scale(frame[0], (settings.TILE_SIZE, settings.TILE_SIZE)), -rotation))
            self.costume_switching_thresholds.append(game_helper.calculate_frames(frame[1]))
        # Number of sprites == number of columns
        self.number_of_sprites = len(self.sprites)
        self.costume_step_counter = 0
        self.costume_index = 0

        # Image
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Set positions on map
        self.current_position_on_map = [
            (self.rect.right // settings.TILE_SIZE) - 1,
            (self.rect.bottom // settings.TILE_SIZE) - 1
        ]
        self.new_position_on_map = list(self.current_position_on_map)

        # Real position is required to store the real distance, which is then cast to integer
        self.real_x_position = float(self.hit_box.x)
        self.real_y_position = float(self.hit_box.y)

    def update(self):
        if self.number_of_sprites > 1:
            self.change_costume()

        self.move()

    def move(self):
        # Increase costume step counter
        self.costume_step_counter += 1

    def custom_draw(self, game_surface, offset):
        # Draw sprite
        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)

        # Draw an outline if it is collided
        # if self.collided_with_weapon:
        #     outline_image = pygame.surface.Surface.copy(self.image)
        #     mask = pygame.mask.from_surface(self.image)
        #     mask_outline = mask.outline()
        #     pygame.draw.polygon(outline_image, (255, 255, 255), mask_outline,
        #                         int(game_helper.multiply_by_tile_size_ratio(1, 1)))
        #     game_surface.blit(outline_image, offset_position)
        #
        #     # Reset status of collided with weapon
        #     self.collided_with_weapon = False

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

    def get_damage_power(self):
        return self.damage_power