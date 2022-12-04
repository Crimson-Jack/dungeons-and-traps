import pygame


class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, animation_row, animation_step, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((animation_step * width), (animation_row * height), width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(colour)

        return image
