import pygame, sys
import settings
from game_state import GameState
from level import Level
from dashboard import Dashboard


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Dungeons and traps')

        # Main - screen surface
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        # Game surface
        self.game_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT - settings.DASHBOARD_HEIGHT))
        # Dashboard surface
        self.dashboard_surface = pygame.Surface((settings.WIDTH, settings.DASHBOARD_HEIGHT))

        self.clock = pygame.time.Clock()

        self.game_state = GameState()
        self.level = Level(self.screen, self.game_surface, self.game_state)
        self.dashboard = Dashboard(self.screen, self.dashboard_surface, self.game_state)

        self.refresh_dashboard_surface()

    def refresh_dashboard_surface(self):
        self.dashboard_surface.fill((50, 50, 50))
        self.dashboard.draw()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == settings.GAME_OVER_EVENT:
                    # Game over - show the end panel
                    self.level.game_over()
                if event.type == settings.ADD_DIAMOND_EVENT:
                    # Refresh dashboard surface
                    self.refresh_dashboard_surface()
                if event.type == settings.DECREASE_ENERGY_EVENT:
                    # Refresh dashboard surface
                    self.refresh_dashboard_surface()

            if not self.game_state.game_over:
                # Refresh game surface
                self.level.run()

            pygame.display.update()
            self.clock.tick(settings.FPS)


if __name__ == '__main__':
    # Initialize and run the game
    game = Game()
    game.run()
