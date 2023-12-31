import pygame
import settings
import spritesheet


class Tombstone(pygame.sprite.Sprite):
    def __init__(self, position, groups):
        super().__init__(groups)

        # Sprite
        self.sprites = []
        self.load_all_sprites(16, 16, (int(settings.TILE_SIZE), int(settings.TILE_SIZE)), (0, 0, 0))

        # Image
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

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
