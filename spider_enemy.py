import pygame
import settings
from custom_draw_sprite import CustomDrawSprite


class SpiderEnemy(CustomDrawSprite):
    def __init__(self, image, position, groups, speed, net_length, moving_obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Create movement variables
        self.movement_vector = pygame.math.Vector2((0, 1))
        self.speed = speed
        self.min_y_position = self.rect.topleft[1]
        self.max_net_length = settings.TILE_SIZE * net_length

        # Real position is required to store the real distance, which is then casted to integer
        self.real_y_position = float(self.hit_box.y)

        # Moving obstacles
        self.moving_obstacle_sprites = moving_obstacle_sprites

    def move(self):
        # Calculate real y position
        self.real_y_position += float(self.movement_vector.y * self.speed)

        # Cast real position to integer and check the collision
        self.hit_box.y = int(self.real_y_position)
        if not self.collision():
            # Start position and net length
            if self.hit_box.y > self.min_y_position + self.max_net_length:
                self.movement_vector.y = self.movement_vector.y * -1
            elif self.hit_box.y < self.min_y_position:
                self.movement_vector.y = self.movement_vector.y * -1

        # Set the movement offset
        self.rect.center = self.hit_box.center

    def update(self):
        self.move()

    def custom_draw(self, game_surface, offset):
        # Draw a net (line) from the beginning to the end spider position
        start_position = pygame.Vector2((self.rect.center[0], self.min_y_position)) + offset
        end_position = pygame.Vector2(self.rect.center) + offset
        pygame.draw.line(game_surface, (215, 215, 215), start_position, end_position, 2)

        # Draw sprite
        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)

    def collision(self):
        is_collision_detected = False
        # Moving obstacle
        for sprite in self.moving_obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if self.movement_vector.y > 0:
                    self.hit_box.bottom = sprite.hit_box.top
                if self.movement_vector.y < 0:
                    self.hit_box.top = sprite.hit_box.bottom
                # Change movement vector
                self.movement_vector.y = self.movement_vector.y * -1
                self.real_y_position = float(self.hit_box.y)
                is_collide = True
        return is_collision_detected
