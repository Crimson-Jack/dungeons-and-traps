import pygame
import settings
import bar


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
        self.energy_bar = bar.Bar(dashboard_surface, (bar_left, bar_top), bar_width, bar_height,
                                  self.game_state.max_energy, 'Energy')
        # Create power bar
        bar_width = settings.WIDTH // 2 - 2 * self.margin
        bar_height = 25
        bar_top = 5 * self.margin
        self.power_bar = bar.Bar(dashboard_surface, (bar_left, bar_top), bar_width, bar_height,
                                 self.game_state.max_power, None, (102, 51, 0))

    def draw(self):
        # Diamonds
        diamonds_counter_text = self.basic_font.render(f'Diamonds {self.game_state.diamonds} ({self.game_state.required_diamonds})', True, self.accent_color)
        self.dashboard_surface.blit(diamonds_counter_text, (self.margin, self.margin))

        # Energy bar
        self.energy_bar.draw(self.game_state.energy)

        # Power bar
        self.power_bar.draw(self.game_state.power)

        # Blit dashboard to the main screen
        self.screen.blit(self.dashboard_surface, (0, settings.HEIGHT - settings.DASHBOARD_HEIGHT))
