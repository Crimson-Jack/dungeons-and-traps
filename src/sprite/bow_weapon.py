import game_helper
import sprite_helper
from src.direction import Direction
from src.sprite.arrow import Arrow
from src.sprite.custom_draw_sprite import CustomDrawSprite


class BowWeapon(CustomDrawSprite):
    def __init__(self, position, groups, enemy_sprites, obstacle_sprites, moving_obstacle_sprites):
        super().__init__(groups)

        # Sprite animation variables
        self.sprites = sprite_helper.get_all_bow_sprites()

        # Image
        self.image = self.sprites['right'][0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Enemies and obstacles
        self.enemy_sprites = enemy_sprites
        self.obstacle_sprites = obstacle_sprites
        self.moving_obstacle_sprites = moving_obstacle_sprites

        # Direction and states
        self.direction = Direction.RIGHT
        self.is_armed = False

        # Arrows
        self.arrows = list()

    def custom_draw(self, game_surface, offset):
        if self.is_armed:
            # Draw sprite
            offset_position = self.rect.topleft + offset
            game_surface.blit(self.image, offset_position)

    def set_position(self, position):
        # Calculate additional offset
        new_position = [position[0], position[1]]
        position_offset = game_helper.multiply_by_tile_size_ratio(24)
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
        self.arrows.append(Arrow(self.rect.topleft, tuple(self.groups()), self.enemy_sprites, self.obstacle_sprites,
                                 self.moving_obstacle_sprites, self.direction))

    def arm_weapon(self):
        self.is_armed = True

    def disarm_weapon(self):
        self.is_armed = False
