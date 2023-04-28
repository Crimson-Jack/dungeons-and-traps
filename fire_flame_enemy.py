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

        # Create movement variables
        self.is_moving = False
        self.speed = speed
        self.max_fire_length = length * settings.TILE_SIZE

        # Create motion variables
        self.motion_schedule = motion_schedule
        self.motion_step_counter = 0
        self.motion_index = 0
        self.motion_switching_threshold = self.motion_schedule[self.motion_index]

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

    def custom_draw(self, game_surface, offset):
        # Draw sprite if reset is not required
        if not self.reset_is_required_for_image:
            offset_position = self.rect.topleft + offset
            game_surface.blit(self.image, offset_position)

    def move(self):
        pass

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
