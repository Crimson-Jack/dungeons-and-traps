import pygame
import settings


class GameState:
    def __init__(self):
        self.game_over = False
        self.required_diamonds = 0
        self.diamonds = 0
        self.max_energy_value = 800
        self.energy = self.max_energy_value

    def set_number_of_required_diamonds(self, value):
        self.required_diamonds = value

    def add_diamond(self):
        self.diamonds += 1
        pygame.event.post(pygame.event.Event(settings.ADD_DIAMOND_EVENT))
        if self.diamonds == self.required_diamonds:
            pygame.event.post(pygame.event.Event(settings.EXIT_POINT_IS_OPEN_EVENT))

    def decrease_energy(self):
        self.energy -= 1
        if self.energy < 0:
            self.energy = 0
            self.game_over = True
            pygame.event.post(pygame.event.Event(settings.GAME_OVER_EVENT))
        else:
            pygame.event.post(pygame.event.Event(settings.DECREASE_ENERGY_EVENT))

    def level_completed(self):
        if self.diamonds == self.required_diamonds:
            # NOTE: Only for temporary solution
            self.game_over = True
            pygame.event.post(pygame.event.Event(settings.NEXT_LEVEL_EVENT))
