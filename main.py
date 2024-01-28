import pygame, sys
import settings
from game_state import GameState
from level import Level
from dashboard import Dashboard


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Dungeons and traps')

        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.game_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT - settings.DASHBOARD_HEIGHT))
        self.dashboard_surface = pygame.Surface((settings.WIDTH, settings.DASHBOARD_HEIGHT))

        self.game_state = GameState()

        self.level = Level(self.screen, self.game_surface, self.game_state)
        self.dashboard = Dashboard(self.screen, self.dashboard_surface, self.game_state)
        self.refresh_dashboard_surface()

        self.clock = pygame.time.Clock()

    def refresh_dashboard_surface(self):
        self.dashboard.clean()
        self.dashboard.draw()

    def run(self):
        pygame.time.set_timer(settings.PARTICLE_EVENT, 40)

        is_running = True
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    is_running = False
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
                if event.type == settings.COLLECT_DIAMOND_EVENT:
                    self.refresh_dashboard_surface()
                if event.type == settings.COLLECT_KEY_EVENT:
                    self.refresh_dashboard_surface()
                if event.type == settings.DECREASE_ENERGY_EVENT:
                    self.refresh_dashboard_surface()
                if event.type == settings.CHANGE_POWER_EVENT:
                    self.refresh_dashboard_surface()
                if event.type == settings.EXIT_POINT_IS_OPEN_EVENT:
                    self.level.show_exit_point()
                if event.type == settings.NEXT_LEVEL_EVENT:
                    self.level.next_level()
                if event.type == settings.GAME_OVER_EVENT:
                    self.level.game_over()
                if event.type == settings.REFRESH_OBSTACLE_MAP_EVENT:
                    self.level.refresh_obstacle_map()
                if event.type == settings.PLAYER_TILE_POSITION_CHANGED_EVENT:
                    self.level.inform_about_player_tile_position()
                if event.type == settings.PLAYER_IS_NOT_USING_WEAPON_EVENT:
                    self.game_state.set_player_is_using_weapon(False)
                if event.type == settings.ADD_TOMBSTONE_EVENT:
                    self.level.add_tombstone(event.dict.get("position"))
                if event.type == settings.ADD_PARTICLE_EFFECT_EVENT:
                    self.level.add_particle_effect(event.dict.get("position"),
                                                   event.dict.get("number_of_sparks"),
                                                   event.dict.get("colors"))
                if event.type == settings.PARTICLE_EVENT:
                    self.level.add_spark_to_particle_effect()

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
