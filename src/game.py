from collections.abc import Callable

import pygame

from settings import Settings
from src.events import Events
from src.enums.game_status import GameStatus
from src.custom_event_controller import CustomEventController
from src.game_manager import GameManager
from src.game_screens import GameScreens
from src.panels.dialog_factory import DialogFactory


class Game:
    # Timer durations (milliseconds)
    PARTICLE_SPARK_INTERVAL_MS = 40

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

        # Game manager
        self.game_manager = GameManager()

        # Game surfaces, level, panels, pages and dialogs
        self.screens = GameScreens(self.screen, self.game_manager)

        # Reactions to custom game events
        self.custom_events = CustomEventController(self.game_manager, self.screens)

        # Select startup mode
        if Settings.STUDIO_PAGE_VISIBILITY:
            self.screens.show_studio_page()
        else:
            self.screens.show_first_page()

        # Clock
        self.clock = pygame.time.Clock()

        # Secret code input text
        self.secret_code_text = ""

        # Tracks movement keys pressed in GAME_IS_RUNNING so KEYUP events from other states are ignored
        self.active_movement_keys = set()

        # Game status -> keyboard (key down) handler
        self.keyboard_handlers = self.create_keyboard_handlers()

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
                self.custom_events.handle_custom_events(event)

            self.screens.run_current_screen()
            pygame.display.update()
            self.clock.tick(Settings.FPS)

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
            self.screens.load_game_paused_menu()
        return True

    def handle_game_is_paused_keys(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            # Close pause menu and continue the game
            self.resume_from_pause()
        elif event.key in (pygame.K_UP, pygame.K_w):
            # Move to the previous menu item
            self.screens.menu_dialog.select_previous()
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            # Move to the next menu item
            self.screens.menu_dialog.select_next()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            selected = self.screens.menu_dialog.get_selected_index()
            if selected == 0:
                # Resume
                self.resume_from_pause()
            elif selected == 1:
                # Restart level or trigger game over if no lives left
                self.screens.dispose_menu_dialog()
                self.game_manager.decrease_number_of_lives()
                if self.game_manager.lives > 0:
                    self.game_manager.clear_settings_for_current_level()
                    self.start_level_intro()
                else:
                    self.game_manager.set_game_is_running()
                    pygame.event.post(pygame.event.Event(Events.GAME_OVER_SUMMARY_EVENT))
            elif selected == 2:
                # Quit to main menu and reset all progress
                self.screens.dispose_menu_dialog()
                self.reset_game_and_show_first_page()
        return True

    def handle_studio_page_keys(self, event: pygame.event.Event) -> bool:
        self.screens.dispose_studio_page()
        self.screens.show_first_page()
        return True

    def handle_first_page_keys(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            # Quit
            return False
        elif event.key in (pygame.K_UP, pygame.K_w):
            # Move to the previous menu item
            self.screens.menu_dialog.select_previous()
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            # Move to the next menu item
            self.screens.menu_dialog.select_next()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            selected = self.screens.menu_dialog.get_selected_index()
            if selected == 0:
                # New Game
                self.screens.dispose_first_page()
                self.screens.show_next_level_dialog()
            elif selected == 1:
                # Secret Code
                self.screens.dispose_first_page()
                self.game_manager.set_secret_code()
                self.screens.load_secret_code_message_dialog(self.secret_code_text)
            elif selected == 2:
                # Credits
                self.screens.dispose_first_page()
                self.game_manager.set_credits()
                self.screens.load_credits_message_dialog()
            elif selected == 3:
                # Quit
                return False
        return True

    def handle_credits_keys(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            # Close credits dialog and show first page
            self.screens.dispose_message_dialog()
            self.screens.show_first_page()
        return True

    def handle_secret_code_keys(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            # Close secret code dialog and show first page
            self.secret_code_text = ''
            self.screens.dispose_message_dialog()
            self.screens.show_first_page()
        elif event.key == pygame.K_RETURN:
            # Validate secret code
            secret_code_level_index = self.game_manager.validate_secret_code(self.secret_code_text)
            if secret_code_level_index is not None:
                # Prepare selected level and change game status
                self.game_manager.clear_settings_for_first_level(secret_code_level_index)
                self.screens.rebuild_level()
                self.game_manager.set_secret_code_is_valid()
                self.screens.load_secret_code_message_dialog(self.secret_code_text,
                                                             DialogFactory.create_secret_code_valid_messages())
            else:
                # Show error message
                self.screens.load_secret_code_message_dialog(self.secret_code_text,
                                                             DialogFactory.create_secret_code_invalid_messages())
        elif event.key == pygame.K_BACKSPACE:
            # Remove last char
            self.secret_code_text = self.secret_code_text[:-1]
            self.screens.load_secret_code_message_dialog(self.secret_code_text)
        else:
            self.secret_code_text = self.append_secret_code_character(self.secret_code_text, event.unicode)
            self.screens.load_secret_code_message_dialog(self.secret_code_text)
        return True

    @classmethod
    def append_secret_code_character(cls, secret_code_text: str, character: str) -> str:
        # Only ASCII letters and digits are accepted, up to SECRET_CODE_MAX_LENGTH characters
        if len(secret_code_text) < cls.SECRET_CODE_MAX_LENGTH and character.isascii() and character.isalnum():
            return secret_code_text + character
        return secret_code_text

    def handle_secret_code_is_valid_keys(self, event: pygame.event.Event) -> bool:
        # Close secret code dialog and open next level dialog
        self.screens.dispose_message_dialog()
        self.screens.show_next_level_dialog()
        self.secret_code_text = ''
        return True

    def handle_next_level_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            # Close next level dialog and continue the game
            self.screens.dispose_message_dialog()
            self.game_manager.set_game_is_running()
            self.screens.clean_screen()
            self.screens.refresh_header_surface()
            self.screens.refresh_dashboard_surface()
        return True

    def handle_level_completed_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            # Close level completed dialog, load next level and open next level dialog
            self.screens.dispose_message_dialog()
            self.game_manager.clear_settings_for_next_level()
            self.start_level_intro()
        return True

    def handle_game_over_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.screens.dispose_message_dialog()
            self.screens.load_summary_panel(player_won=False)
        return True

    def handle_you_win_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.screens.dispose_message_dialog()
            self.screens.load_summary_panel(player_won=True)
        return True

    def handle_summary_keys(self, event: pygame.event.Event) -> bool:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
            self.screens.summary_panel.next_page()
        elif event.key == pygame.K_LEFT:
            self.screens.summary_panel.previous_page()
        elif event.key == pygame.K_ESCAPE:
            self.screens.dispose_summary_panel()
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

    def start_level_intro(self) -> None:
        self.game_manager.set_player_is_using_weapon(False)
        self.screens.rebuild_level()
        self.screens.show_next_level_dialog()

    def resume_from_pause(self) -> None:
        self.active_movement_keys.clear()
        self.game_manager.reset_player_movement()
        self.screens.dispose_menu_dialog()
        self.game_manager.switch_pause_state()

    def reset_game_and_show_first_page(self) -> None:
        self.game_manager.clear_settings_for_first_level()
        self.screens.rebuild_level()
        self.screens.show_first_page()
