import pygame
import settings
from enemy import Enemy


class GhostEnemy(Enemy):
    def __init__(self, position, groups, obstacle_map):
        super().__init__(groups)
        image = pygame.image.load('img/tile_0121.png').convert_alpha()
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(0, 0)

        # Set obstacle map
        self.obstacle_map = obstacle_map

        # Create movement variables
        self.direction = pygame.math.Vector2((1, 0))
        self.speed = 1
        self.current_position_on_map = [(self.rect.right // settings.TILE_SIZE) - 1, (self.rect.bottom // settings.TILE_SIZE) - 1]
        self.new_position_on_map = [(self.rect.right // settings.TILE_SIZE) - 1, (self.rect.bottom // settings.TILE_SIZE) - 1]

    def determine_direction(self, x_tile_number, y_tile_number):
        # TODO: Add a logic
        if self.direction.x > 0:
            if self.obstacle_map[y_tile_number][x_tile_number+1]:
                self.direction.x = 0
                self.direction.y = 1
                print('A')

        elif self.direction.y > 0:
            if self.obstacle_map[y_tile_number+1][x_tile_number]:
                self.direction.x = -1
                self.direction.y = 0
                print('B')

        elif self.direction.x < 0:
            if self.obstacle_map[y_tile_number][x_tile_number-1]:
                self.direction.x = 0
                self.direction.y = -1
                print('C')

        elif self.direction.y < 0:
            if self.obstacle_map[y_tile_number-1][x_tile_number]:
                self.direction.x = 1
                self.direction.y = 0
                print('D')

    def move(self):
        # Set the movement offset
        self.hitbox.x += self.direction.x * self.speed
        self.hitbox.y += self.direction.y * self.speed
        self.rect.center = self.hitbox.center

        if self.rect.right % settings.TILE_SIZE == 0:
            self.new_position_on_map[0] = (self.rect.right // settings.TILE_SIZE) - 1

        if self.rect.bottom % settings.TILE_SIZE == 0:
            self.new_position_on_map[1] = (self.rect.bottom // settings.TILE_SIZE) - 1

        if self.current_position_on_map != self.new_position_on_map:
            if self.current_position_on_map[0] != self.new_position_on_map[0]:
                self.current_position_on_map[0] = self.new_position_on_map[0]
            if self.current_position_on_map[1] != self.new_position_on_map[1]:
                self.current_position_on_map[1] = self.new_position_on_map[1]

            print(f'x={self.current_position_on_map[0]}')
            print(f'y={self.current_position_on_map[1]}')

            self.determine_direction(self.current_position_on_map[0], self.current_position_on_map[1])

    def update(self):
        self.move()

    def custom_draw(self, game_surface, offset):
        pass

