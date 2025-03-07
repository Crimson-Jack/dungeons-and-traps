import pygame


class CustomDrawSprite(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(*groups)

    def custom_draw(self, game_surface, offset):
        pass
