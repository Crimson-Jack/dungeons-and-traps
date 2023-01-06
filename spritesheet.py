import pygame


class SpriteSheet():
    def __init__(self, image, width, height, scale, key_color):
        self.sheet = image
        self.width = width
        self.height = height
        self.scale = scale
        self.key_color = key_color

    def get_image(self, row, step):
        image = pygame.Surface((self.width, self.height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((step * self.width), (row * self.height), self.width, self.height))
        image = pygame.transform.scale(image, self.scale)
        image.set_colorkey(self.key_color)

        return image
