import pygame
import settings
from custom_draw_sprite import CustomDrawSprite


class FireFlameEnemy(CustomDrawSprite):
    def __init__(self, image, position, groups, speed, fire_length, motion_schedule, moving_obstacle_sprites):
        super().__init__(groups)
        self.base_image = image
        self.image = self.get_merged_image(2)
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Create movement variables
        self.is_moving = False
        self.movement_vector = pygame.math.Vector2((-1, 0))
        self.speed = speed
        self.max_fire_length = settings.TILE_SIZE * fire_length

        # Create motion variables
        self.motion_schedule = motion_schedule
        self.step_counter = 0
        self.motion_index = 0
        self.motion_switching_threshold = self.motion_schedule[self.motion_index]

        # Left and right positions of the flame
        self.max_left_flame_position = self.rect.left
        self.max_right_flame_position = self.rect.right

        # Real position is required to store the real distance, which is then cast to integer
        self.real_x_position = float(self.hit_box.x)

    def get_merged_image(self, count):
        base_image = pygame.transform.scale(self.base_image, (settings.TILE_SIZE, settings.TILE_SIZE))
        merged = pygame.surface.Surface((settings.TILE_SIZE*count, settings.TILE_SIZE))
        merged = merged.convert_alpha()
        merged.fill((0, 0, 0, 0))

        for index in range(count):
            merged.blit(base_image, (settings.TILE_SIZE * index, 0))

        return merged

    def custom_draw(self, game_surface, offset):
        # Draw a fire (line)
        start_position = pygame.Vector2((self.rect.right, self.rect.centery)) + offset
        end_position = pygame.Vector2((self.max_right_flame_position, self.rect.centery)) + offset
        if start_position.x < end_position.x:
            pygame.draw.line(game_surface, (247, 75, 75), start_position, end_position, 20)

        # Draw sprite
        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)

    def move(self):
        # Calculate real y position
        self.real_x_position += float(self.movement_vector.x * self.speed)

        # Start position and fire length
        if self.real_x_position < self.max_left_flame_position - self.max_fire_length:
            self.real_x_position = self.max_left_flame_position - self.max_fire_length
            self.movement_vector.x = self.movement_vector.x * -1
        elif self.real_x_position > self.max_left_flame_position:
            self.real_x_position = self.max_left_flame_position
            self.movement_vector.x = self.movement_vector.x * -1
            # Stop the moving
            self.is_moving = False

        # Cast real position to integer
        self.hit_box.x = int(self.real_x_position)

        # Create a new image
        if self.hit_box.x % settings.TILE_SIZE == 0:
            tail_length = (self.max_right_flame_position - self.hit_box.x) // settings.TILE_SIZE
            if self.movement_vector.x > 0:
                tail_length -= 1
            print(f'now {tail_length}')
            # Get a new image
            self.image = self.get_merged_image(tail_length)
            # Change rectangle and hit_box
            current_top_left_position = self.rect.topleft
            self.rect = self.image.get_rect(topleft=current_top_left_position)
            self.hit_box = self.rect

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
