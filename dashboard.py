import pygame
import settings


class Dashboard:
    def __init__(self, screen, dashboard_surface):
        self.screen = screen
        self.dashboard_surface = dashboard_surface
        self.accent_color = (155, 155, 155)
        self.basic_font = pygame.font.Font('freesansbold.ttf', 22)

    def draw(self):
        game_name = self.basic_font.render('Dashboard of Dungeons and traps: diamonds, points, stamina ...', True, self.accent_color)
        self.dashboard_surface.blit(game_name, (50, 50))

        self.screen.blit(self.dashboard_surface, (0, settings.HEIGHT - settings.DASHBOARD_HEIGHT))
