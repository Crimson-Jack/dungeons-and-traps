import pygame
import time

from settings import Settings
from src.events import Events
from src.enums.game_status import GameStatus
from src.game_manager import GameManager
from src.level import Level
from src.panels.dashboard import Dashboard
from src.panels.first_page import FirstPage
from src.panels.studio_page import StudioPage
from src.panels.header import Header
from src.panels.input_message import InputMessage
from src.panels.message import Message
from src.panels.multi_page_panel import MultiPagePanel
from src.panels.summary_collectables_page import SummaryCollectablesPage
from src.panels.summary_enemies_page import SummaryEnemiesPage
from src.panels.summary_trophy_page import SummaryTrophyPage
from src.panels.menu_box import MenuBox
from src.panels.message_box import MessageBox


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Dungeons and traps')

        if Settings.FULL_SCREEN_MODE:
            # Full screen mode
            monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
            Settings.WIDTH = pygame.display.Info().current_w
            Settings.HEIGHT = pygame.display.Info().current_h
            self.screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
        else:
            # Regular window
            self.screen = pygame.display.set_mode((Settings.WIDTH, Settings.HEIGHT))

        # Game surfaces
        game_surface_size = Settings.WIDTH, Settings.HEIGHT - Settings.HEADER_HEIGHT - Settings.DASHBOARD_HEIGHT
        header_surface_size = Settings.WIDTH, Settings.HEADER_HEIGHT
        dashboard_surface_size = Settings.WIDTH, Settings.DASHBOARD_HEIGHT
        self.game_surface = pygame.Surface(game_surface_size)
        self.header_surface = pygame.Surface(header_surface_size)
        self.dashboard_surface = pygame.Surface(dashboard_surface_size)

        # Game manager
        self.game_manager = GameManager()

        # Game components
        self.level = Level(self.screen, self.game_surface, self.game_manager)
        self.header = Header(self.screen, self.header_surface, self.game_manager)
        self.dashboard = Dashboard(self.screen, self.dashboard_surface, self.game_manager)

        # Studio page, first page, dialogs and summary panel
        self.studio_page = None
        self.first_page = None
        self.menu_dialog = None
        self.message_dialog = None
        self.summary_panel = None
        self.first_page_selected_index = 0

        # Select startup mode
        if Settings.STUDIO_PAGE_VISIBILITY:
            self.game_manager.set_studio_page()
            self.clean_screen()
            self.load_studio_page()
        else:
            self.game_manager.set_first_page()
            self.clean_screen()
            self.load_first_page()

        # Clock and time variables
        self.loop_start_time = None
        self.loop_end_time = None
        self.clock = pygame.time.Clock()

        # Secret code input text
        self.secret_code_text = ""

        # Tracks movement keys pressed in GAME_IS_RUNNING so KEYUP events from other states are ignored
        self.active_movement_keys = set()

    def clean_screen(self):
        self.screen.fill(Settings.GAME_BACKGROUND_COLOR)

    def refresh_header_surface(self):
        self.header.clean()
        self.header.draw()

    def refresh_dashboard_surface(self):
        self.dashboard.clean()
        self.dashboard.draw()

    def run(self):
        pygame.time.set_timer(Events.PARTICLE_EVENT, 40)

        is_running = True
        while is_running:
            # Save start time
            self.loop_start_time = time.time()

            # Handle events
            for event in pygame.event.get():
                # Input events: QUIT
                if event.type == pygame.QUIT:
                    is_running = False
                # Input events: keyboard (down)
                if event.type == pygame.KEYDOWN:
                    is_running = self.handle_keyboard_buttons_down(event)
                # Input events: keyboard (up)
                if event.type == pygame.KEYUP:
                    self.handle_keyboard_buttons_up(event)
                # Custom events
                self.handle_custom_events(event)

            if self.game_manager.game_status == GameStatus.GAME_IS_RUNNING:
                # Main game logic
                self.level.run()
            elif self.game_manager.game_status == GameStatus.STUDIO_PAGE:
                self.studio_page.draw()
            elif self.game_manager.game_status == GameStatus.FIRST_PAGE:
                self.first_page.draw()
                self.menu_dialog.draw()
            elif self.game_manager.game_status == GameStatus.CREDITS:
                self.message_dialog.draw()
            elif self.game_manager.game_status == GameStatus.SECRET_CODE:
                self.message_dialog.draw()
            elif self.game_manager.game_status == GameStatus.SECRET_CODE_IS_VALID:
                self.message_dialog.draw()
            elif self.game_manager.game_status == GameStatus.NEXT_LEVEL:
                self.message_dialog.draw()
            elif self.game_manager.game_status == GameStatus.GAME_IS_PAUSED:
                self.menu_dialog.draw()
            elif self.game_manager.game_status == GameStatus.LEVEL_COMPLETED:
                self.message_dialog.draw()
            elif self.game_manager.game_status == GameStatus.GAME_OVER:
                self.message_dialog.draw()
            elif self.game_manager.game_status == GameStatus.YOU_WIN:
                self.message_dialog.draw()
            elif self.game_manager.game_status == GameStatus.SUMMARY:
                self.summary_panel.draw()

            pygame.display.update()

            # Save end time and calculate FPS parameter
            self.loop_end_time = time.time()
            self.clock.tick(self.calculate_fps())

            # TODO: Remove
            # print(self.game_manager.player_movement_vector)
            # print(self.active_movement_keys)

        # TODO: Remove
        # print(sum(times_elapsed) / len(times_elapsed))

    def calculate_fps(self):
        if not Settings.DYNAMIC_FPS_ENABLED:
            return Settings.FPS
        else:
            base_frame_time = (1 / Settings.FPS)
            new_frame_time = base_frame_time - (self.loop_end_time - self.loop_start_time)
            new_fps = 1 / new_frame_time

            # TODO: Remove
            # print(f"Time {(self.loop_end_time - self.loop_start_time) * 1000:.2f} millisecond. New frame {new_frame_time}. New fps {new_fps}")

            return new_fps

    def handle_keyboard_buttons_down(self, event):
        if self.game_manager.game_status == GameStatus.GAME_IS_RUNNING:
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.active_movement_keys.add(event.key)
                self.game_manager.set_player_movement(0, 1)
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.active_movement_keys.add(event.key)
                self.game_manager.set_player_movement(0, -1)
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.active_movement_keys.add(event.key)
                self.game_manager.set_player_movement(1, 0)
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.active_movement_keys.add(event.key)
                self.game_manager.set_player_movement(-1, 0)
            if event.key == pygame.K_LCTRL or event.key == pygame.K_LSHIFT:
                self.game_manager.set_player_is_using_weapon(True)
            if event.key == pygame.K_x:
                self.game_manager.set_next_weapon()
            if event.key == pygame.K_z:
                self.game_manager.set_previous_weapon()
            if event.key == pygame.K_ESCAPE:
                # Open pause dialog and pause the game
                self.active_movement_keys.clear()
                self.game_manager.reset_player_movement()
                self.game_manager.switch_pause_state()
                self.load_game_paused_menu()
        elif self.game_manager.game_status == GameStatus.STUDIO_PAGE:
            self.dispose_studio_page()
            self.game_manager.set_first_page()
            self.clean_screen()
            self.load_first_page()
        elif self.game_manager.game_status == GameStatus.FIRST_PAGE:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.menu_dialog.select_previous()
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.menu_dialog.select_next()
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected = self.menu_dialog.get_selected_index()
                if selected == 0:
                    # New Game
                    self.dispose_first_page()
                    self.game_manager.set_next_level()
                    self.load_next_level_message_dialog()
                elif selected == 1:
                    # Secret Code
                    self.dispose_first_page()
                    self.game_manager.set_secret_code()
                    self.load_secret_code_message_dialog()
                elif selected == 2:
                    # Credits
                    self.dispose_first_page()
                    self.game_manager.set_credits()
                    self.load_credits_message_dialog()
                elif selected == 3:
                    # Quit
                    return False
        elif self.game_manager.game_status == GameStatus.CREDITS:
            if event.key == pygame.K_ESCAPE:
                # Close credits dialog and show first page
                self.dispose_message_dialog()
                self.game_manager.set_first_page()
                self.clean_screen()
                self.load_first_page()
        elif self.game_manager.game_status == GameStatus.SECRET_CODE:
            if event.key == pygame.K_ESCAPE:
                # Close secret code dialog and show first page
                self.secret_code_text = ''
                self.game_manager.set_first_page()
                self.clean_screen()
                self.load_first_page()
            elif event.key == pygame.K_RETURN:
                # Validate secret code
                secret_code_level_index = self.game_manager.validate_secret_code(self.secret_code_text)
                if secret_code_level_index is not None:
                    # Prepare selected level and change game status
                    self.game_manager.clear_settings_for_first_level(secret_code_level_index)
                    self.level = Level(self.screen, self.game_surface, self.game_manager)
                    self.game_manager.set_secret_code_is_valid()
                    messages = list()
                    messages.append(Message('The code is valid!', Settings.HIGHLIGHTED_TEXT_COLOR, 20))
                    messages.append(Message('Press any button to start the game', Settings.TEXT_COLOR, 20))
                    self.load_secret_code_message_dialog(messages)
                else:
                    # Show error message
                    messages = list()
                    messages.append(Message('', Settings.TEXT_COLOR, 20))
                    messages.append(Message('The code is not valid - please try again!', Settings.TEXT_COLOR, 20))
                    self.load_secret_code_message_dialog(messages)
            elif event.key == pygame.K_BACKSPACE:
                # Remove last char
                self.secret_code_text = self.secret_code_text[:-1]
                self.load_secret_code_message_dialog()
            else:
                if len(self.secret_code_text) < 16 and event.unicode.isascii() and event.unicode.isalnum():
                    # Add char to secret code text only if it's ASCII alphanumeric
                    self.secret_code_text += event.unicode
                self.load_secret_code_message_dialog()
        elif self.game_manager.game_status == GameStatus.SECRET_CODE_IS_VALID:
            # Close secret code dialog and open next level dialog
            self.dispose_message_dialog()
            self.game_manager.set_next_level()
            self.load_next_level_message_dialog()
            self.secret_code_text = ''
        elif self.game_manager.game_status == GameStatus.NEXT_LEVEL:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Close next level dialog and continue the game
                self.dispose_message_dialog()
                self.game_manager.set_game_is_running()
                self.clean_screen()
                self.refresh_header_surface()
                self.refresh_dashboard_surface()
        elif self.game_manager.game_status == GameStatus.GAME_IS_PAUSED:
            if event.key == pygame.K_ESCAPE:
                # Close pause menu and continue the game
                self.active_movement_keys.clear()
                self.game_manager.reset_player_movement()
                self.dispose_menu_dialog()
                self.game_manager.switch_pause_state()
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.menu_dialog.select_previous()
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.menu_dialog.select_next()
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected = self.menu_dialog.get_selected_index()
                if selected == 0:
                    # Resume
                    self.active_movement_keys.clear()
                    self.game_manager.reset_player_movement()
                    self.dispose_menu_dialog()
                    self.game_manager.switch_pause_state()
                elif selected == 1:
                    # Restart level or trigger game over if no lives left
                    self.dispose_menu_dialog()
                    self.game_manager.decrease_number_of_lives()
                    if self.game_manager.lives > 0:
                        self.game_manager.clear_settings_for_current_level()
                        self.game_manager.set_player_is_using_weapon(False)
                        self.level = Level(self.screen, self.game_surface, self.game_manager)
                        self.game_manager.set_next_level()
                        self.load_next_level_message_dialog()
                    else:
                        self.game_manager.set_game_is_running()
                        pygame.event.post(pygame.event.Event(Events.GAME_OVER_SUMMARY_EVENT))
                elif selected == 2:
                    # Quit to main menu and reset all progress
                    self.dispose_menu_dialog()
                    self.game_manager.clear_settings_for_first_level()
                    self.level = Level(self.screen, self.game_surface, self.game_manager)
                    self.game_manager.set_first_page()
                    self.clean_screen()
                    self.load_first_page()
        elif self.game_manager.game_status == GameStatus.LEVEL_COMPLETED:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Close level completed dialog, load next level and open next level dialog
                self.dispose_message_dialog()
                self.game_manager.clear_settings_for_next_level()
                self.game_manager.set_player_is_using_weapon(False)
                self.level = Level(self.screen, self.game_surface, self.game_manager)
                self.game_manager.set_next_level()
                self.load_next_level_message_dialog()
        elif self.game_manager.game_status == GameStatus.GAME_OVER:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.dispose_message_dialog()
                self.load_summary_panel()
        elif self.game_manager.game_status == GameStatus.YOU_WIN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.dispose_message_dialog()
                self.load_summary_panel()
        elif self.game_manager.game_status == GameStatus.SUMMARY:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_RIGHT:
                self.summary_panel.next_page()
            elif event.key == pygame.K_LEFT:
                self.summary_panel.previous_page()
            elif event.key == pygame.K_ESCAPE:
                self.dispose_summary_panel()
                self.game_manager.clear_settings_for_first_level()
                self.level = Level(self.screen, self.game_surface, self.game_manager)
                self.game_manager.set_first_page()
                self.clean_screen()
                self.load_first_page()

        return True

    def handle_keyboard_buttons_up(self, event):
        if event.key in self.active_movement_keys:
            self.active_movement_keys.discard(event.key)
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.game_manager.set_player_movement(0, -1)
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.game_manager.set_player_movement(0, 1)
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.game_manager.set_player_movement(-1, 0)
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.game_manager.set_player_movement(1, 0)

    def handle_custom_events(self, event):
        if event.type == Events.CHANGE_SCORE_EVENT:
            self.refresh_header_surface()

        if event.type == Events.COLLECT_DIAMOND_EVENT:
            self.refresh_header_surface()
            self.refresh_dashboard_surface()

        if event.type == Events.COLLECT_KEY_EVENT:
            self.refresh_header_surface()
            self.refresh_dashboard_surface()

        if event.type == Events.COLLECT_LIFE_EVENT:
            self.refresh_dashboard_surface()

        if event.type == Events.CHANGE_WEAPON_CAPACITY_EVENT:
            self.refresh_header_surface()

        if event.type == Events.CHANGE_ENERGY_EVENT:
            self.refresh_dashboard_surface()

        if event.type == Events.CHANGE_WEAPON_EVENT:
            self.refresh_header_surface()

        if event.type == Events.EXIT_POINT_IS_OPEN_EVENT:
            self.level.show_exit_point()

        if event.type == Events.START_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT:
            self.level.show_player_vanishing_point()
            pygame.time.set_timer(
                pygame.event.Event(Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT), 2500)

        if event.type == Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT:
            pygame.time.set_timer(Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT, 0)
            self.game_manager.load_next_level()

        if event.type == Events.NEXT_LEVEL_EVENT:
            self.game_manager.set_level_completed()
            if self.game_manager.level_stats[-1].all_enemies_defeated():
                self.game_manager.award_completion_bonus(1000)
            self.load_level_completed_message_dialog()

        if event.type == Events.REMOVE_OBSTACLES_EVENT:
            self.level.remove_obstacles()

        if event.type == Events.REFRESH_OBSTACLE_MAP_EVENT:
            self.level.refresh_obstacle_map()

        if event.type == Events.PLAYER_TILE_POSITION_CHANGED_EVENT:
            self.level.inform_about_player_tile_position()

        if event.type == Events.PLAYER_IS_NOT_USING_WEAPON_EVENT:
            self.game_manager.set_player_is_using_weapon(False)

        if event.type == Events.ADD_PARTICLE_EFFECT_EVENT:
            self.level.add_particle_effect(event.dict.get("position"),
                                           event.dict.get("number_of_sparks"),
                                           event.dict.get("colors"))

        if event.type == Events.PARTICLE_EVENT:
            self.level.add_spark_to_particle_effect()

        if event.type == Events.ADD_TOMBSTONE_EVENT:
            self.level.add_tombstone(event.dict.get("position"))

        if event.type == Events.ADD_BOSS_TOMBSTONE_EVENT:
            self.level.add_boss_tombstone(event.dict.get("position"))

        if event.type == Events.ADD_VANISHING_POINT_EVENT:
            self.level.add_vanishing_point(event.dict.get("position"))

        if event.type == Events.CREATE_EGG_EVENT:
            self.level.create_egg(event.dict.get("position"))

        if event.type == Events.CREATE_MONSTER_EVENT:
            self.level.create_monster(event.dict.get("position"))

        if event.type == Events.CREATE_BOSS_OCTOPUS_EVENT:
            self.level.create_boss_octopus()
            self.refresh_dashboard_surface()

        if event.type == Events.PLAYER_LOST_LIFE_EVENT:
            self.level.show_player_tombstone()
            pygame.time.set_timer(Events.RESPAWN_PLAYER_EVENT, 2000)

        if event.type == Events.TELEPORT_PLAYER_EVENT:
            self.level.show_player_vanishing_point()
            pygame.time.set_timer(
                pygame.event.Event(Events.RESPAWN_PLAYER_EVENT, {"position": event.dict.get("position")}),
                1000)

        if event.type == Events.RESPAWN_PLAYER_EVENT:
            player_new_position = event.dict.get("position")
            pygame.time.set_timer(Events.RESPAWN_PLAYER_EVENT, 0)
            self.game_manager.set_player_is_using_weapon(False)
            self.level.respawn_player(player_new_position)
            self.refresh_dashboard_surface()

        if event.type == Events.CREATE_EXPLODE_EFFECT_EVENT:
            self.level.show_explode_effect(event.dict.get("position"))

        if event.type == Events.GAME_OVER_EVENT:
            self.level.show_player_tombstone()
            pygame.time.set_timer(Events.GAME_OVER_SUMMARY_EVENT, 2500)

        if event.type == Events.GAME_OVER_SUMMARY_EVENT:
            pygame.time.set_timer(Events.GAME_OVER_SUMMARY_EVENT, 0)
            self.game_manager.set_game_over()
            self.load_game_over_message_dialog()
            self.refresh_dashboard_surface()

        if event.type == Events.YOU_WIN_EVENT:
            pygame.time.set_timer(Events.YOU_WIN_SUMMARY_EVENT, 2500)

        if event.type == Events.YOU_WIN_SUMMARY_EVENT:
            pygame.time.set_timer(Events.YOU_WIN_SUMMARY_EVENT, 0)
            self.game_manager.set_you_win()
            self.load_you_win_message_dialog()
            self.refresh_dashboard_surface()

        if event.type == Events.TILT_EFFECT_EVENT:
            self.level.enable_tilt_effect(event.dict.get("tilt_cursor_increment_value"))

    def load_studio_page(self):
        self.studio_page = StudioPage(self.screen)

    def dispose_studio_page(self):
        self.studio_page = None

    def load_first_page(self):
        self.first_page = FirstPage(self.screen)
        self.menu_dialog = MenuBox(self.screen, 500, 0, 0,
                                   Settings.MESSAGE_BACKGROUND_COLOR, Settings.MESSAGE_BORDER_COLOR,
                                   Settings.HIGHLIGHTED_TEXT_COLOR,
                                   None, [
                                       Message('New Game', Settings.TEXT_COLOR, 35),
                                       Message('Secret Code', Settings.TEXT_COLOR, 25),
                                       Message('Credits', Settings.TEXT_COLOR, 25),
                                       Message('Quit', Settings.TEXT_COLOR, 25),
                                   ],
                                   show_border=False)
        self.menu_dialog.selected_index = self.first_page_selected_index

    def dispose_first_page(self):
        if self.menu_dialog is not None:
            self.first_page_selected_index = self.menu_dialog.get_selected_index()
        self.first_page = None
        self.menu_dialog = None

    def load_game_paused_menu(self):
        self.menu_dialog = MenuBox(self.screen, 740, 200, 20,
                                   Settings.MESSAGE_BACKGROUND_COLOR, Settings.MESSAGE_BORDER_COLOR,
                                   Settings.HIGHLIGHTED_TEXT_COLOR,
                                   Message('PAUSED', Settings.HIGHLIGHTED_TEXT_COLOR, 40), [
                                       Message('Resume', Settings.TEXT_COLOR, 20),
                                       Message('Restart level', Settings.TEXT_COLOR, 20),
                                       Message('Quit game', Settings.TEXT_COLOR, 20),
                                   ])

    def load_level_completed_message_dialog(self):
        current_stats = self.game_manager.level_stats[-1]

        messages = list()
        messages.append(Message('CONGRATULATIONS', Settings.HIGHLIGHTED_TEXT_COLOR, 40))
        messages.append(Message('Level completed', Settings.TEXT_COLOR, 20))
        messages.append(Message('', Settings.TEXT_COLOR, 15))

        spider_kills = current_stats.get_enemy_spider_total_kills()
        spider_count = current_stats.get_enemy_spider_total_count()
        monster_kills = current_stats.get_enemy_monster_total_kills()
        monster_count = current_stats.get_enemy_monster_total_count()
        bat_kills = current_stats.get_enemy_bat_total_kills()
        bat_count = current_stats.get_enemy_bat_total_count()

        kill_lines_count = 0

        if spider_kills > 0 or monster_kills > 0 or bat_kills > 0:
            messages.append(Message('Defeated enemies:', Settings.TEXT_COLOR, 16))
            kill_lines_count += 1

            if spider_kills > 0:
                spider_score = current_stats.get_enemy_spider_total_score()
                messages.append(Message(f'Spiders: {spider_kills} / {spider_count} ({spider_score} pts)', Settings.TEXT_COLOR, 16))
                kill_lines_count += 1

            if monster_kills > 0:
                monster_score = current_stats.get_enemy_monster_total_score()
                messages.append(Message(f'Goblins: {monster_kills} / {monster_count} ({monster_score} pts)', Settings.TEXT_COLOR, 16))
                kill_lines_count += 1

            if bat_kills > 0:
                bat_score = current_stats.get_enemy_bat_total_score()
                messages.append(Message(f'Bats: {bat_kills} / {bat_count} ({bat_score} pts)', Settings.TEXT_COLOR, 16))
                kill_lines_count += 1

        dialog_height = 196 + kill_lines_count * 20

        if current_stats.all_enemies_defeated():
            messages.append(Message('EXTRA BONUS +1000 pts', Settings.HIGHLIGHTED_TEXT_COLOR, 20))
            dialog_height += 20

        messages.append(Message('', Settings.TEXT_COLOR, 15))
        messages.append(Message('Press the SPACE button to go to the next level', Settings.TEXT_COLOR, 20))

        self.message_dialog = MessageBox(self.screen, 740, dialog_height, 20, Settings.MESSAGE_BACKGROUND_COLOR,
                                         Settings.MESSAGE_BORDER_COLOR, messages)

    def load_next_level_message_dialog(self):
        messages = list()
        messages.append(Message(f'LEVEL {self.game_manager.level + 1}', Settings.HIGHLIGHTED_TEXT_COLOR, 80))

        level_name = self.game_manager.get_level_name()
        if level_name is not None:
            messages.append(Message('', Settings.TEXT_COLOR, 20))
            messages.append(Message(level_name, Settings.HIGHLIGHTED_TEXT_COLOR, 20))

        level_description = self.game_manager.get_level_description()
        if level_description is not None:
            sentences = level_description.split('. ')
            messages.append(Message('', Settings.TEXT_COLOR, 20))
            for sentence in sentences:
                if not sentence.endswith(('.', '!', '?')):
                    sentence += '.'
                messages.append(Message(sentence, Settings.TEXT_COLOR, 16))

        secret_code = self.game_manager.get_secret_code()
        if secret_code is not None and len(secret_code) > 0:
            messages.append(Message('', Settings.TEXT_COLOR, 80))
            messages.append(Message('The secret code for this level is', Settings.TEXT_COLOR, 16))
            messages.append(Message(secret_code, Settings.HIGHLIGHTED_TEXT_COLOR, 20))

        messages.append(Message('', Settings.TEXT_COLOR, 80))
        messages.append(Message('Press the SPACE button to start', Settings.TEXT_COLOR, 20))

        top_margin = 40
        if level_name is None:
            top_margin += 40
        if level_description is None:
            top_margin += 36

        self.message_dialog = MessageBox(self.screen, Settings.WIDTH, Settings.HEIGHT, top_margin,
                                         Settings.MESSAGE_BACKGROUND_COLOR, Settings.MESSAGE_BORDER_COLOR, messages)

    def load_summary_panel(self):
        diamond_record, key_record, bonus_record = self.game_manager.get_aggregate_collectable_stats()
        pages = (
            [SummaryTrophyPage(self.game_manager.score)]
            + SummaryEnemiesPage.create_pages(self.game_manager.get_aggregate_kill_stats())
            + [SummaryCollectablesPage(diamond_record, key_record, bonus_record)]
        )
        self.summary_panel = MultiPagePanel(self.screen, pages)
        self.game_manager.set_summary()

    def load_game_over_message_dialog(self):
        messages = list()
        messages.append(Message('GAME OVER', Settings.HIGHLIGHTED_TEXT_COLOR, 40))
        messages.append(Message('Press the SPACE button to open summary page', Settings.TEXT_COLOR, 20))
        self.message_dialog = MessageBox(self.screen, 740, 130, 20, Settings.MESSAGE_BACKGROUND_COLOR,
                                         Settings.MESSAGE_BORDER_COLOR, messages)

    def load_you_win_message_dialog(self):
        messages = list()
        messages.append(Message('YOU WIN', Settings.HIGHLIGHTED_TEXT_COLOR, 40))
        messages.append(Message('Press the SPACE button to open summary page', Settings.TEXT_COLOR, 20))
        self.message_dialog = MessageBox(self.screen, 740, 130, 20, Settings.MESSAGE_BACKGROUND_COLOR,
                                         Settings.MESSAGE_BORDER_COLOR, messages)

    def load_secret_code_message_dialog(self, dialog_response_messages: list[Message] = None):
        messages = list()
        messages.append(Message('SECRET CODE', Settings.HIGHLIGHTED_TEXT_COLOR, 40))
        messages.append(Message('to jump to a specific level', Settings.TEXT_COLOR, 16))
        messages.append(InputMessage(self.secret_code_text, Settings.TEXT_COLOR, 40, 610, 50, -5, 10, 20))
        if dialog_response_messages is not None:
            for item in dialog_response_messages:
                messages.append(item)
        else:
            messages.append(Message('', Settings.TEXT_COLOR, 20))
            messages.append(Message('Press ESC to cancel', Settings.TEXT_COLOR, 20))
        self.message_dialog = MessageBox(self.screen, 740, 270, 20, Settings.MESSAGE_BACKGROUND_COLOR,
                                              Settings.MESSAGE_BORDER_COLOR, messages)

    def load_credits_message_dialog(self):
        messages = list()
        messages.append(Message('CREDITS', Settings.HIGHLIGHTED_TEXT_COLOR, 40))
        messages.append(Message('', Settings.TEXT_COLOR, 15))
        messages.append(Message('A game by Crimson-Jack', Settings.TEXT_COLOR, 20))
        messages.append(Message('', Settings.TEXT_COLOR, 15))
        messages.append(Message('Graphics:', Settings.TEXT_COLOR, 16))
        messages.append(Message('Original graphics by Crimson-Jack,', Settings.TEXT_COLOR, 12))
        messages.append(Message('inspired by Tiny Dungeon tileset by Kenney - CC0', Settings.TEXT_COLOR, 12))
        messages.append(Message('', Settings.TEXT_COLOR, 15))
        messages.append(Message('Sound:', Settings.TEXT_COLOR, 16))
        messages.append(Message('Effects by Crimson-Jack,', Settings.TEXT_COLOR, 12))
        messages.append(Message('created with ChipTone by SFBGames', Settings.TEXT_COLOR, 12))
        messages.append(Message('', Settings.TEXT_COLOR, 15))
        messages.append(Message('Fonts:', Settings.TEXT_COLOR, 16))
        messages.append(Message('Silkscreen font by Jason Kottke', Settings.TEXT_COLOR, 12))
        messages.append(Message('Trade Winds font by Sideshow (Font Diner, Inc)', Settings.TEXT_COLOR, 12))
        messages.append(Message('', Settings.TEXT_COLOR, 15))
        messages.append(Message('Thanks to:', Settings.TEXT_COLOR, 16))
        messages.append(Message('My wife and kids, who are always so eager', Settings.TEXT_COLOR, 12))
        messages.append(Message('to help me pursue my indie game-making passion :-)', Settings.TEXT_COLOR, 12))
        messages.append(Message('My friend MAK and all my mates from CF', Settings.TEXT_COLOR, 12))
        messages.append(Message('The whole Polish retro YouTube community,', Settings.TEXT_COLOR, 12))
        messages.append(Message('especially fans of 8-bit computers from the 80s and 90s,', Settings.TEXT_COLOR, 12))
        messages.append(Message('in particular: ARF, Retrobajtel and more ... ', Settings.TEXT_COLOR, 12))
        messages.append(Message('', Settings.TEXT_COLOR, 15))
        messages.append(Message('Press ESC to return', Settings.TEXT_COLOR, 20))
        self.message_dialog = MessageBox(self.screen, 740, 560, 20, Settings.MESSAGE_BACKGROUND_COLOR,
                                         Settings.MESSAGE_BORDER_COLOR, messages)

    def dispose_menu_dialog(self):
        self.menu_dialog = None

    def dispose_message_dialog(self):
        self.message_dialog = None

    def dispose_summary_panel(self):
        self.summary_panel = None
