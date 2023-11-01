import pygame
import diamond
import game_helper
import settings
from bar import Bar
from color_set import ColorSet


class Dashboard:
    def __init__(self, screen, dashboard_surface, game_state):
        self.screen = screen
        self.dashboard_surface = dashboard_surface
        self.game_state = game_state

        # Fonts
        self.accent_color = (187, 187, 204)
        self.basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 32)
        self.margin = 16

        # Background and border
        self.border = self.dashboard_surface.get_rect()
        self.border = self.border.inflate(-8, -8)
        self.dashboard_surface.fill((64, 78, 107))
        pygame.draw.rect(self.dashboard_surface, (42, 53, 70), self.border)
        pygame.draw.rect(self.dashboard_surface, (244, 244, 244), self.border, 4)
        self.inner_background_color = 42, 53, 70

        # Surfaces
        self.left_top_surface = pygame.Surface(
            (settings.WIDTH // 2 - self.margin, settings.DASHBOARD_HEIGHT // 2 - self.margin // 2))
        self.right_top_surface = pygame.Surface(
            (settings.WIDTH // 2 - self.margin, settings.DASHBOARD_HEIGHT // 2 - self.margin // 2))
        self.left_bottom_surface = pygame.Surface(
            (settings.WIDTH // 2 - self.margin, settings.DASHBOARD_HEIGHT // 2 - self.margin // 2))
        self.right_bottom_surface = pygame.Surface(
            (settings.WIDTH // 2 - self.margin, settings.DASHBOARD_HEIGHT // 2 - self.margin // 2))

        # Energy bar
        self.energy_bar_margin = 20
        bar_width = self.right_top_surface.get_width() - 2 * self.energy_bar_margin
        bar_height = 25
        bar_left = self.energy_bar_margin
        bar_top = self.right_top_surface.get_height() // 2 - (bar_height // 2)
        bar_colors = ColorSet([
                ((0, 20), (255, 60, 0)),        # Red
                ((21, 40), (255, 158, 87)),     # Dark orange
                ((41, 60), (243, 244, 180)),    # Rotten green
                ((61, 80), (189, 244, 180)),    # Light green
                ((81, 100), (122, 231, 104))    # Dark green
            ])
        self.energy_bar = Bar((bar_left, bar_top), bar_width, bar_height, self.game_state.max_energy,
                              bar_colors, True, (167, 185, 194), True,
                              (33, 59, 99), True, 'Energy', (33, 59, 99))

    def clean(self):
        self.left_top_surface.fill(self.inner_background_color)
        self.right_top_surface.fill(self.inner_background_color)
        self.left_bottom_surface.fill(self.inner_background_color)
        self.right_bottom_surface.fill(self.inner_background_color)

    def draw(self):
        # Left top
        lives_counter_text = self.basic_font.render(
            f'Lives', True, self.accent_color)
        self.left_top_surface.blit(lives_counter_text, (self.margin, self.right_bottom_surface.get_height() // 2 - lives_counter_text.get_rect().height // 2))
        self.dashboard_surface.blit(self.left_top_surface, (settings.WIDTH // 2 + self.margin // 2,
                                                            settings.DASHBOARD_HEIGHT // 2))
        self.dashboard_surface.blit(self.left_top_surface, (self.margin // 2, self.margin // 2))

        # Right top
        self.energy_bar.draw(self.right_top_surface, self.game_state.energy)
        self.dashboard_surface.blit(self.right_top_surface, (settings.WIDTH // 2 + self.margin // 2, self.margin // 2))

        # Left bottom
        keys_counter_text = self.basic_font.render(
            f'Keys', True, self.accent_color)
        self.left_bottom_surface.blit(keys_counter_text, (self.margin, self.right_bottom_surface.get_height() // 2 - keys_counter_text.get_rect().height // 2))
        self.dashboard_surface.blit(self.left_bottom_surface, (settings.WIDTH // 2 + self.margin // 2,
                                                               settings.DASHBOARD_HEIGHT // 2))
        self.dashboard_surface.blit(self.left_bottom_surface,
                                    (self.margin // 2, settings.DASHBOARD_HEIGHT // 2))

        # Right bottom
        diamonds_counter_text = self.basic_font.render(
            f'Diamonds', True, self.accent_color)
        self.right_bottom_surface.blit(diamonds_counter_text, (self.margin, self.right_bottom_surface.get_height() // 2 - diamonds_counter_text.get_rect().height // 2))

        count = 0
        for item in self.game_state.diamonds:
            if item.alive():
                # Copy sprite for dashboard - semi transparent
                transparent_image = diamond.Diamond(item.image, item.rect.topleft, list())
                transparent_image.image.set_alpha(100)
                self.right_bottom_surface.blit(transparent_image.image, (self.margin * 2 + diamonds_counter_text.get_width() + (count * game_helper.BASE_TILE_SIZE), 0))
            else:
                # Use original sprite
                self.right_bottom_surface.blit(item.image, (self.margin * 2 + diamonds_counter_text.get_width() + (count * game_helper.BASE_TILE_SIZE), 0))
            count += 1

        self.dashboard_surface.blit(self.right_bottom_surface, (settings.WIDTH // 2 + self.margin // 2,
                                                                settings.DASHBOARD_HEIGHT // 2))

        # Blit dashboard to the main screen
        self.screen.blit(self.dashboard_surface, (0, settings.HEIGHT - settings.DASHBOARD_HEIGHT))
