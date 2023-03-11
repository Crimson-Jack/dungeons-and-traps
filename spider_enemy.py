import pygame
import settings
from custom_draw_sprite import CustomDrawSprite


class SpiderEnemy(CustomDrawSprite):
    def __init__(self, image, position, groups, speed, net_length, motion_schedule, moving_obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Create movement variables
        self.is_moving = False
        self.movement_vector = pygame.math.Vector2((0, 1))
        self.speed = speed
        self.min_y_position = self.rect.top
        self.max_net_length = settings.TILE_SIZE * net_length

        # Create motion variables
        self.motion_schedule = motion_schedule
        self.step_counter = 0
        self.motion_index = 0
        self.motion_switching_threshold = self.motion_schedule[self.motion_index]

        # Real position is required to store the real distance, which is then cast to integer
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
                # Stop the moving
                self.is_moving = False

        # Set the movement offset
        self.rect.center = self.hit_box.center

    def change_motion(self):
        # Change motion only if threshold exceeded
        if self.step_counter > self.motion_switching_threshold:
            # Reset counter and increase motion index
            self.step_counter = 0
            self.motion_index += 1
            # If it's the last motion state - start from the first state (index = 0)
            if self.motion_index >= len(self.motion_schedule):
                self.motion_index = 0

            # Set a new threshold from motion schedule
            self.motion_switching_threshold = self.motion_schedule[self.motion_index]

            # Start the moving
            self.is_moving = True

        # Increase step counter
        self.step_counter += 1

    def update(self):
        if self.is_moving:
            self.move()
        else:
            self.change_motion()

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
                    # Stop the moving
                    self.is_moving = False

                # Change movement vector
                self.movement_vector.y = self.movement_vector.y * -1

                # Adjust position after collision
                self.real_y_position = float(self.hit_box.y)

                # Collision was detected
                is_collision_detected = True

        return is_collision_detected
