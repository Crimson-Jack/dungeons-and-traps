import pygame
import random


class ParticleSpark:
    def __init__(self, base_position, color):
        self.base_position = base_position
        self.color = color
        self.position = list(self.base_position)
        self.radius = 10
        self.radius_reduction_value = 0.25
        self.counter = 0
        self.direction_x = random.randint(-1, 1)
        self.direction_y = random.randint(-1, 1)

    def update_position(self, map_offset):
        self.position[0] = self.base_position[0] + map_offset.x
        self.position[1] = self.base_position[1] + map_offset.y

    def move(self):
        self.position[0] += (self.direction_x * self.counter)
        self.position[1] += (self.direction_y * self.counter)
        self.radius -= self.radius_reduction_value
        self.counter += 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, int(self.radius))

    def is_expired(self):
        return self.radius <= 0
