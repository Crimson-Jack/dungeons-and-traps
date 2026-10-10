from collections.abc import Callable

import pygame

from src.enums.game_status import GameStatus
from src.events import Events
from src.game_manager import GameManager
from src.panels.dialog_factory import DialogFactory
from src.screen_manager import ScreenManager


class KeyboardController:
    """Reacts to keyboard input according to the current game status."""

    SECRET_CODE_MAX_LENGTH = 16

    def __init__(self, game_manager: GameManager, screen_manager: ScreenManager) -> None:
        """
        Start with empty secret code text and no pressed movement keys,
        and build the table that maps each game status to its key down handler.

        :param game_manager: shared game state
        :param screen_manager: level, panels, pages and dialogs currently on screen
        """
        self.game_manager = game_manager
        self.screen_manager = screen_manager

        # Secret code input text
        self.secret_code_text = ''

        # Tracks movement keys pressed in GAME_IS_RUNNING so KEYUP events from other states are ignored
        self.active_movement_keys = set()

        # Game status -> keyboard (key down) handler
        self.keyboard_handlers = self.create_keyboard_handlers()

    def handle_keyboard_buttons_down(self, event: pygame.event.Event) -> bool:
        """
        Run the key down handler registered for the current game status.
        Statuses without a handler ignore the key.

        :param event: KEYDOWN event
        :return: False when the player chose to quit the game, True otherwise
        """
        handler = self.keyboard_handlers.get(self.game_manager.game_status)
        if handler is None:
            return True
        return handler(event)

    def handle_keyboard_buttons_up(self, event: pygame.event.Event) -> None:
        """
        Revert the movement of a released movement key, if it was pressed while the game was running.

        :param event: KEYUP event
        """
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

    def create_keyboard_handlers(self) -> dict[GameStatus, Callable[[pygame.event.Event], bool]]:
        """
        Create the table that maps each game status to its key down handler.

        :return: game status -> key down handler
        """
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

    def handle_game_is_running_keys(self, event: pygame.event.Event) -> bool:
        """
        Move the player, use or switch the weapon, or pause the game.

        :param event: KEYDOWN event
        :return: always True
        """
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
            self.screen_manager.load_game_paused_menu()
        return True

    def handle_studio_page_keys(self, event: pygame.event.Event) -> bool:
        """
        Close the studio page and show the first page on any key.

        :param event: KEYDOWN event
        :return: always True
        """
        self.screen_manager.dispose_studio_page()
        self.screen_manager.show_first_page()
        return True

    def handle_first_page_keys(self, event: pygame.event.Event) -> bool:
        """
        Move through the first page menu and run the selected item: new game, secret code, credits or quit.

        :param event: KEYDOWN event
        :return: False when the player quits the game, True otherwise
        """
        if event.key == pygame.K_ESCAPE:
            # Quit
            return False
        elif event.key in (pygame.K_UP, pygame.K_w):
            # Move to the previous menu item
            self.screen_manager.menu_dialog.select_previous()
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            # Move to the next menu item
            self.screen_manager.menu_dialog.select_next()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            selected = self.screen_manager.menu_dialog.get_selected_index()
            if selected == 0:
                # New Game
                self.screen_manager.dispose_first_page()
                self.screen_manager.show_next_level_dialog()
            elif selected == 1:
                # Secret Code
                self.screen_manager.dispose_first_page()
                self.game_manager.set_secret_code()
                self.screen_manager.load_secret_code_message_dialog(self.secret_code_text)
            elif selected == 2:
                # Credits
                self.screen_manager.dispose_first_page()
                self.game_manager.set_credits()
                self.screen_manager.load_credits_message_dialog()
            elif selected == 3:
                # Quit
                return False
        return True

    def handle_credits_keys(self, event: pygame.event.Event) -> bool:
        """
        Close the credits dialog and show the first page on Escape.

        :param event: KEYDOWN event
        :return: always True
        """
        if event.key == pygame.K_ESCAPE:
            # Close credits dialog and show first page
            self.screen_manager.dispose_message_dialog()
            self.screen_manager.show_first_page()
        return True

    def handle_secret_code_keys(self, event: pygame.event.Event) -> bool:
        """
        Edit the secret code text, validate it on Return or go back to the first page on Escape.

        :param event: KEYDOWN event
        :return: always True
        """
        if event.key == pygame.K_ESCAPE:
            # Close secret code dialog and show first page
            self.secret_code_text = ''
            self.screen_manager.dispose_message_dialog()
            self.screen_manager.show_first_page()
        elif event.key == pygame.K_RETURN:
            # Validate secret code
            secret_code_level_index = self.game_manager.validate_secret_code(self.secret_code_text)
            if secret_code_level_index is not None:
                # Prepare selected level and change game status
                self.game_manager.clear_settings_for_first_level(secret_code_level_index)
                self.screen_manager.rebuild_level()
                self.game_manager.set_secret_code_is_valid()
                self.screen_manager.load_secret_code_message_dialog(self.secret_code_text,
                                                                    DialogFactory.create_secret_code_valid_messages())
            else:
                # Show error message
                self.screen_manager.load_secret_code_message_dialog(self.secret_code_text,
                                                                    DialogFactory.create_secret_code_invalid_messages())
        elif event.key == pygame.K_BACKSPACE:
            # Remove last char
            self.secret_code_text = self.secret_code_text[:-1]
            self.screen_manager.load_secret_code_message_dialog(self.secret_code_text)
        else:
            self.secret_code_text = self.append_secret_code_character(self.secret_code_text, event.unicode)
            self.screen_manager.load_secret_code_message_dialog(self.secret_code_text)
        return True

    @classmethod
    def append_secret_code_character(cls, secret_code_text: str, character: str) -> str:
        """
        Append the typed character to the secret code text when it is allowed.

        :param secret_code_text: text typed so far
        :param character: character produced by the pressed key, may be empty
        :return: text with the character appended, or the unchanged text
        """
        # Only ASCII letters and digits are accepted, up to SECRET_CODE_MAX_LENGTH characters
        if len(secret_code_text) < cls.SECRET_CODE_MAX_LENGTH and character.isascii() and character.isalnum():
            return secret_code_text + character
        return secret_code_text

    def handle_secret_code_is_valid_keys(self, event: pygame.event.Event) -> bool:
        """
        Close the valid secret code dialog and show the next level dialog on any key.

        :param event: KEYDOWN event
        :return: always True
        """
        # Close secret code dialog and open next level dialog
        self.screen_manager.dispose_message_dialog()
        self.screen_manager.show_next_level_dialog()
        self.secret_code_text = ''
        return True

    def handle_next_level_keys(self, event: pygame.event.Event) -> bool:
        """
        Close the next level dialog and start the game on Return or Space.

        :param event: KEYDOWN event
        :return: always True
        """
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            # Close next level dialog and continue the game
            self.screen_manager.dispose_message_dialog()
            self.game_manager.set_game_is_running()
            self.screen_manager.clean_screen()
            self.screen_manager.refresh_header_surface()
            self.screen_manager.refresh_dashboard_surface()
        return True

    def handle_game_is_paused_keys(self, event: pygame.event.Event) -> bool:
        """
        Move through the pause menu and run the selected item: resume, restart level or quit to the first page.

        :param event: KEYDOWN event
        :return: always True
        """
        if event.key == pygame.K_ESCAPE:
            # Close pause menu and continue the game
            self.resume_from_pause()
        elif event.key in (pygame.K_UP, pygame.K_w):
            # Move to the previous menu item
            self.screen_manager.menu_dialog.select_previous()
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            # Move to the next menu item
            self.screen_manager.menu_dialog.select_next()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            selected = self.screen_manager.menu_dialog.get_selected_index()
            if selected == 0:
                # Resume
                self.resume_from_pause()
            elif selected == 1:
                # Restart level or trigger game over if no lives left
                self.screen_manager.dispose_menu_dialog()
                self.game_manager.decrease_number_of_lives()
                if self.game_manager.lives > 0:
                    self.game_manager.clear_settings_for_current_level()
                    self.start_level_intro()
                else:
                    self.game_manager.set_game_is_running()
                    pygame.event.post(pygame.event.Event(Events.GAME_OVER_SUMMARY_EVENT))
            elif selected == 2:
                # Quit to main menu and reset all progress
                self.screen_manager.dispose_menu_dialog()
                self.reset_game_and_show_first_page()
        return True

    def handle_level_completed_keys(self, event: pygame.event.Event) -> bool:
        """
        Close the level completed dialog and prepare the next level on Return or Space.

        :param event: KEYDOWN event
        :return: always True
        """
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            # Close level completed dialog, load next level and open next level dialog
            self.screen_manager.dispose_message_dialog()
            self.game_manager.clear_settings_for_next_level()
            self.start_level_intro()
        return True

    def handle_game_over_keys(self, event: pygame.event.Event) -> bool:
        """
        Close the game over dialog and show the summary on Return or Space.

        :param event: KEYDOWN event
        :return: always True
        """
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.screen_manager.dispose_message_dialog()
            self.screen_manager.load_summary_panel(player_won=False)
        return True

    def handle_you_win_keys(self, event: pygame.event.Event) -> bool:
        """
        Close the 'you win' dialog and show the summary on Return or Space.

        :param event: KEYDOWN event
        :return: always True
        """
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.screen_manager.dispose_message_dialog()
            self.screen_manager.load_summary_panel(player_won=True)
        return True

    def handle_summary_keys(self, event: pygame.event.Event) -> bool:
        """
        Turn the summary pages, or reset the game and show the first page on Escape.

        :param event: KEYDOWN event
        :return: always True
        """
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
            self.screen_manager.summary_panel.next_page()
        elif event.key == pygame.K_LEFT:
            self.screen_manager.summary_panel.previous_page()
        elif event.key == pygame.K_ESCAPE:
            self.screen_manager.dispose_summary_panel()
            self.reset_game_and_show_first_page()
        return True

    def start_level_intro(self) -> None:
        """
        Put the weapon away, rebuild the level and show the next level dialog.
        """
        self.game_manager.set_player_is_using_weapon(False)
        self.screen_manager.rebuild_level()
        self.screen_manager.show_next_level_dialog()

    def resume_from_pause(self) -> None:
        """
        Forget pressed movement keys, stop the player, close the pause menu and continue the game.
        """
        self.active_movement_keys.clear()
        self.game_manager.reset_player_movement()
        self.screen_manager.dispose_menu_dialog()
        self.game_manager.switch_pause_state()

    def reset_game_and_show_first_page(self) -> None:
        """
        Reset all progress, rebuild the first level and show the first page.
        """
        self.game_manager.clear_settings_for_first_level()
        self.screen_manager.rebuild_level()
        self.screen_manager.show_first_page()
