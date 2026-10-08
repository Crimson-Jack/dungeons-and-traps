from collections.abc import Callable

import pygame

from settings import Settings
from src.events import Events
from src.enums.game_status import GameStatus
from src.game_manager import GameManager
from src.level import Level
from src.panels.dashboard import Dashboard
from src.panels.dialog_factory import DialogFactory
from src.panels.first_page import FirstPage
from src.panels.studio_page import StudioPage
from src.panels.header import Header
from src.panels.message import Message
from src.panels.multi_page_panel import MultiPagePanel
from src.panels.summary_collectables_page import SummaryCollectablesPage
from src.panels.summary_enemies_page import SummaryEnemiesPage
from src.panels.summary_trophy_page import SummaryTrophyPage


class Game:
    # Statuses whose whole screen is the current message_dialog
    MESSAGE_DIALOG_STATUSES = frozenset({
        GameStatus.CREDITS,
        GameStatus.SECRET_CODE,
        GameStatus.SECRET_CODE_IS_VALID,
        GameStatus.NEXT_LEVEL,
        GameStatus.LEVEL_COMPLETED,
        GameStatus.GAME_OVER,
        GameStatus.YOU_WIN,
    })

    # Timer durations (milliseconds)
    PARTICLE_SPARK_INTERVAL_MS = 40
    TELEPORT_TO_NEXT_LEVEL_DELAY_MS = 2500
    RESPAWN_AFTER_LOST_LIFE_DELAY_MS = 2000
    RESPAWN_AFTER_TELEPORT_DELAY_MS = 1000
    END_OF_GAME_SUMMARY_DELAY_MS = 2500

    SECRET_CODE_MAX_LENGTH = 16

    def __init__(self) -> None:
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

        # Clock
        self.clock = pygame.time.Clock()

        # Secret code input text
        self.secret_code_text = ""

        # Tracks movement keys pressed in GAME_IS_RUNNING so KEYUP events from other states are ignored
        self.active_movement_keys = set()

        # Custom event type -> handler
        self.custom_event_handlers = self.create_custom_event_handlers()

        # Game status -> keyboard (key down) handler
        self.keyboard_handlers = self.create_keyboard_handlers()

    def clean_screen(self) -> None:
        self.screen.fill(Settings.GAME_BACKGROUND_COLOR)

    def refresh_header_surface(self) -> None:
        self.header.clean()
        self.header.draw()

    def refresh_dashboard_surface(self) -> None:
        self.dashboard.clean()
        self.dashboard.draw()

    def refresh_header_and_dashboard_surfaces(self) -> None:
        self.refresh_header_surface()
        self.refresh_dashboard_surface()

    def run(self) -> None:
        pygame.time.set_timer(Events.PARTICLE_EVENT, self.PARTICLE_SPARK_INTERVAL_MS)

        is_running = True
        while is_running:
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

            self.run_current_screen()
            pygame.display.update()
            self.clock.tick(Settings.FPS)

    def run_current_screen(self) -> None:
        status = self.game_manager.game_status
        if status == GameStatus.GAME_IS_RUNNING:
            # Main game logic
            self.level.run()
        elif status == GameStatus.STUDIO_PAGE:
            self.studio_page.draw()
        elif status == GameStatus.FIRST_PAGE:
            self.first_page.draw()
            self.menu_dialog.draw()
        elif status == GameStatus.GAME_IS_PAUSED:
            self.menu_dialog.draw()
        elif status == GameStatus.SUMMARY:
            self.summary_panel.draw()
        elif status in self.MESSAGE_DIALOG_STATUSES:
            self.message_dialog.draw()

    def create_keyboard_handlers(self) -> dict[GameStatus, Callable[[pygame.event.Event], bool]]:
        return {
            GameStatus.GAME_IS_RUNNING: self.handle_game_is_running_keys,
            GameStatus.STUDIO_PAGE: self.handle_studio_page_keys,
            GameStatus.FIRST_PAGE: self.handle_first_page_keys,
            GameStatus.CREDITS: self.handle_credits_keys,
            GameStatus.SECRET_CODE: self.handle_secret_code_keys,
            GameStatus.SECRET_CODE_IS_VALID: self.handle_secret_code_is_valid_keys,
            GameStatus.NEXT_LEVEL: self.handle_next_level_keys,
            GameStatus.GAME_IS_PAUSED: self.handle_game_is_paused_keys,
            GameStatus.LEVEL_COMPLETED: self.handle_level_completed_keys,
            GameStatus.GAME_OVER: self.handle_game_over_keys,
            GameStatus.YOU_WIN: self.handle_you_win_keys,
            GameStatus.SUMMARY: self.handle_summary_keys,
        }

    def handle_keyboard_buttons_down(self, event: pygame.event.Event) -> bool:
        handler = self.keyboard_handlers.get(self.game_manager.game_status)
        if handler is None:
            return True
        return handler(event)

    def handle_game_is_running_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.active_movement_keys.add(event.key)
            self.game_manager.set_player_movement(0, 1)
        if event.key in (pygame.K_UP, pygame.K_w):
            self.active_movement_keys.add(event.key)
            self.game_manager.set_player_movement(0, -1)
        if event.key in (pygame.K_RIGHT, pygame.K_d):
            self.active_movement_keys.add(event.key)
            self.game_manager.set_player_movement(1, 0)
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.active_movement_keys.add(event.key)
            self.game_manager.set_player_movement(-1, 0)
        if event.key in (pygame.K_LCTRL, pygame.K_LSHIFT):
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
        return True

    def handle_game_is_paused_keys(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            # Close pause menu and continue the game
            self.resume_from_pause()
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.menu_dialog.select_previous()
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_dialog.select_next()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            selected = self.menu_dialog.get_selected_index()
            if selected == 0:
                # Resume
                self.resume_from_pause()
            elif selected == 1:
                # Restart level or trigger game over if no lives left
                self.dispose_menu_dialog()
                self.game_manager.decrease_number_of_lives()
                if self.game_manager.lives > 0:
                    self.game_manager.clear_settings_for_current_level()
                    self.start_level_intro()
                else:
                    self.game_manager.set_game_is_running()
                    pygame.event.post(pygame.event.Event(Events.GAME_OVER_SUMMARY_EVENT))
            elif selected == 2:
                # Quit to main menu and reset all progress
                self.dispose_menu_dialog()
                self.reset_game_and_show_first_page()
        return True

    def handle_studio_page_keys(self, event: pygame.event.Event) -> bool:
        self.dispose_studio_page()
        self.show_first_page()
        return True

    def handle_first_page_keys(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            return False
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_dialog.select_previous()
        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_dialog.select_next()
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            selected = self.menu_dialog.get_selected_index()
            if selected == 0:
                # New Game
                self.dispose_first_page()
                self.show_next_level_dialog()
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
        return True

    def handle_credits_keys(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            # Close credits dialog and show first page
            self.dispose_message_dialog()
            self.show_first_page()
        return True

    def handle_secret_code_keys(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            # Close secret code dialog and show first page
            self.secret_code_text = ''
            self.dispose_message_dialog()
            self.show_first_page()
        elif event.key == pygame.K_RETURN:
            # Validate secret code
            secret_code_level_index = self.game_manager.validate_secret_code(self.secret_code_text)
            if secret_code_level_index is not None:
                # Prepare selected level and change game status
                self.game_manager.clear_settings_for_first_level(secret_code_level_index)
                self.rebuild_level()
                self.game_manager.set_secret_code_is_valid()
                self.load_secret_code_message_dialog(DialogFactory.create_secret_code_valid_messages())
            else:
                # Show error message
                self.load_secret_code_message_dialog(DialogFactory.create_secret_code_invalid_messages())
        elif event.key == pygame.K_BACKSPACE:
            # Remove last char
            self.secret_code_text = self.secret_code_text[:-1]
            self.load_secret_code_message_dialog()
        else:
            self.secret_code_text = self.append_secret_code_character(self.secret_code_text, event.unicode)
            self.load_secret_code_message_dialog()
        return True

    @classmethod
    def append_secret_code_character(cls, secret_code_text: str, character: str) -> str:
        # Only ASCII letters and digits are accepted, up to SECRET_CODE_MAX_LENGTH characters
        if len(secret_code_text) < cls.SECRET_CODE_MAX_LENGTH and character.isascii() and character.isalnum():
            return secret_code_text + character
        return secret_code_text

    def handle_secret_code_is_valid_keys(self, event: pygame.event.Event) -> bool:
        # Close secret code dialog and open next level dialog
        self.dispose_message_dialog()
        self.show_next_level_dialog()
        self.secret_code_text = ''
        return True

    def handle_next_level_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            # Close next level dialog and continue the game
            self.dispose_message_dialog()
            self.game_manager.set_game_is_running()
            self.clean_screen()
            self.refresh_header_surface()
            self.refresh_dashboard_surface()
        return True

    def handle_level_completed_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            # Close level completed dialog, load next level and open next level dialog
            self.dispose_message_dialog()
            self.game_manager.clear_settings_for_next_level()
            self.start_level_intro()
        return True

    def handle_game_over_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.dispose_message_dialog()
            self.load_summary_panel(player_won=False)
        return True

    def handle_you_win_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.dispose_message_dialog()
            self.load_summary_panel(player_won=True)
        return True

    def handle_summary_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
            self.summary_panel.next_page()
        elif event.key == pygame.K_LEFT:
            self.summary_panel.previous_page()
        elif event.key == pygame.K_ESCAPE:
            self.dispose_summary_panel()
            self.reset_game_and_show_first_page()
        return True

    def handle_keyboard_buttons_up(self, event: pygame.event.Event) -> None:
        if event.key in self.active_movement_keys:
            self.active_movement_keys.discard(event.key)
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.game_manager.set_player_movement(0, -1)
            if event.key in (pygame.K_UP, pygame.K_w):
                self.game_manager.set_player_movement(0, 1)
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.game_manager.set_player_movement(-1, 0)
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.game_manager.set_player_movement(1, 0)

    def create_custom_event_handlers(self) -> dict[int, Callable[[pygame.event.Event], None]]:
        # Handlers read self.level on every call, because the level object is replaced on restart and level change.
        return {
            Events.CHANGE_SCORE_EVENT: lambda event: self.refresh_header_surface(),
            Events.COLLECT_DIAMOND_EVENT: lambda event: self.refresh_header_and_dashboard_surfaces(),
            Events.COLLECT_KEY_EVENT: lambda event: self.refresh_header_and_dashboard_surfaces(),
            Events.COLLECT_LIFE_EVENT: lambda event: self.refresh_dashboard_surface(),
            Events.CHANGE_WEAPON_CAPACITY_EVENT: lambda event: self.refresh_header_surface(),
            Events.CHANGE_ENERGY_EVENT: lambda event: self.refresh_dashboard_surface(),
            Events.CHANGE_WEAPON_EVENT: lambda event: self.refresh_header_surface(),
            Events.EXIT_POINT_IS_OPEN_EVENT: lambda event: self.level.show_exit_point(),
            Events.START_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT: self.handle_start_teleport_player_to_next_level_event,
            Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT: self.handle_finish_teleport_player_to_next_level_event,
            Events.NEXT_LEVEL_EVENT: self.handle_next_level_event,
            Events.REMOVE_OBSTACLES_EVENT: lambda event: self.level.remove_obstacles(),
            Events.REFRESH_OBSTACLE_MAP_EVENT: lambda event: self.level.refresh_obstacle_map(),
            Events.PLAYER_TILE_POSITION_CHANGED_EVENT: lambda event: self.level.inform_about_player_tile_position(),
            Events.PLAYER_IS_NOT_USING_WEAPON_EVENT: lambda event: self.game_manager.set_player_is_using_weapon(False),
            Events.ADD_PARTICLE_EFFECT_EVENT: lambda event: self.level.add_particle_effect(event.dict.get("position"),
                                                                                           event.dict.get("number_of_sparks"),
                                                                                           event.dict.get("colors")),
            Events.PARTICLE_EVENT: lambda event: self.level.add_spark_to_particle_effect(),
            Events.ADD_TOMBSTONE_EVENT: lambda event: self.level.add_tombstone(event.dict.get("position")),
            Events.ADD_BOSS_TOMBSTONE_EVENT: lambda event: self.level.add_boss_tombstone(event.dict.get("position")),
            Events.ADD_VANISHING_POINT_EVENT: lambda event: self.level.add_vanishing_point(event.dict.get("position")),
            Events.CREATE_EGG_EVENT: lambda event: self.level.create_egg(event.dict.get("position")),
            Events.CREATE_MONSTER_EVENT: lambda event: self.level.create_monster(event.dict.get("position")),
            Events.CREATE_BOSS_OCTOPUS_EVENT: self.handle_create_boss_octopus_event,
            Events.PLAYER_LOST_LIFE_EVENT: self.handle_player_lost_life_event,
            Events.TELEPORT_PLAYER_EVENT: self.handle_teleport_player_event,
            Events.RESPAWN_PLAYER_EVENT: self.handle_respawn_player_event,
            Events.CREATE_EXPLODE_EFFECT_EVENT: lambda event: self.level.show_explode_effect(event.dict.get("position")),
            Events.GAME_OVER_EVENT: self.handle_game_over_event,
            Events.GAME_OVER_SUMMARY_EVENT: self.handle_game_over_summary_event,
            Events.YOU_WIN_EVENT: lambda event: pygame.time.set_timer(
                Events.YOU_WIN_SUMMARY_EVENT, self.END_OF_GAME_SUMMARY_DELAY_MS),
            Events.YOU_WIN_SUMMARY_EVENT: self.handle_you_win_summary_event,
            Events.TILT_EFFECT_EVENT: lambda event: self.level.enable_tilt_effect(
                event.dict.get("tilt_cursor_increment_value")),
        }

    def handle_custom_events(self, event: pygame.event.Event) -> None:
        handler = self.custom_event_handlers.get(event.type)
        if handler is not None:
            handler(event)

    def handle_start_teleport_player_to_next_level_event(self, event: pygame.event.Event) -> None:
        self.level.show_player_vanishing_point()
        pygame.time.set_timer(
            pygame.event.Event(Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT), self.TELEPORT_TO_NEXT_LEVEL_DELAY_MS)

    def handle_finish_teleport_player_to_next_level_event(self, event: pygame.event.Event) -> None:
        pygame.time.set_timer(Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT, 0)
        self.game_manager.load_next_level()

    def handle_next_level_event(self, event: pygame.event.Event) -> None:
        self.game_manager.set_level_completed()
        if self.game_manager.level_stats[-1].all_enemies_defeated():
            self.game_manager.award_completion_bonus(Settings.LEVEL_COMPLETION_BONUS)
        self.load_level_completed_message_dialog()

    def handle_create_boss_octopus_event(self, event: pygame.event.Event) -> None:
        self.level.create_boss_octopus()
        self.refresh_dashboard_surface()

    def handle_player_lost_life_event(self, event: pygame.event.Event) -> None:
        self.level.show_player_tombstone()
        pygame.time.set_timer(Events.RESPAWN_PLAYER_EVENT, self.RESPAWN_AFTER_LOST_LIFE_DELAY_MS)

    def handle_teleport_player_event(self, event: pygame.event.Event) -> None:
        self.level.show_player_vanishing_point()
        pygame.time.set_timer(
            pygame.event.Event(Events.RESPAWN_PLAYER_EVENT, {"position": event.dict.get("position")}),
            self.RESPAWN_AFTER_TELEPORT_DELAY_MS)

    def handle_respawn_player_event(self, event: pygame.event.Event) -> None:
        player_new_position = event.dict.get("position")
        pygame.time.set_timer(Events.RESPAWN_PLAYER_EVENT, 0)
        self.game_manager.set_player_is_using_weapon(False)
        self.level.respawn_player(player_new_position)
        self.refresh_dashboard_surface()

    def handle_game_over_event(self, event: pygame.event.Event) -> None:
        self.level.show_player_tombstone()
        pygame.time.set_timer(Events.GAME_OVER_SUMMARY_EVENT, self.END_OF_GAME_SUMMARY_DELAY_MS)

    def handle_game_over_summary_event(self, event: pygame.event.Event) -> None:
        pygame.time.set_timer(Events.GAME_OVER_SUMMARY_EVENT, 0)
        self.game_manager.set_game_over()
        self.load_game_over_message_dialog()
        self.refresh_dashboard_surface()

    def handle_you_win_summary_event(self, event: pygame.event.Event) -> None:
        pygame.time.set_timer(Events.YOU_WIN_SUMMARY_EVENT, 0)
        self.game_manager.set_you_win()
        self.load_you_win_message_dialog()
        self.refresh_dashboard_surface()

    def load_studio_page(self) -> None:
        self.studio_page = StudioPage(self.screen)

    def dispose_studio_page(self) -> None:
        self.studio_page = None

    def load_first_page(self) -> None:
        self.first_page = FirstPage(self.screen)
        self.menu_dialog = DialogFactory.create_first_page_menu(self.screen)
        self.menu_dialog.selected_index = self.first_page_selected_index

    def dispose_first_page(self) -> None:
        if self.menu_dialog is not None:
            self.first_page_selected_index = self.menu_dialog.get_selected_index()
        self.first_page = None
        self.menu_dialog = None

    def load_game_paused_menu(self) -> None:
        self.menu_dialog = DialogFactory.create_game_paused_menu(self.screen)

    def load_level_completed_message_dialog(self) -> None:
        self.message_dialog = DialogFactory.create_level_completed_dialog(self.screen,
                                                                          self.game_manager.level_stats[-1])

    def load_next_level_message_dialog(self) -> None:
        self.message_dialog = DialogFactory.create_next_level_dialog(self.screen,
                                                                     self.game_manager.level + 1,
                                                                     self.game_manager.get_level_name(),
                                                                     self.game_manager.get_level_description(),
                                                                     self.game_manager.get_secret_code())

    def load_summary_panel(self, player_won: bool) -> None:
        diamond_record, key_record, bonus_record = self.game_manager.get_aggregate_collectable_stats()
        pages = (
            [SummaryTrophyPage(self.game_manager.score, player_won)]
            + SummaryEnemiesPage.create_pages(self.game_manager.get_aggregate_kill_stats())
            + [SummaryCollectablesPage(diamond_record, key_record, bonus_record)]
        )
        self.summary_panel = MultiPagePanel(self.screen, pages)
        self.game_manager.set_summary()

    def load_game_over_message_dialog(self) -> None:
        self.message_dialog = DialogFactory.create_game_over_dialog(self.screen)

    def load_you_win_message_dialog(self) -> None:
        self.message_dialog = DialogFactory.create_you_win_dialog(self.screen)

    def load_secret_code_message_dialog(self, dialog_response_messages: list[Message] | None = None) -> None:
        self.message_dialog = DialogFactory.create_secret_code_dialog(self.screen, self.secret_code_text,
                                                                      dialog_response_messages)

    def load_credits_message_dialog(self) -> None:
        self.message_dialog = DialogFactory.create_credits_dialog(self.screen)

    def dispose_menu_dialog(self) -> None:
        self.menu_dialog = None

    def dispose_message_dialog(self) -> None:
        self.message_dialog = None

    def dispose_summary_panel(self) -> None:
        self.summary_panel = None

    def show_first_page(self) -> None:
        self.game_manager.set_first_page()
        self.clean_screen()
        self.load_first_page()

    def show_next_level_dialog(self) -> None:
        self.game_manager.set_next_level()
        self.load_next_level_message_dialog()

    def rebuild_level(self) -> None:
        self.level = Level(self.screen, self.game_surface, self.game_manager)

    def start_level_intro(self) -> None:
        self.game_manager.set_player_is_using_weapon(False)
        self.rebuild_level()
        self.show_next_level_dialog()

    def resume_from_pause(self) -> None:
        self.active_movement_keys.clear()
        self.game_manager.reset_player_movement()
        self.dispose_menu_dialog()
        self.game_manager.switch_pause_state()

    def reset_game_and_show_first_page(self) -> None:
        self.game_manager.clear_settings_for_first_level()
        self.rebuild_level()
        self.show_first_page()
