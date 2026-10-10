import pygame

from src.enums.game_status import GameStatus
from src.panels.first_page import FirstPage
from src.panels.menu_box import MenuBox
from tests.test_keyboard_controller import key_down_event, message_texts


class TestGameConstruction:
    def test_starts_on_first_page_with_menu(self, game):
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE
        assert isinstance(game.screen_manager.first_page, FirstPage)
        assert isinstance(game.screen_manager.menu_dialog, MenuBox)
        assert game.screen_manager.menu_dialog.get_selected_index() == 0
        assert game.screen_manager.studio_page is None
        assert game.screen_manager.message_dialog is None
        assert game.screen_manager.summary_panel is None
        assert game.keyboard_controller.secret_code_text == ''
        assert game.keyboard_controller.active_movement_keys == set()


class TestKeyboardPlayerPath:
    def test_from_first_page_to_moving_player(self, game):
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE

        game.keyboard_controller.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))
        assert game.game_manager.game_status == GameStatus.NEXT_LEVEL
        assert message_texts(game.screen_manager.message_dialog.messages)[0] == 'LEVEL 1'

        game.keyboard_controller.handle_keyboard_buttons_down(key_down_event(pygame.K_SPACE))
        assert game.game_manager.game_status == GameStatus.GAME_IS_RUNNING

        game.keyboard_controller.handle_keyboard_buttons_down(key_down_event(pygame.K_DOWN))
        assert game.game_manager.player_movement_vector == (0, 1)
