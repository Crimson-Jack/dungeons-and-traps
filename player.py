import pygame
import settings
import game_helper
from custom_draw_sprite import CustomDrawSprite


class Player(CustomDrawSprite):
    def __init__(self, image, position, groups, obstacle_sprites, collectable_sprites, enemy_sprites, game_state):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE * 0.9, settings.TILE_SIZE * 0.9))
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(game_helper.calculate_ratio(-5), 0)

        # Create movement variables
        self.direction = pygame.math.Vector2()
        self.speed = game_helper.calculate_ratio(7)

        # Real position is required to store the real distance, which is then casted to integer
        self.real_x_position = float(self.hitbox.x)
        self.real_y_position = float(self.hitbox.y)

        # Create groups of collision
        self.obstacle_sprites = obstacle_sprites
        self.collectable_sprites = collectable_sprites
        self.enemy_sprites = enemy_sprites

        # Set game state
        self.game_state = game_state

        # Player state variables
        self.collided_with_enemy = False

    def input(self):
        # Read pressed key and specify movement direction
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self):
        # Normalize vector
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Calculate real y position
        self.real_x_position += float(self.direction.x * self.speed)
        self.real_y_position += float(self.direction.y * self.speed)

        # Cast real position to integer and check the collision
        self.hitbox.x = int(self.real_x_position)
        self.collision('horizontal')
        self.hitbox.y = int(self.real_y_position)
        self.collision('vertical')
        # Set the movement offset
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        self.collided_with_enemy = False

        # Check collision with collectable sprites
        for sprite in self.collectable_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                # Increase number of collected diamonds
                self.game_state.add_diamond()
                # Remove diamond
                sprite.kill()

        # Check collision with enemy sprites
        for sprite in self.enemy_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                self.collided_with_enemy = True
                self.game_state.decrease_energy()

        # Check collision with obstacle sprites
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.real_x_position = float(self.hitbox.x)
                    self.real_y_position = float(self.hitbox.y)
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.real_x_position = float(self.hitbox.x)
                    self.real_y_position = float(self.hitbox.y)

    def update(self):
        self.input()
        self.move()

    def custom_draw(self, game_surface, offset):
        # Draw glow effect when player is collided with an enemy
        if self.collided_with_enemy:
            position = pygame.Vector2(self.rect.center) + offset
            pygame.draw.circle(game_surface, (255, 0, 0), position, settings.TILE_SIZE // 1.45)
            pygame.draw.circle(game_surface, (255, 100, 0), position, settings.TILE_SIZE // 1.55)
            pygame.draw.circle(game_surface, (255, 150, 0), position, settings.TILE_SIZE // 1.8)
            pygame.draw.circle(game_surface, (255, 200, 0), position, settings.TILE_SIZE // 2.2)
