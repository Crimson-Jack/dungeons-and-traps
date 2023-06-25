import pygame

import enemy_with_energy
import game_helper
import settings
import spritesheet
import direction
from custom_draw_sprite import CustomDrawSprite


class SwordWeapon(CustomDrawSprite):
    def __init__(self, position, groups, enemy_sprites, obstacle_sprites, moving_obstacle_sprites):
        super().__init__(groups)

        self.sprites = {
            'left': [],
            'right': [],
            'up': [],
            'down': []
        }
        self.load_all_sprites(16, 16, (int(settings.TILE_SIZE), int(settings.TILE_SIZE)), (0, 0, 0))

        # Sword image
        self.direction = direction.Direction.RIGHT
        self.image = self.sprites['right'][0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Visibility
        self.is_visible = False

        # Enemies
        self.enemy_sprites = enemy_sprites

        # Obstacles
        self.obstacle_sprites = obstacle_sprites
        self.moving_obstacle_sprites = moving_obstacle_sprites

    def load_all_sprites(self, source_sprite_width, source_sprite_height, scale, key_color):
        # Load image with all sprite sheets
        sprite_sheet = spritesheet.SpriteSheet(
            pygame.image.load('img/sword.png').convert_alpha(),
            source_sprite_width,
            source_sprite_height,
            scale,
            key_color
        )

        # Sprites
        self.sprites['right'].append(sprite_sheet.get_image(0, 0))
        self.sprites['left'].append(sprite_sheet.get_image(1, 0))
        self.sprites['up'].append(sprite_sheet.get_image(2, 0))
        self.sprites['down'].append(sprite_sheet.get_image(3, 0))

    def set_direction(self, new_direction):
        self.direction = new_direction
        # Set image based on direction
        if self.direction == direction.Direction.RIGHT:
            self.image = self.sprites['right'][0]
        elif self.direction == direction.Direction.LEFT:
            self.image = self.sprites['left'][0]
        elif self.direction == direction.Direction.UP:
            self.image = self.sprites['up'][0]
        elif self.direction == direction.Direction.DOWN:
            self.image = self.sprites['down'][0]

    def set_position(self, position):
        # Calculate additional offset
        new_position = [position[0], position[1]]
        position_offset = game_helper.multiply_by_tile_size_ratio(24)
        # Add additional offset to the base position
        if self.direction == direction.Direction.RIGHT:
            new_position[0] += position_offset
        elif self.direction == direction.Direction.LEFT:
            new_position[0] -= position_offset
        elif self.direction == direction.Direction.DOWN:
            new_position[1] += position_offset
        elif self.direction == direction.Direction.UP:
            new_position[1] -= position_offset

        self.rect = self.image.get_rect(topleft=new_position)
        self.hit_box = self.rect

    def update(self):
        if self.is_visible:
            # Check collision with enemy sprites
            for sprite in self.enemy_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                                   pygame.sprite.collide_mask):
                        if isinstance(sprite, enemy_with_energy.EnemyWithEnergy):
                            sprite.decrease_energy()
                            if sprite.get_energy() == 0:
                                sprite.kill()
            # Check collision with obstacle sprites
            for sprite in self.obstacle_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                                   pygame.sprite.collide_mask):
                        self.is_visible = False
            # Check collision with moving obstacle sprites
            for sprite in self.moving_obstacle_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                                   pygame.sprite.collide_mask):
                        self.is_visible = False

    def custom_draw(self, game_surface, offset):
        if self.is_visible:
            # Draw sprite
            offset_position = self.rect.topleft + offset
            game_surface.blit(self.image, offset_position)
