import pygame
import settings
from enemy import Enemy


class SpiderEnemy(Enemy):
    def __init__(self, image, position, groups, speed, net_length):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(0, 0)

        # Create movement variables
        self.direction = pygame.math.Vector2((0, 1))
        self.speed = speed
        self.min_y_position = self.rect.topleft[1]
        self.max_net_length = settings.TILE_SIZE * net_length

    def move(self):
        # Set the movement offset
        self.hitbox.y += self.direction.y * self.speed
        if self.hitbox.y > self.min_y_position + self.max_net_length:
            self.direction.y = self.direction.y * -1
        if self.hitbox.y < self.min_y_position:
            self.direction.y = self.direction.y * -1
        self.rect.center = self.hitbox.center

    def update(self):
        self.move()

    def custom_draw(self, game_surface, offset):
        # Draw a net (line) from the beginning to the end spider position
        start_position = pygame.Vector2((self.rect.center[0], self.min_y_position)) + offset
        end_position = pygame.Vector2(self.rect.center) + offset
        pygame.draw.line(game_surface, (215, 215, 215), start_position, end_position, 2)




