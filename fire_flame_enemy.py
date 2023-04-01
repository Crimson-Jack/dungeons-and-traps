import pygame
import settings
from custom_draw_sprite import CustomDrawSprite
from obstacle_map_refresh_sprite import ObstacleMapRefreshSprite


class FireFlameEnemy(CustomDrawSprite, ObstacleMapRefreshSprite):
    def __init__(self, sprites, position, groups, speed, length, motion_schedule, moving_obstacle_sprites):
        super().__init__(groups)

        # Create sprite animation variables
        self.sprites = sprites
        self.number_of_sprites = len(sprites)
        self.costume_switching_threshold = 14
        self.costume_step_counter = 0
        self.costume_index = 0

        # Create image
        self.tail_length = 2
        self.base_image = sprites[0]
        self.image = self.get_merged_image()
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Max left and right positions of the flame
        self.max_rect_left_flame_position = self.rect.left
        self.max_rect_right_flame_position = self.rect.right

        # Create movement variables
        self.is_moving = False
        self.movement_vector = pygame.math.Vector2((-1, 0))
        self.speed = speed
        self.max_fire_length = settings.TILE_SIZE * length

        # Create motion variables
        self.motion_schedule = motion_schedule
        self.motion_step_counter = 0
        self.motion_index = 0
        self.motion_switching_threshold = self.motion_schedule[self.motion_index]

        # Real position is required to store the real distance, which is then cast to integer
        self.real_x_position = float(self.hit_box.left)

        # Moving obstacles
        self.moving_obstacle_sprites = moving_obstacle_sprites

        # Indicates the requirement to return to the initial image state
        self.reset_is_required_for_image = False

    def get_merged_image(self):
        base_image = pygame.transform.scale(self.base_image, (settings.TILE_SIZE, settings.TILE_SIZE))
        merged_image = pygame.surface.Surface((settings.TILE_SIZE*self.tail_length, settings.TILE_SIZE))
        merged_image = merged_image.convert_alpha()
        merged_image.fill((0, 0, 0, 0))

        for index in range(self.tail_length):
            merged_image.blit(base_image, (settings.TILE_SIZE * index, 0))

        return merged_image

    def set_new_image(self):
        # Get merged image
        self.image = self.get_merged_image()

        # Change (increase or decrease) rectangle and hit_box
        current_top_left_position = self.rect.topleft
        self.rect = self.image.get_rect(topleft=current_top_left_position)
        self.hit_box = self.rect

    def custom_draw(self, game_surface, offset):
        # Draw sprite if reset is not required
        if not self.reset_is_required_for_image:
            offset_position = self.rect.topleft + offset
            game_surface.blit(self.image, offset_position)

    def move(self):
        # Calculate real y position
        self.real_x_position += float(self.movement_vector.x * self.speed)

        # Check collision with moving obstacles
        (collision_detected, collision_hit_box_right) = self.check_collision()
        if collision_detected:
            # Set fire flame left border
            self.hit_box.left = collision_hit_box_right
            # Change movement vector always to the right direction
            self.movement_vector.x = 1
            # Adjust position after collision
            self.real_x_position = float(self.hit_box.x)
        else:
            # Check start position
            if self.real_x_position < self.max_rect_left_flame_position - self.max_fire_length + settings.TILE_SIZE:
                # Reverse
                self.movement_vector.x *= -1
            # Check fire flame length
            elif self.real_x_position > self.max_rect_left_flame_position + settings.TILE_SIZE:
                # Reverse
                self.movement_vector.x *= -1
                # Stop the moving
                self.is_moving = False

        # Cast real position to integer
        self.hit_box.x = int(self.real_x_position)

        # Set the movement offset
        self.rect.center = self.hit_box.center

        # Adjust offset
        # This is necessary for offsets that are not TILE_SIZE dividers
        x_remainder = self.rect.right % settings.TILE_SIZE

        if x_remainder < self.speed:
            self.hit_box.x = self.hit_box.x - x_remainder
            self.rect.center = self.hit_box.center

        # Recognize the moment when fire flame moves to a new area
        if self.hit_box.x % settings.TILE_SIZE == 0:

            # Calculate the length
            self.tail_length = (self.max_rect_right_flame_position - self.hit_box.x) // settings.TILE_SIZE
            if self.tail_length < 1:
                self.tail_length = 1

            if self.movement_vector.x > 0:
                self.tail_length -= 1

            # Set image
            self.set_new_image()

        # Increase costume step counter
        self.costume_step_counter += 1

    def change_motion(self):
        # Change motion only if threshold exceeded
        if self.motion_step_counter > self.motion_switching_threshold:
            # Reset counter and increase motion index
            self.motion_step_counter = 0
            self.motion_index += 1
            # If it's the last motion state - start from the first state (index = 0)
            if self.motion_index >= len(self.motion_schedule):
                self.motion_index = 0

            # Set a new threshold from motion schedule
            self.motion_switching_threshold = self.motion_schedule[self.motion_index]

            # Start the moving
            self.is_moving = True

        # Increase step counter
        self.motion_step_counter += 1

        # Increase costume step counter
        self.costume_step_counter += 1

    def update(self):
        self.change_costume()
        if self.is_moving:
            self.move()
        else:
            self.change_motion()

        # Reset the image length if it's required
        if self.reset_is_required_for_image:
            # Set a new image
            self.set_new_image()
            # Reset is not required anymore
            self.reset_is_required_for_image = False

    def check_collision(self):
        is_collision_detected = False
        hit_box_right = 0

        # Moving obstacle
        for sprite in self.moving_obstacle_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                # Save collided sprite right border
                hit_box_right = sprite.hit_box.right
                # Collision was detected
                is_collision_detected = True
                break

        return is_collision_detected, hit_box_right

    def change_costume(self):
        # Change costume only if threshold exceeded
        if self.costume_step_counter > self.costume_switching_threshold:

            # Reset counter and increase costume index
            self.costume_step_counter = 0
            self.costume_index += 1

            # If it's the last costume - start from the second costume (index = 1)
            if self.costume_index > self.number_of_sprites:
                self.costume_index = 1

            # Set image based on costume index
            self.base_image = self.sprites[self.costume_index-1]

            # Set new image
            self.set_new_image()

    def refresh_obstacle_map(self):
        # Check if moving obstacle is collided with the flame
        collision_detected, collision_hit_box_right = self.check_collision()
        if collision_detected:
            # Calculate tail length
            self.tail_length = (self.max_rect_right_flame_position - collision_hit_box_right) // settings.TILE_SIZE
            # Set flag - reset is required for the image
            self.reset_is_required_for_image = True
