import pygame
import settings
import game_helper
import enemy_with_energy
import spritesheet
import direction
from custom_draw_sprite import CustomDrawSprite


class Arrow(CustomDrawSprite):
    def __init__(self, position, groups, enemy_sprites, obstacle_sprites, moving_obstacle_sprites, arrow_direction):
        super().__init__(groups)

        # Direction and states
        self.direction = arrow_direction

        # Image
        self.image = self.get_image(16, 16, (int(settings.TILE_SIZE), int(settings.TILE_SIZE)), (0, 0, 0))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Enemies
        self.enemy_sprites = enemy_sprites

        # Obstacles
        self.obstacle_sprites = obstacle_sprites
        self.moving_obstacle_sprites = moving_obstacle_sprites

        # Properties
        self.speed = game_helper.multiply_by_tile_size_ratio(13)
        self.power = 60

    def get_image(self, source_sprite_width, source_sprite_height, scale, key_color):
        # Load image with all sprite sheets
        sprite_sheet = spritesheet.SpriteSheet(
            pygame.image.load('img/arrow.png').convert_alpha(),
            source_sprite_width,
            source_sprite_height,
            scale,
            key_color
        )

        image = None
        if self.direction == direction.Direction.RIGHT:
            image = sprite_sheet.get_image(0, 0)
        elif self.direction == direction.Direction.LEFT:
            image = sprite_sheet.get_image(1, 0)
        elif (self.direction == direction.Direction.UP or
              self.direction == direction.Direction.LEFT_UP or
              self.direction == direction.Direction.RIGHT_UP):
            image = sprite_sheet.get_image(2, 0)
        elif (self.direction == direction.Direction.DOWN or
              self.direction == direction.Direction.LEFT_DOWN or
              self.direction == direction.Direction.RIGHT_DOWN):
            image = sprite_sheet.get_image(3, 0)

        return image

    def custom_draw(self, game_surface, offset):
        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)

    def update(self):
        self.move()

    def move(self):
        if self.direction == direction.Direction.RIGHT:
            self.hit_box.x += self.speed
        elif self.direction == direction.Direction.LEFT:
            self.hit_box.x -= self.speed
        if (self.direction == direction.Direction.UP or
                self.direction == direction.Direction.LEFT_UP or
                self.direction == direction.Direction.RIGHT_UP):
            self.hit_box.y -= self.speed
        elif (self.direction == direction.Direction.DOWN or
              self.direction == direction.Direction.LEFT_DOWN or
              self.direction == direction.Direction.RIGHT_DOWN):
            self.hit_box.y += self.speed

        # Check collision
        self.check_collision()

    def check_collision(self):
        # Check collision with enemy sprites
        for sprite in self.enemy_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                               pygame.sprite.collide_mask):
                    if isinstance(sprite, enemy_with_energy.EnemyWithEnergy):
                        sprite.decrease_energy(self.power)
                        if sprite.get_energy() == 0:
                            sprite.kill()
                        self.kill()
        # Check collision with obstacle sprites
        for sprite in self.obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                               pygame.sprite.collide_mask):
                    self.kill()
        # Check collision with moving obstacle sprites
        for sprite in self.moving_obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                               pygame.sprite.collide_mask):
                    self.kill()
