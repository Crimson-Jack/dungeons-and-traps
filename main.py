import pygame, sys
from settings import *
from level import Level
from dashboard import Dashboard


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Dungeons and traps')

        # Main - screen surface
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # Game surface
        self.game_surface = pygame.Surface((WIDTH, HEIGHT - DASHBOARD_HEIGHT))
        # Dashboard surface
        self.dashboard_surface = pygame.Surface((WIDTH, DASHBOARD_HEIGHT))

        self.clock = pygame.time.Clock()

        self.level = Level(self.screen, self.game_surface)
        self.dashboard = Dashboard(self.screen, self.dashboard_surface)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((0, 0, 0))
            self.game_surface.fill((234, 165, 108))
            self.dashboard_surface.fill((50, 50, 50))
            self.dashboard.draw()
            self.level.run()

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()