import pygame
import sys
import settings
from game_state import GameState
from level import Level
from header import Header
from dashboard import Dashboard
from message_box import MessageBox
from message import Message
from first_page import FirstPage
from game_status import GameStatus


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Dungeons and traps')

        if settings.FULL_SCREEN_MODE:
            # Full screen mode
            monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
            settings.WIDTH = pygame.display.Info().current_w
            settings.HEIGHT = pygame.display.Info().current_h
            self.screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
        else:
            # Regular window
            self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))

        # Game surfaces
        game_surface_size = settings.WIDTH, settings.HEIGHT - settings.HEADER_HEIGHT - settings.DASHBOARD_HEIGHT
        header_surface_size = settings.WIDTH, settings.HEADER_HEIGHT
        dashboard_surface_size = settings.WIDTH, settings.DASHBOARD_HEIGHT
        self.game_surface = pygame.Surface(game_surface_size)
        self.header_surface = pygame.Surface(header_surface_size)
        self.dashboard_surface = pygame.Surface(dashboard_surface_size)

        # Game states
        self.game_state = GameState()

        # Game components
        self.level = Level(self.screen, self.game_surface, self.game_state)
        self.header = Header(self.screen, self.header_surface, self.game_state)
        self.dashboard = Dashboard(self.screen, self.dashboard_surface, self.game_state)

        # First page and message dialog
        self.first_page = None
        self.message_dialog = None

        # Select startup mode and load first page
        self.game_state.set_first_page()
        self.clean_screen()
        self.load_first_page()

        self.clock = pygame.time.Clock()

    def clean_screen(self):
        self.screen.fill(settings.GAME_BACKGROUND_COLOR)

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
                if event.type == pygame.QUIT:
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
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state.game_status == GameStatus.FIRST_PAGE:
                            # Exit and stop the game
                            is_running = False
                        elif self.game_state.game_status == GameStatus.GAME_IS_RUNNING:
                            # Open options dialog and pause the game
                            self.game_state.switch_escape_state()
                            self.load_game_options_message_dialog()
                        elif self.game_state.game_status == GameStatus.OPTIONS:
                            # Close options dialog and continue the game
                            self.dispose_message_dialog()
                            self.game_state.switch_escape_state()
                    if event.key == pygame.K_F5:
                        if self.game_state.game_status == GameStatus.FIRST_PAGE:
                            # Close first page and start next level
                            self.dispose_first_page()
                            self.game_state.set_next_level()
                            self.load_next_level_message_dialog()
                        elif self.game_state.game_status == GameStatus.OPTIONS:
                            # Close options dialog and restart level or call game over summary dialog
                            self.dispose_message_dialog()
                            self.game_state.decrease_number_of_lives()
                            if self.game_state.lives > 0:
                                self.game_state.clear_settings_for_current_level()
                                self.level = Level(self.screen, self.game_surface, self.game_state)
                                self.game_state.set_next_level()
                                self.load_next_level_message_dialog()
                            else:
                                self.game_state.set_game_is_running()
                                pygame.event.post(pygame.event.Event(settings.GAME_OVER_SUMMARY_EVENT))
                    if event.key == pygame.K_F7:
                        if self.game_state.game_status == GameStatus.OPTIONS:
                            # Close options dialog and quit the game
                            self.dispose_message_dialog()
                            self.game_state.clear_settings_for_first_level()
                            self.level = Level(self.screen, self.game_surface, self.game_state)
                            self.game_state.set_first_page()
                            self.clean_screen()
                            self.load_first_page()
                    if event.key == pygame.K_SPACE:
                        if self.game_state.game_status == GameStatus.GAME_IS_RUNNING:
                            # Open pause dialog and pause the game
                            self.game_state.switch_pause_state()
                            self.load_game_paused_message_dialog()
                        elif self.game_state.game_status == GameStatus.GAME_IS_PAUSED:
                            # Close pause dialog and continue the game
                            self.dispose_message_dialog()
                            self.game_state.switch_pause_state()
                        elif self.game_state.game_status == GameStatus.NEXT_LEVEL:
                            # Close next level dialog and continue the game
                            self.dispose_message_dialog()
                            self.game_state.set_game_is_running()
                            self.clean_screen()
                            self.refresh_header_surface()
                            self.refresh_dashboard_surface()
                        elif self.game_state.game_status == GameStatus.LEVEL_COMPLETED:
                            # Close level completed dialog, load next level and open next level dialog
                            self.dispose_message_dialog()
                            self.game_state.clear_settings_for_next_level()
                            self.level = Level(self.screen, self.game_surface, self.game_state)
                            self.game_state.set_next_level()
                            self.load_next_level_message_dialog()
                        elif self.game_state.game_status == GameStatus.GAME_OVER:
                            # Close game over dialog, load first level and open first page
                            self.dispose_message_dialog()
                            self.game_state.clear_settings_for_first_level()
                            self.level = Level(self.screen, self.game_surface, self.game_state)
                            self.game_state.set_first_page()
                            self.clean_screen()
                            self.load_first_page()

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
                if event.type == settings.CHANGE_SCORE_EVENT:
                    self.refresh_header_surface()

                if event.type == settings.COLLECT_DIAMOND_EVENT:
                    self.refresh_header_surface()
                    self.refresh_dashboard_surface()

                if event.type == settings.COLLECT_KEY_EVENT:
                    self.refresh_header_surface()
                    self.refresh_dashboard_surface()

                if event.type == settings.COLLECT_LIFE_EVENT:
                    self.refresh_dashboard_surface()

                if event.type == settings.CHANGE_WEAPON_CAPACITY_EVENT:
                    self.refresh_header_surface()

                if event.type == settings.CHANGE_ENERGY_EVENT:
                    self.refresh_dashboard_surface()

                if event.type == settings.CHANGE_WEAPON_EVENT:
                    self.refresh_header_surface()

                if event.type == settings.EXIT_POINT_IS_OPEN_EVENT:
                    self.level.show_exit_point()

                if event.type == settings.START_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT:
                    self.level.show_player_vanishing_point()
                    pygame.time.set_timer(
                        pygame.event.Event(settings.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT), 1000)

                if event.type == settings.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT:
                    pygame.time.set_timer(settings.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT, 0)
                    self.game_state.load_next_level()

                if event.type == settings.NEXT_LEVEL_EVENT:
                    self.game_state.set_level_completed()
                    self.load_level_completed_message_dialog()

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

                if event.type == settings.ADD_VANISHING_POINT_EVENT:
                    self.level.add_vanishing_point(event.dict.get("position"))

                if event.type == settings.PLAYER_LOST_LIFE_EVENT:
                    self.level.show_player_tombstone()
                    pygame.time.set_timer(settings.RESPAWN_PLAYER_EVENT, 2000)

                if event.type == settings.TELEPORT_PLAYER_EVENT:
                    self.level.show_player_vanishing_point()
                    pygame.time.set_timer(
                        pygame.event.Event(settings.RESPAWN_PLAYER_EVENT, {"position": event.dict.get("position")}),
                        1000)

                if event.type == settings.RESPAWN_PLAYER_EVENT:
                    player_new_position = event.dict.get("position")
                    pygame.time.set_timer(settings.RESPAWN_PLAYER_EVENT, 0)
                    self.level.respawn_player(player_new_position)
                    self.refresh_dashboard_surface()

                if event.type == settings.GAME_OVER_EVENT:
                    self.level.show_player_tombstone()
                    pygame.time.set_timer(settings.GAME_OVER_SUMMARY_EVENT, 2000)

                if event.type == settings.GAME_OVER_SUMMARY_EVENT:
                    pygame.time.set_timer(settings.GAME_OVER_SUMMARY_EVENT, 0)
                    self.game_state.set_game_over()
                    self.load_game_over_message_dialog()
                    self.refresh_dashboard_surface()

            if self.game_state.game_status == GameStatus.GAME_IS_RUNNING:
                self.level.run()
            elif self.game_state.game_status == GameStatus.FIRST_PAGE and self.first_page is not None:
                self.first_page.draw()
            elif self.message_dialog is not None:
                self.message_dialog.draw()

            pygame.display.update()
            self.clock.tick(settings.FPS)

    def load_first_page(self):
        self.first_page = FirstPage(self.screen)

    def dispose_first_page(self):
        self.first_page = None

    def load_game_paused_message_dialog(self):
        messages = list()
        messages.append(Message('PAUSED', settings.HIGHLIGHTED_TEXT_COLOR, 40))
        messages.append(Message('Press the SPACE button to return to the game', settings.TEXT_COLOR, 20))
        self.message_dialog = MessageBox(self.screen, 740, 130, 20, settings.MESSAGE_BACKGROUND_COLOR,
                                         settings.MESSAGE_BORDER_COLOR, messages)

    def load_game_options_message_dialog(self):
        messages = list()
        messages.append(Message('SELECT OPTION', settings.HIGHLIGHTED_TEXT_COLOR, 40))
        messages.append(Message('F5 - Restart level', settings.TEXT_COLOR, 20))
        messages.append(Message('F7 - Quit game', settings.TEXT_COLOR, 20))
        messages.append(Message('', settings.TEXT_COLOR, 20))
        messages.append(Message('Press the ESC button to return to the game', settings.TEXT_COLOR, 20))
        self.message_dialog = MessageBox(self.screen, 740, 210, 20, settings.MESSAGE_BACKGROUND_COLOR,
                                         settings.MESSAGE_BORDER_COLOR, messages)

    def load_level_completed_message_dialog(self):
        messages = list()
        messages.append(Message('CONGRATULATIONS', settings.HIGHLIGHTED_TEXT_COLOR, 40))
        messages.append(Message('Level completed', settings.TEXT_COLOR, 20))
        messages.append(Message('Press the SPACE button to go to the next level', settings.TEXT_COLOR, 16))
        self.message_dialog = MessageBox(self.screen, 740, 150, 20, settings.MESSAGE_BACKGROUND_COLOR,
                                         settings.MESSAGE_BORDER_COLOR, messages)

    def load_next_level_message_dialog(self):
        messages = list()
        messages.append(Message(f'LEVEL {self.game_state.level + 1}', settings.HIGHLIGHTED_TEXT_COLOR, 80))
        messages.append(Message('Press the SPACE button to start', settings.TEXT_COLOR, 20))
        self.message_dialog = MessageBox(self.screen, settings.WIDTH, settings.HEIGHT, settings.HEIGHT // 2 - 80,
                                         settings.MESSAGE_BACKGROUND_COLOR, settings.MESSAGE_BORDER_COLOR, messages)

    def load_game_over_message_dialog(self):
        messages = list()
        messages.append(Message('GAME OVER', settings.HIGHLIGHTED_TEXT_COLOR, 40))
        self.message_dialog = MessageBox(self.screen, 800, 100, 20, settings.MESSAGE_BACKGROUND_COLOR,
                                         settings.MESSAGE_BORDER_COLOR, messages)

    def dispose_message_dialog(self):
        self.message_dialog = None


if __name__ == '__main__':
    # Initialize and run the game
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
