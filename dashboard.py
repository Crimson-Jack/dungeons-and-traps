import pygame
import settings
from bar import Bar
from color_set import ColorSet


class Dashboard:
    def __init__(self, screen, dashboard_surface, game_state):
        self.screen = screen
        self.dashboard_surface = dashboard_surface
        self.game_state = game_state

        self.accent_color = (155, 155, 155)
        self.basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 18)
        self.margin = 20

        # Create energy bar
        bar_width = settings.WIDTH - 2 * self.margin
        bar_height = 25
        bar_left = self.margin
        bar_top = 3 * self.margin
        bar_colors = ColorSet([
                ((0, 20), (102, 0, 0)),     # Red
                ((21, 40), (102, 51, 0)),   # Dark orange
                ((41, 60), (102, 102, 0)),  # Rotten green
                ((61, 80), (51, 102, 0)),   # Light green
                ((81, 100), (0, 51, 0))     # Dark green
            ])
        self.energy_bar = Bar((bar_left, bar_top), bar_width, bar_height, self.game_state.max_energy,
                              bar_colors, True, (135, 135, 135), False, None, True, 'Energy', (180, 180, 180))

    def draw(self):
        # Diamonds
        diamonds_counter_text = self.basic_font.render(
            f'Diamonds {self.game_state.diamonds} ({self.game_state.required_diamonds})', True, self.accent_color)
        self.dashboard_surface.blit(diamonds_counter_text, (self.margin, self.margin))

        # Energy bar
        self.energy_bar.draw(self.dashboard_surface, self.game_state.energy)

        # Blit dashboard to the main screen
        self.screen.blit(self.dashboard_surface, (0, settings.HEIGHT - settings.DASHBOARD_HEIGHT))
