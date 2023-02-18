import pygame
import direction
import settings
import game_helper
import spritesheet
from custom_draw_sprite import CustomDrawSprite


class Player(CustomDrawSprite):
    def __init__(self, image, position, groups, speed, exit_points, obstacle_sprites,
                 moving_obstacle_sprites, collectable_sprites, enemy_sprites, game_state):
        super().__init__(groups)

        # Create sprite animation variables
        self.costume_switching_threshold = 5
        self.number_of_sprites = 4
        self.step_counter = 0
        self.costume_index = 0
        self.sprites = {
            'left': [],
            'right': [],
            'up': [],
            'down': [],
            'right_down': [],
            'left_down': [],
            'left_up': [],
            'right_up': []}
        self.load_all_sprites(16, 16, (int(settings.TILE_SIZE), int(settings.TILE_SIZE)), (0, 0, 0))

        # Player image
        self.image = self.sprites['right'][0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(game_helper.calculate_ratio(-5), 0)

        # Create movement variables
        self.is_moving = False
        self.movement_vector = pygame.math.Vector2()
        self.movement_direction = direction.Direction.RIGHT
        self.previous_movement_direction = direction.Direction.RIGHT
        self.speed = speed

        # Real position is required to store the real distance, which is then cast to integer
        self.real_x_position = float(self.hit_box.x)
        self.real_y_position = float(self.hit_box.y)

        # Create groups of collision
        self.exit_points = exit_points
        self.moving_obstacle_sprites = moving_obstacle_sprites
        self.obstacle_sprites = obstacle_sprites
        self.collectable_sprites = collectable_sprites
        self.enemy_sprites = enemy_sprites

        # Set game state
        self.game_state = game_state

        # Player state variables
        self.collided_with_enemy = False

    def load_all_sprites(self, source_sprite_width, source_sprite_height, scale, key_color):
        # Load image with all sprite sheets
        sprite_sheet = spritesheet.SpriteSheet(
            pygame.image.load('img/player.png').convert_alpha(),
            source_sprite_width,
            source_sprite_height,
            scale,
            key_color
        )

        # Sprites with the state: standing
        self.sprites['right'].append(sprite_sheet.get_image(0, 0))
        self.sprites['left'].append(sprite_sheet.get_image(2, 0))
        self.sprites['up'].append(sprite_sheet.get_image(4, 0))
        self.sprites['down'].append(sprite_sheet.get_image(6, 0))
        self.sprites['right_down'].append(sprite_sheet.get_image(6, 0))
        self.sprites['right_up'].append(sprite_sheet.get_image(4, 0))
        self.sprites['left_down'].append(sprite_sheet.get_image(6, 0))
        self.sprites['left_up'].append(sprite_sheet.get_image(4, 0))

        # Sprites with the state: walking
        for number in range(0, self.number_of_sprites):
            self.sprites['right'].append(sprite_sheet.get_image(1, number))
            self.sprites['left'].append(sprite_sheet.get_image(3, number))
            self.sprites['up'].append(sprite_sheet.get_image(5, number))
            self.sprites['down'].append(sprite_sheet.get_image(7, number))
            self.sprites['right_down'].append(sprite_sheet.get_image(7, number))
            self.sprites['right_up'].append(sprite_sheet.get_image(5, number))
            self.sprites['left_down'].append(sprite_sheet.get_image(7, number))
            self.sprites['left_up'].append(sprite_sheet.get_image(5, number))

    def input(self):
        self.movement_vector = self.game_state.player_movement_vector
        self.movement_direction = self.game_state.player_movement_direction

    def set_costume(self, current_direction, index):
        # Select appropriate costume for sprite
        if current_direction == direction.Direction.RIGHT:
            self.image = self.sprites['right'][index]
        elif current_direction == direction.Direction.LEFT:
            self.image = self.sprites['left'][index]
        elif current_direction == direction.Direction.UP:
            self.image = self.sprites['up'][index]
        elif current_direction == direction.Direction.DOWN:
            self.image = self.sprites['down'][index]
        elif current_direction == direction.Direction.RIGHT_UP:
            self.image = self.sprites['right_up'][index]
        elif current_direction == direction.Direction.RIGHT_DOWN:
            self.image = self.sprites['right_down'][index]
        elif current_direction == direction.Direction.LEFT_UP:
            self.image = self.sprites['left_up'][index]
        elif current_direction == direction.Direction.LEFT_DOWN:
            self.image = self.sprites['left_down'][index]

    def reset_costume(self):
        # Reset counter and costume index
        self.step_counter = 0
        self.costume_index = 0

        # Set image based on direction and costume index
        self.set_costume(self.movement_direction, self.costume_index)

    def change_costume(self):
        if self.is_moving:
            # Change costume only if threshold exceeded
            if self.step_counter > self.costume_switching_threshold:
                # Reset counter and increase costume index
                self.step_counter = 0
                self.costume_index += 1

                # If it's the last costume - start from the second costume (index = 1)
                if self.costume_index > self.number_of_sprites:
                    self.costume_index = 1

                # Set image based on direction and costume index
                self.set_costume(self.movement_direction, self.costume_index)

            # The player's move is complete
            self.is_moving = False
        else:
            # Player is not moving
            # Reset costume if the time elapsed: 2 * threshold
            if self.step_counter > self.costume_switching_threshold * 2:
                # Reset counter and costume index
                self.step_counter = 0
                self.costume_index = 0

                # Set image based on direction and costume index
                self.set_costume(self.previous_movement_direction, self.costume_index)

    def move(self):
        # Normalize vector
        if self.movement_vector.magnitude() != 0:
            self.movement_vector = self.movement_vector.normalize()

        # Calculate real y position
        self.real_x_position += float(self.movement_vector.x * self.speed)
        self.real_y_position += float(self.movement_vector.y * self.speed)

        # Cast real position to integer and check the collision
        self.hit_box.x = int(self.real_x_position)
        self.collision('horizontal')
        self.hit_box.y = int(self.real_y_position)
        self.collision('vertical')

        # Check the movement
        if self.rect.center != self.hit_box.center:

            # If direction was changed - set the first costume
            if self.movement_direction != self.previous_movement_direction:
                self.reset_costume()

            # Set the movement offset
            self.rect.center = self.hit_box.center

            # Player is moving
            self.is_moving = True

            # Save previous direction
            self.previous_movement_direction = self.movement_direction

        # Increase step counter
        self.step_counter += 1

    def collision(self, direction):
        self.collided_with_enemy = False

        # Check collision with exit points
        for sprite in self.exit_points:
            if sprite.hit_box.colliderect(self.hit_box):
                self.game_state.level_completed()

        # Check collision with collectable sprites
        for sprite in self.collectable_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                # Increase number of collected diamonds
                self.game_state.add_diamond()
                # Remove diamond
                sprite.kill()

        # Check collision with enemy sprites
        for sprite in self.enemy_sprites:
            if sprite.hit_box.colliderect(self.hit_box):
                if pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(sprite), False, pygame.sprite.collide_mask):
                    self.collided_with_enemy = True
                    self.game_state.decrease_energy()

        # Check collision with obstacle and moving obstacle sprites
        if direction == 'horizontal':
            # Obstacle
            for sprite in self.obstacle_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if self.movement_vector.x > 0:
                        self.hit_box.right = sprite.hit_box.left
                    if self.movement_vector.x < 0:
                        self.hit_box.left = sprite.hit_box.right
                    # Adjust position after collision
                    self.real_x_position = float(self.hit_box.x)
                    self.real_y_position = float(self.hit_box.y)
            # Moving obstacle
            for sprite in self.moving_obstacle_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if not sprite.move_obstacle_if_allowed(self.movement_direction):
                        # Obstacle has not been moved
                        if self.movement_vector.x > 0:
                            self.hit_box.right = sprite.hit_box.left
                        if self.movement_vector.x < 0:
                            self.hit_box.left = sprite.hit_box.right
                        # Adjust position after collision
                        self.real_x_position = float(self.hit_box.x)
                        self.real_y_position = float(self.hit_box.y)

        if direction == 'vertical':
            # Obstacle
            for sprite in self.obstacle_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if self.movement_vector.y > 0:
                        self.hit_box.bottom = sprite.hit_box.top
                    if self.movement_vector.y < 0:
                        self.hit_box.top = sprite.hit_box.bottom
                    # Adjust position after collision
                    self.real_x_position = float(self.hit_box.x)
                    self.real_y_position = float(self.hit_box.y)
            # Moving obstacle
            for sprite in self.moving_obstacle_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if not sprite.move_obstacle_if_allowed(self.movement_direction):
                        # Obstacle has not been moved
                        if self.movement_vector.y > 0:
                            self.hit_box.bottom = sprite.hit_box.top
                        if self.movement_vector.y < 0:
                            self.hit_box.top = sprite.hit_box.bottom
                        # Adjust position after collision
                        self.real_x_position = float(self.hit_box.x)
                        self.real_y_position = float(self.hit_box.y)

    def update(self):
        self.input()
        self.change_costume()
        self.move()

    def custom_draw(self, game_surface, offset):
        # Draw glow effect when player is collided with an enemy
        if self.collided_with_enemy:
            position = pygame.Vector2(self.rect.center) + offset
            pygame.draw.circle(game_surface, (255, 0, 0), position, settings.TILE_SIZE // 1.45)
            pygame.draw.circle(game_surface, (255, 100, 0), position, settings.TILE_SIZE // 1.55)
            pygame.draw.circle(game_surface, (255, 150, 0), position, settings.TILE_SIZE // 1.8)
            pygame.draw.circle(game_surface, (255, 200, 0), position, settings.TILE_SIZE // 2.2)

        # Draw sprite
        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)
