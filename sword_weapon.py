import pygame
import random
import enemy_with_energy
import game_helper
import settings
import spritesheet
import direction
from custom_draw_sprite import CustomDrawSprite


class SwordWeapon(CustomDrawSprite):
    def __init__(self, position, groups, enemy_sprites, obstacle_sprites, moving_obstacle_sprites):
        super().__init__(groups)

        # Sprite animation variables
        self.sprites = {
            'left': [],
            'right': [],
            'up': [],
            'down': []
        }
        self.load_all_sprites(16, 16, (int(settings.TILE_SIZE), int(settings.TILE_SIZE)), (0, 0, 0))
        self.costume_switching_threshold = 1
        self.number_of_sprites = 8
        self.costume_step_counter = 0
        self.costume_step_counter_increment = 2
        self.costume_index = 0

        # Image
        self.image = self.sprites['right'][0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Direction and states
        self.direction = direction.Direction.RIGHT
        self.is_armed = True
        self.is_moving = False
        self.is_blocked = False

        # Enemies
        self.enemy_sprites = enemy_sprites

        # Obstacles
        self.obstacle_sprites = obstacle_sprites
        self.moving_obstacle_sprites = moving_obstacle_sprites

        # Other
        self.power = 5

    def load_all_sprites(self, source_sprite_width, source_sprite_height, scale, key_color):
        # Load image with all sprite sheets
        sprite_sheet = spritesheet.SpriteSheet(
            pygame.image.load('img/sword_v2.png').convert_alpha(),
            source_sprite_width,
            source_sprite_height,
            scale,
            key_color
        )

        self.sprites['right'].append(sprite_sheet.get_image(0, 0))
        self.sprites['right'].append(sprite_sheet.get_image(0, 1))
        self.sprites['right'].append(sprite_sheet.get_image(0, 2))
        self.sprites['right'].append(sprite_sheet.get_image(0, 3))
        self.sprites['right'].append(sprite_sheet.get_image(0, 3))
        self.sprites['right'].append(sprite_sheet.get_image(0, 3))
        self.sprites['right'].append(sprite_sheet.get_image(0, 3))
        self.sprites['right'].append(sprite_sheet.get_image(0, 3))

        self.sprites['left'].append(sprite_sheet.get_image(1, 0))
        self.sprites['left'].append(sprite_sheet.get_image(1, 1))
        self.sprites['left'].append(sprite_sheet.get_image(1, 2))
        self.sprites['left'].append(sprite_sheet.get_image(1, 3))
        self.sprites['left'].append(sprite_sheet.get_image(1, 3))
        self.sprites['left'].append(sprite_sheet.get_image(1, 3))
        self.sprites['left'].append(sprite_sheet.get_image(1, 3))
        self.sprites['left'].append(sprite_sheet.get_image(1, 3))

        self.sprites['up'].append(sprite_sheet.get_image(2, 0))
        self.sprites['up'].append(sprite_sheet.get_image(2, 1))
        self.sprites['up'].append(sprite_sheet.get_image(2, 2))
        self.sprites['up'].append(sprite_sheet.get_image(2, 3))
        self.sprites['up'].append(sprite_sheet.get_image(2, 3))
        self.sprites['up'].append(sprite_sheet.get_image(2, 3))
        self.sprites['up'].append(sprite_sheet.get_image(2, 3))
        self.sprites['up'].append(sprite_sheet.get_image(2, 3))

        self.sprites['down'].append(sprite_sheet.get_image(3, 0))
        self.sprites['down'].append(sprite_sheet.get_image(3, 1))
        self.sprites['down'].append(sprite_sheet.get_image(3, 2))
        self.sprites['down'].append(sprite_sheet.get_image(3, 3))
        self.sprites['down'].append(sprite_sheet.get_image(3, 3))
        self.sprites['down'].append(sprite_sheet.get_image(3, 3))
        self.sprites['down'].append(sprite_sheet.get_image(3, 3))
        self.sprites['down'].append(sprite_sheet.get_image(3, 3))

    def set_costume(self, new_direction, index):
        self.direction = new_direction
        # Set image based on direction
        if self.direction == direction.Direction.RIGHT:
            self.image = self.sprites['right'][index]
        elif self.direction == direction.Direction.LEFT:
            self.image = self.sprites['left'][index]
        elif (self.direction == direction.Direction.UP or
              self.direction == direction.Direction.LEFT_UP or
              self.direction == direction.Direction.RIGHT_UP):
            self.image = self.sprites['up'][index]
        elif (self.direction == direction.Direction.DOWN or
              self.direction == direction.Direction.LEFT_DOWN or
              self.direction == direction.Direction.RIGHT_DOWN):
            self.image = self.sprites['down'][index]

    def set_position(self, position):
        # Calculate additional offset
        new_position = [position[0], position[1]]
        position_offset = game_helper.multiply_by_tile_size_ratio(24)
        # Add additional offset to the base position
        if self.direction == direction.Direction.RIGHT:
            new_position[0] += position_offset
        elif self.direction == direction.Direction.LEFT:
            new_position[0] -= position_offset
        elif (self.direction == direction.Direction.DOWN or
              self.direction == direction.Direction.LEFT_DOWN or
              self.direction == direction.Direction.RIGHT_DOWN):
            new_position[1] += position_offset
        elif (self.direction == direction.Direction.UP or
              self.direction == direction.Direction.LEFT_UP or
              self.direction == direction.Direction.RIGHT_UP):
            new_position[1] -= position_offset

        self.rect = self.image.get_rect(topleft=new_position)
        self.hit_box = self.rect

    def update(self):
        self.change_costume()
        if self.is_armed and self.is_moving:
            self.move()

    def custom_draw(self, game_surface, offset):
        if self.is_armed and self.is_moving and not self.is_blocked:
            # Draw sprite
            offset_position = self.rect.topleft + offset
            game_surface.blit(self.image, offset_position)

    def move(self):
        # Check collision
        self.check_collision()
        # Increase costume step counter
        self.costume_step_counter += self.costume_step_counter_increment

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
                        collided_position = game_helper.get_collided_rectangle(sprite.hit_box, self.hit_box).center
                        pygame.event.post(
                            pygame.event.Event(settings.ADD_PARTICLE_EFFECT_EVENT,
                                               {"position": collided_position,
                                                "number_of_sparks": 1,
                                                "colors": [settings.ENEMY_PARTICLE_COLORS[random.randint(0, len(settings.ENEMY_PARTICLE_COLORS)-1)]]}))
        # Check collision with obstacle sprites
        for sprite in self.obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                               pygame.sprite.collide_mask):
                    self.is_moving = False
                    self.is_blocked = True
        # Check collision with moving obstacle sprites
        for sprite in self.moving_obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                               pygame.sprite.collide_mask):
                    self.is_moving = False
                    self.is_blocked = True

    def change_costume(self):
        # Change costume only if threshold exceeded
        if self.costume_step_counter > self.costume_switching_threshold:
            # Reset counter and increase costume index
            self.costume_step_counter = 0
            self.costume_index += 1

            # If it's the last costume - start from the first costume (index = 0)
            if self.costume_index >= self.number_of_sprites:
                self.costume_index = 0
                pygame.event.post(pygame.event.Event(settings.PLAYER_IS_NOT_USING_WEAPON_EVENT))

            # Set new image
            self.set_costume(self.direction, self.costume_index)

    def arm_weapon(self):
        self.is_armed = True

    def disarm_weapon(self):
        self.is_armed = False

    def start_cutting(self):
        self.is_moving = True

    def stop_cutting(self):
        self.is_moving = False
