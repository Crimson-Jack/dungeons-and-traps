import pygame
import random


class ParticleSpark:
    def __init__(self, position, color):
        self.position = position
        self.color = color
        self.radius = 10
        self.radius_reduction_value = 0.25
        self.direction_x = random.randint(-1, 1)
        self.direction_y = random.randint(-1, 1)

    def move(self):
        self.position[0] += self.direction_x
        self.position[1] += self.direction_y
        self.radius -= self.radius_reduction_value

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, int(self.radius))

    def is_expired(self):
        return self.radius <= 0
