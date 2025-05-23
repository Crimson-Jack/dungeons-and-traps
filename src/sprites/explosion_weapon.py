import pygame

from settings import Settings
from src.enums.direction import Direction
from src.game_helper import GameHelper
from src.sprite_helper import SpriteHelper
from src.abstract_classes.enemy_with_energy import EnemyWithEnergy
from src.sprites.custom_draw_sprite import CustomDrawSprite


class ExplosionWeapon(CustomDrawSprite):
    def __init__(self, position, groups, enemy_sprites):
        super().__init__(groups)
        self.enemy_sprites = enemy_sprites

        # Sprite animation variables
        self.sprites = SpriteHelper.get_all_tnt_sprites()

        # Image
        self.image = self.sprites['right'][0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Direction and states
        self.direction = Direction.RIGHT
        self.is_armed = False

        # Offset position
        self.last_center_position_with_offset = None

        # Explosion variables
        self.range = (Settings.EXPLOSION_WEAPON_RANGE + 1) * Settings.TILE_SIZE
        self.damage_power = 300
        self.is_fired = False
        self.step_counter = 0
        self.explosion_starting_threshold = Settings.NUMBER_OF_EXPLOSION_STEPS

    def update(self):
        if self.is_fired:
            self.step_counter += 1
            if self.step_counter > self.explosion_starting_threshold:
                # Damage enemies in range
                for enemy in self.enemy_sprites:
                    if self.is_enemy_in_range(enemy) and isinstance(enemy, EnemyWithEnergy):
                        enemy.decrease_energy(self.damage_power)
                # Reset counter
                self.step_counter = 0
                self.is_fired = False

    def is_enemy_in_range(self, enemy):
        distance = (abs(enemy.rect.center[0] - self.rect.center[0]),
                    abs(enemy.rect.center[1] - self.rect.center[1]))

        return (distance[0]**2 + distance[1]**2)**0.5 < self.range

    def custom_draw(self, game_surface, offset):
        if self.is_armed:
            # Draw sprite
            offset_position = self.rect.topleft + offset
            game_surface.blit(self.image, offset_position)

            # Save the last center position with offset
            self.last_center_position_with_offset = self.rect.center + offset

    def set_position(self, position):
        # Calculate additional offset
        new_position = [position[0], position[1]]
        position_offset = GameHelper.multiply_by_tile_size_ratio(24)
        # Add additional offset to the base position
        if self.direction == Direction.RIGHT:
            new_position[0] += position_offset
        elif self.direction == Direction.LEFT:
            new_position[0] -= position_offset
        elif (self.direction == Direction.DOWN or
              self.direction == Direction.LEFT_DOWN or
              self.direction == Direction.RIGHT_DOWN):
            new_position[1] += position_offset
        elif (self.direction == Direction.UP or
              self.direction == Direction.LEFT_UP or
              self.direction == Direction.RIGHT_UP):
            new_position[1] -= position_offset

        self.rect = self.image.get_rect(topleft=new_position)
        self.hit_box = self.rect

    def set_costume(self, new_direction):
        self.direction = new_direction
        # Set image based on direction
        if self.direction == Direction.RIGHT:
            self.image = self.sprites['right'][0]
        elif self.direction == Direction.LEFT:
            self.image = self.sprites['left'][0]
        elif (self.direction == Direction.UP or
              self.direction == Direction.LEFT_UP or
              self.direction == Direction.RIGHT_UP):
            self.image = self.sprites['up'][0]
        elif (self.direction == Direction.DOWN or
              self.direction == Direction.LEFT_DOWN or
              self.direction == Direction.RIGHT_DOWN):
            self.image = self.sprites['down'][0]

    def fire(self):
        if self.is_armed:
            pygame.event.post(pygame.event.Event(Settings.CREATE_EXPLODE_EFFECT_EVENT, {"position": self.last_center_position_with_offset}))
            self.is_fired = True

    def arm_weapon(self):
        self.is_armed = True

    def disarm_weapon(self):
        self.is_armed = False
