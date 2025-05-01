import pygame


class ItemToCollect(pygame.sprite.Sprite):
    def __init__(self, groups, game_state):
        super().__init__(*groups)
        self.game_state = game_state

    def collect(self):
        pass
