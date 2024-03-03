import pygame
from powerup import Powerup


class BowPowerup(Powerup):
    def __init__(self, image, position, groups, game_state, number_of_arrows):
        super().__init__(image, position, groups, game_state)
        self.number_of_arrows = number_of_arrows

    def activate(self):
        self.game_state.collect_bow_powerup(self.number_of_arrows)
