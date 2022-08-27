import pygame
import settings


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, collectable_sprites):
        super().__init__(groups)
        image = pygame.image.load('img/tile_0097.png').convert_alpha()
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -5)

        # Create movement variables
        self.direction = pygame.math.Vector2()
        self.speed = 7

        # Create groups of collision
        self.obstacle_sprites = obstacle_sprites
        self.collectable_sprites = collectable_sprites

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

    def move(self, speed):
        # Normalize vector
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Set the movement offset and check the collision
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        # Check collision with collectable sprites
        for sprite in self.collectable_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                sprite.kill()
                print("Diamond collected")

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
        self.move(self.speed)