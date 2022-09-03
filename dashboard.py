import pygame
import settings


class Dashboard:
    def __init__(self, screen, dashboard_surface, game_state):
        self.screen = screen
        self.dashboard_surface = dashboard_surface
        self.accent_color = (155, 155, 155)
        self.basic_font = pygame.font.Font('freesansbold.ttf', 18)

        # Set game state
        self.game_state = game_state

    def draw(self):
        game_name = self.basic_font.render('Dashboard of Dungeons and traps', True, self.accent_color)
        diamonds = self.basic_font.render(f'Diamonds {self.game_state.diamonds}', True, self.accent_color)
        energy = self.basic_font.render(f'Energy {self.game_state.energy}', True, self.accent_color)
        self.dashboard_surface.blit(game_name, (50, 30))
        self.dashboard_surface.blit(diamonds, (50, 50))
        self.dashboard_surface.blit(energy, (50, 70))

        self.screen.blit(self.dashboard_surface, (0, settings.HEIGHT - settings.DASHBOARD_HEIGHT))
