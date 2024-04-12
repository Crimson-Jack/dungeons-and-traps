import pygame, sys
import settings
from game_state import GameState
from level import Level
from header import Header
from dashboard import Dashboard
from message_box import MessageBox
from message import Message


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Dungeons and traps')

        if settings.FULL_SCREEN_MODE:
            # NOTE: full screen mode
            monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
            settings.WIDTH = pygame.display.Info().current_w
            settings.HEIGHT = pygame.display.Info().current_h
            self.screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))

        self.game_surface = pygame.Surface(
            (settings.WIDTH, settings.HEIGHT - settings.HEADER_HEIGHT - settings.DASHBOARD_HEIGHT))
        self.header_surface = pygame.Surface((settings.WIDTH, settings.HEADER_HEIGHT))
        self.dashboard_surface = pygame.Surface((settings.WIDTH, settings.DASHBOARD_HEIGHT))

        self.game_state = GameState()

        self.level = Level(self.screen, self.game_surface, self.game_state)
        self.message_box = None
        self.header = Header(self.screen, self.header_surface, self.game_state)
        self.refresh_header_surface()
        self.dashboard = Dashboard(self.screen, self.dashboard_surface, self.game_state)
        self.refresh_dashboard_surface()

        self.paused = False
        self.level_completed = False

        self.clock = pygame.time.Clock()

    def refresh_header_surface(self):
        self.header.clean()
        self.header.draw()

    def refresh_dashboard_surface(self):
        self.dashboard.clean()
        self.dashboard.draw()

    def run(self):
        pygame.time.set_timer(settings.PARTICLE_EVENT, 40)

        is_running = True
        while is_running:
            for event in pygame.event.get():
                # Input events: keyboard, mouse
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
                    if event.key == pygame.K_SPACE:
                        if not self.level_completed and not self.game_state.game_over:
                            self.paused = not self.paused
                            if self.paused:
                                messages = list()
                                messages.append(Message('PAUSED', settings.HIGHLIGHTED_TEXT_COLOR, 40))
                                messages.append(Message('Press the SPACE button to return to the game', settings.TEXT_COLOR, 20))
                                self.message_box = MessageBox(self.screen, 740, 130, 20, settings.MESSAGE_BACKGROUND_COLOR, settings.MESSAGE_BORDER_COLOR, messages)
                            else:
                                self.message_box = None
                        elif self.level_completed:
                            self.level_completed = False
                            self.message_box = None
                            self.game_state.set_next_level()
                            self.level = Level(self.screen, self.game_surface, self.game_state)
                            self.refresh_header_surface()
                            self.refresh_dashboard_surface()
                        elif self.game_state.game_over:
                            is_running = False

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.game_state.set_player_movement(0, -1)
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.game_state.set_player_movement(0, 1)
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.game_state.set_player_movement(-1, 0)
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.game_state.set_player_movement(1, 0)

                # Custom events
                if event.type == settings.COLLECT_DIAMOND_EVENT:
                    self.refresh_dashboard_surface()

                if event.type == settings.COLLECT_KEY_EVENT:
                    self.refresh_dashboard_surface()

                if event.type == settings.COLLECT_LIFE_EVENT:
                    self.refresh_dashboard_surface()

                if event.type == settings.DECREASE_NUMBER_OF_ARROWS_EVENT:
                    self.refresh_header_surface()

                if event.type == settings.CHANGE_ENERGY_EVENT:
                    self.refresh_dashboard_surface()

                if event.type == settings.CHANGE_POWER_EVENT:
                    self.refresh_dashboard_surface()

                if event.type == settings.CHANGE_WEAPON_EVENT:
                    self.refresh_header_surface()

                if event.type == settings.EXIT_POINT_IS_OPEN_EVENT:
                    self.level.show_exit_point()

                if event.type == settings.NEXT_LEVEL_EVENT:
                    self.level_completed = True
                    messages = list()
                    messages.append(Message('CONGRATULATIONS', settings.HIGHLIGHTED_TEXT_COLOR, 40))
                    messages.append(Message('Level completed', settings.TEXT_COLOR, 20))
                    messages.append(Message('Press the SPACE button to go to the next level', settings.TEXT_COLOR, 16))
                    self.message_box = MessageBox(self.screen, 740, 150, 20, settings.MESSAGE_BACKGROUND_COLOR,
                                                  settings.MESSAGE_BORDER_COLOR, messages)

                if event.type == settings.REFRESH_OBSTACLE_MAP_EVENT:
                    self.level.refresh_obstacle_map()

                if event.type == settings.PLAYER_TILE_POSITION_CHANGED_EVENT:
                    self.level.inform_about_player_tile_position()

                if event.type == settings.PLAYER_IS_NOT_USING_WEAPON_EVENT:
                    self.game_state.set_player_is_using_weapon(False)

                if event.type == settings.ADD_PARTICLE_EFFECT_EVENT:
                    self.level.add_particle_effect(event.dict.get("position"),
                                                   event.dict.get("number_of_sparks"),
                                                   event.dict.get("colors"))

                if event.type == settings.PARTICLE_EVENT:
                    self.level.add_spark_to_particle_effect()

                if event.type == settings.ADD_TOMBSTONE_EVENT:
                    self.level.add_tombstone(event.dict.get("position"))

                if event.type == settings.PLAYER_LOST_LIFE_EVENT:
                    self.level.show_player_tombstone()
                    pygame.time.set_timer(settings.RESPAWN_PLAYER_EVENT, 1500)

                if event.type == settings.RESPAWN_PLAYER_EVENT:
                    pygame.time.set_timer(settings.RESPAWN_PLAYER_EVENT, 0)
                    self.game_state.set_player_max_energy()
                    self.level.respawn_player()
                    self.refresh_dashboard_surface()

                if event.type == settings.GAME_OVER_EVENT:
                    self.level.show_player_tombstone()
                    pygame.time.set_timer(settings.GAME_OVER_SUMMARY_EVENT, 1500)

                if event.type == settings.GAME_OVER_SUMMARY_EVENT:
                    pygame.time.set_timer(settings.GAME_OVER_SUMMARY_EVENT, 0)
                    self.game_state.game_over = True
                    messages = list()
                    messages.append(Message('GAME OVER', settings.HIGHLIGHTED_TEXT_COLOR, 40))
                    self.message_box = MessageBox(self.screen, 800, 100, 20, settings.MESSAGE_BACKGROUND_COLOR,
                                                  settings.MESSAGE_BORDER_COLOR, messages)

            if not self.paused and not self.level_completed and not self.game_state.game_over:
                # Refresh game surface
                self.level.run()
            if self.message_box is not None:
                # Draw message box
                self.message_box.draw()

            pygame.display.update()
            self.clock.tick(settings.FPS)


if __name__ == '__main__':
    # Initialize and run the game
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
