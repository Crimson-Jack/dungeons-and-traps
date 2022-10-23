import pygame
import settings


class Player(pygame.sprite.Sprite):
    def __init__(self, image, position, groups, obstacle_sprites, collectable_sprites, enemy_sprites, game_state):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(-5, -5)

        # Create movement variables
        self.direction = pygame.math.Vector2()
        self.speed = 7

        # Create groups of collision
        self.obstacle_sprites = obstacle_sprites
        self.collectable_sprites = collectable_sprites
        self.enemy_sprites = enemy_sprites

        # Set game state
        self.game_state = game_state

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

        # Set the movement offset and check the collision
        self.hitbox.x += self.direction.x * self.speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * self.speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
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
                self.game_state.decrease_energy()

        # Check collision with obstacle sprites
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def update(self):
        self.input()
        self.move()