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
        self.dashboard.clean()
        self.dashboard.draw()

    def run(self):
        is_running = True
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    is_running = False
                # Player movement direction
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.game_state.set_player_movement(0, 1)
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.game_state.set_player_movement(0, -1)
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.game_state.set_player_movement(1, 0)
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.game_state.set_player_movement(-1, 0)
                    if event.key == pygame.K_LCTRL or event.key == pygame.K_LSHIFT:
                        self.game_state.set_player_is_using_weapon(True)
                    if event.key == pygame.K_x:
                        self.game_state.set_next_weapon()
                    if event.key == pygame.K_z:
                        self.game_state.set_previous_weapon()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.game_state.set_player_movement(0, -1)
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.game_state.set_player_movement(0, 1)
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.game_state.set_player_movement(-1, 0)
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.game_state.set_player_movement(1, 0)

                #  Custom events
                if event.type == settings.COLLECT_DIAMOND_EVENT:
                    # Refresh dashboard surface
                    self.refresh_dashboard_surface()
                if event.type == settings.COLLECT_KEY_EVENT:
                    # Refresh dashboard surface
                    self.refresh_dashboard_surface()
                if event.type == settings.DECREASE_ENERGY_EVENT:
                    # Refresh dashboard surface
                    self.refresh_dashboard_surface()
                if event.type == settings.CHANGE_POWER_EVENT:
                    # Refresh dashboard surface
                    self.refresh_dashboard_surface()
                if event.type == settings.EXIT_POINT_IS_OPEN_EVENT:
                    # Show exit point
                    self.level.show_exit_point()
                if event.type == settings.NEXT_LEVEL_EVENT:
                    # Next level - go to the next level
                    self.level.next_level()
                if event.type == settings.GAME_OVER_EVENT:
                    # Game over - show the end panel
                    self.level.game_over()
                if event.type == settings.REFRESH_OBSTACLE_MAP_EVENT:
                    # Refresh obstacle map after modification
                    self.level.refresh_obstacle_map()
                if event.type == settings.PLAYER_TILE_POSITION_CHANGED_EVENT:
                    # Inform about the change of player tile position
                    self.level.inform_about_player_tile_position()
                if event.type == settings.PLAYER_IS_NOT_USING_WEAPON_EVENT:
                    # Weapon is not used
                    self.game_state.set_player_is_using_weapon(False)
                if event.type == settings.SHOW_TOMBSTONE_EVENT:
                    # Show tombstone
                    self.level.show_tombstone(event.dict.get("position"))

            if not self.game_state.game_over:
                # Refresh game surface
                self.level.run()

            pygame.display.update()
            self.clock.tick(settings.FPS)


if __name__ == '__main__':
    # Initialize and run the game
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
