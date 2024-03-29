import pygame
import settings
import spritesheet


class Tombstone(pygame.sprite.Sprite):
    def __init__(self, position, groups):
        super().__init__(groups)

        # Sprite animation variables
        self.sprites = []
        self.load_all_sprites(16, 16, (int(settings.TILE_SIZE), int(settings.TILE_SIZE)), (0, 0, 0))
        self.number_of_sprites = 3
        self.costume_switching_threshold = 4
        self.costume_step_counter = 0
        self.costume_step_counter_increment = 1
        self.costume_index = 0

        # Image
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        self.can_be_removed_counter = 10

    def load_all_sprites(self, source_sprite_width, source_sprite_height, scale, key_color):
        # Load image with all sprite sheets
        sprite_sheet = spritesheet.SpriteSheet(
            pygame.image.load('img/skull.png').convert_alpha(),
            source_sprite_width,
            source_sprite_height,
            scale,
            key_color
        )

        self.sprites.append(sprite_sheet.get_image(0, 0))
        self.sprites.append(sprite_sheet.get_image(1, 0))
        self.sprites.append(sprite_sheet.get_image(2, 0))
        self.sprites.append(sprite_sheet.get_image(3, 0))

    def update(self):
        # Increase costume step counter
        self.costume_step_counter += self.costume_step_counter_increment
        self.change_costume()

    def change_costume(self):
        # Change costume only if threshold exceeded
        if self.costume_step_counter > self.costume_switching_threshold:
            # Reset counter
            self.costume_step_counter = 0
            if self.costume_index < self.number_of_sprites:
                # Increase costume index
                self.costume_index += 1
                # Set new image
                self.image = self.sprites[self.costume_index]
            else:
                self.can_be_removed_counter -= 1

    def is_expired(self):
        return self.can_be_removed_counter < 0
