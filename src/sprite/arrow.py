import pygame
import settings
import game_helper
from src.abstract_classes.enemy_with_energy import EnemyWithEnergy
import sprite_helper
from src.direction import Direction
from src.sprite.custom_draw_sprite import CustomDrawSprite


class Arrow(CustomDrawSprite):
    def __init__(self, position, groups, enemy_sprites, obstacle_sprites, moving_obstacle_sprites, arrow_direction):
        super().__init__(groups)

        # Direction and states
        self.direction = arrow_direction

        # Image
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Enemies
        self.enemy_sprites = enemy_sprites

        # Obstacles
        self.obstacle_sprites = obstacle_sprites
        self.moving_obstacle_sprites = moving_obstacle_sprites

        # Properties
        self.speed = game_helper.multiply_by_tile_size_ratio(13)
        self.damage_power = 60

    def get_image(self):
        sprites = sprite_helper.get_all_arrow_sprites()

        image = None
        if self.direction == Direction.RIGHT:
            image = sprites['right'][0]
        elif self.direction == Direction.LEFT:
            image = sprites['left'][0]
        elif (self.direction == Direction.UP or
              self.direction == Direction.LEFT_UP or
              self.direction == Direction.RIGHT_UP):
            image = sprites['up'][0]
        elif (self.direction == Direction.DOWN or
              self.direction == Direction.LEFT_DOWN or
              self.direction == Direction.RIGHT_DOWN):
            image = sprites['down'][0]

        return image

    def custom_draw(self, game_surface, offset):
        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)

    def update(self):
        self.move()

    def move(self):
        if self.direction == Direction.RIGHT:
            self.hit_box.x += self.speed
        elif self.direction == Direction.LEFT:
            self.hit_box.x -= self.speed
        if (self.direction == Direction.UP or
                self.direction == Direction.LEFT_UP or
                self.direction == Direction.RIGHT_UP):
            self.hit_box.y -= self.speed
        elif (self.direction == Direction.DOWN or
              self.direction == Direction.LEFT_DOWN or
              self.direction == Direction.RIGHT_DOWN):
            self.hit_box.y += self.speed

        # Check collision
        self.check_collision()

    def check_collision(self):
        # Check collision with enemy sprites
        for sprite in self.enemy_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                               pygame.sprite.collide_mask):
                    sprite_hit_box = sprite.hit_box
                    if isinstance(sprite, EnemyWithEnergy):
                        sprite.decrease_energy(self.damage_power)
                        self.kill()
                        self.create_particle_effect(sprite_hit_box, 12, settings.ENEMY_PARTICLE_COLORS)
        # Check collision with obstacle sprites
        for sprite in self.obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                               pygame.sprite.collide_mask):
                    self.kill()
                    self.create_particle_effect(sprite.hit_box, 12, settings.OBSTACLE_PARTICLE_COLORS)
        # Check collision with moving obstacle sprites
        for sprite in self.moving_obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False,
                                               pygame.sprite.collide_mask):
                    self.kill()
                    self.create_particle_effect(sprite.hit_box, 12, settings.OBSTACLE_PARTICLE_COLORS)

    def create_particle_effect(self, target_sprite_hit_box, number_of_sparks, colors):
        collided_position = game_helper.get_collided_rectangle(target_sprite_hit_box, self.hit_box).center
        pygame.event.post(
            pygame.event.Event(settings.ADD_PARTICLE_EFFECT_EVENT,
                               {"position": collided_position,
                                "number_of_sparks": number_of_sparks,
                                "colors": colors}))
