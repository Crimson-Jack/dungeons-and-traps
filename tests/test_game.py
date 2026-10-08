from unittest.mock import Mock, call

import pygame
import pytest

from settings import Settings
from src.enums.enemy_type import EnemyType
from src.enums.game_status import GameStatus
from src.enums.weapon_type import WeaponType
from src.events import Events
from src.game import Game
from src.level import Level
from src.level_stats import LevelStats
from src.panels.dashboard import Dashboard
from src.panels.dialog_factory import DialogFactory
from src.panels.first_page import FirstPage
from src.panels.header import Header
from src.panels.menu_box import MenuBox
from src.panels.message_box import MessageBox
from src.panels.studio_page import StudioPage


# Game() calls pygame.init() and loads level 1 in its constructor, so the SDL drivers must be
# switched to dummy before construction and Pygame must be shut down after every test.
@pytest.fixture
def game(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER', 'dummy')
    monkeypatch.setattr(Settings, 'FULL_SCREEN_MODE', False)
    monkeypatch.setattr(Settings, 'STUDIO_PAGE_VISIBILITY', False)

    game = Game()
    yield game

    pygame.event.clear()
    pygame.quit()


# Replaces the level and both panels with mocks so custom events can be checked by the calls Game makes.
@pytest.fixture
def game_with_mocked_components(game):
    game.level = Mock(spec=Level)
    game.header = Mock(spec=Header)
    game.dashboard = Mock(spec=Dashboard)
    pygame.event.clear()
    return game


@pytest.fixture
def set_timer_mock(monkeypatch):
    set_timer_mock = Mock()
    monkeypatch.setattr(pygame.time, 'set_timer', set_timer_mock)
    return set_timer_mock


PANEL_REFRESH_CALLS = [call.clean(), call.draw()]
POSITION = (100, 200)


def event_type_name(parameter_value) -> str | None:
    if type(parameter_value) is not int:
        return None
    return next((name for name, value in vars(Events).items() if value == parameter_value), None)


class TestGameConstruction:
    def test_starts_on_first_page_with_menu(self, game):
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE
        assert isinstance(game.first_page, FirstPage)
        assert isinstance(game.menu_dialog, MenuBox)
        assert game.menu_dialog.get_selected_index() == 0
        assert game.studio_page is None
        assert game.message_dialog is None
        assert game.summary_panel is None
        assert game.secret_code_text == ''
        assert game.active_movement_keys == set()


SCREEN_COMPONENT_NAMES = ('level', 'studio_page', 'first_page', 'menu_dialog', 'message_dialog', 'summary_panel')


RUN_CURRENT_SCREEN_CASES = [
    (GameStatus.UNKNOWN, {}),
    (GameStatus.GAME_IS_RUNNING, {'level': [call.run()]}),
    (GameStatus.STUDIO_PAGE, {'studio_page': [call.draw()]}),
    (GameStatus.FIRST_PAGE, {'first_page': [call.draw()], 'menu_dialog': [call.draw()]}),
    (GameStatus.GAME_IS_PAUSED, {'menu_dialog': [call.draw()]}),
    (GameStatus.SUMMARY, {'summary_panel': [call.draw()]}),
    (GameStatus.CREDITS, {'message_dialog': [call.draw()]}),
    (GameStatus.SECRET_CODE, {'message_dialog': [call.draw()]}),
    (GameStatus.SECRET_CODE_IS_VALID, {'message_dialog': [call.draw()]}),
    (GameStatus.NEXT_LEVEL, {'message_dialog': [call.draw()]}),
    (GameStatus.LEVEL_COMPLETED, {'message_dialog': [call.draw()]}),
    (GameStatus.GAME_OVER, {'message_dialog': [call.draw()]}),
    (GameStatus.YOU_WIN, {'message_dialog': [call.draw()]}),
]


class TestRunCurrentScreen:
    @pytest.mark.parametrize('game_status, expected_component_calls', RUN_CURRENT_SCREEN_CASES,
                             ids=[game_status.name for game_status, expected_component_calls in RUN_CURRENT_SCREEN_CASES])
    def test_runs_only_components_of_current_status(self, game, game_status, expected_component_calls):
        for component_name in SCREEN_COMPONENT_NAMES:
            setattr(game, component_name, Mock())
        game.game_manager.game_status = game_status

        game.run_current_screen()

        for component_name in SCREEN_COMPONENT_NAMES:
            assert getattr(game, component_name).method_calls == expected_component_calls.get(component_name, []), \
                component_name

    def test_message_dialog_statuses(self):
        assert Game.MESSAGE_DIALOG_STATUSES == {
            GameStatus.CREDITS, GameStatus.SECRET_CODE, GameStatus.SECRET_CODE_IS_VALID,
            GameStatus.NEXT_LEVEL, GameStatus.LEVEL_COMPLETED, GameStatus.GAME_OVER, GameStatus.YOU_WIN,
        }


class TestCustomEventHandlers:
    def test_every_custom_event_type_has_handler(self, game):
        event_types = {value for name, value in vars(Events).items() if name.endswith('_EVENT')}

        assert set(game.custom_event_handlers) == event_types


class TestHandleCustomEvents:
    @pytest.mark.parametrize('event_type, event_attributes, expected_level_calls, header_refreshed, dashboard_refreshed', [
        (Events.CHANGE_SCORE_EVENT, {}, [], True, False),
        (Events.COLLECT_DIAMOND_EVENT, {}, [], True, True),
        (Events.COLLECT_KEY_EVENT, {}, [], True, True),
        (Events.COLLECT_LIFE_EVENT, {}, [], False, True),
        (Events.CHANGE_WEAPON_CAPACITY_EVENT, {}, [], True, False),
        (Events.CHANGE_ENERGY_EVENT, {}, [], False, True),
        (Events.CHANGE_WEAPON_EVENT, {}, [], True, False),
        (Events.EXIT_POINT_IS_OPEN_EVENT, {}, [call.show_exit_point()], False, False),
        (Events.REMOVE_OBSTACLES_EVENT, {}, [call.remove_obstacles()], False, False),
        (Events.REFRESH_OBSTACLE_MAP_EVENT, {}, [call.refresh_obstacle_map()], False, False),
        (Events.PLAYER_TILE_POSITION_CHANGED_EVENT, {}, [call.inform_about_player_tile_position()], False, False),
        (Events.PARTICLE_EVENT, {}, [call.add_spark_to_particle_effect()], False, False),
        (Events.ADD_TOMBSTONE_EVENT, {'position': POSITION}, [call.add_tombstone(POSITION)], False, False),
        (Events.ADD_BOSS_TOMBSTONE_EVENT, {'position': POSITION}, [call.add_boss_tombstone(POSITION)], False, False),
        (Events.ADD_VANISHING_POINT_EVENT, {'position': POSITION}, [call.add_vanishing_point(POSITION)], False, False),
        (Events.CREATE_EGG_EVENT, {'position': POSITION}, [call.create_egg(POSITION)], False, False),
        (Events.CREATE_MONSTER_EVENT, {'position': POSITION}, [call.create_monster(POSITION)], False, False),
        (Events.CREATE_EXPLODE_EFFECT_EVENT, {'position': POSITION}, [call.show_explode_effect(POSITION)], False, False),
        (Events.ADD_PARTICLE_EFFECT_EVENT, {'position': POSITION, 'number_of_sparks': 12, 'colors': ['red', 'blue']},
         [call.add_particle_effect(POSITION, 12, ['red', 'blue'])], False, False),
        (Events.TILT_EFFECT_EVENT, {'tilt_cursor_increment_value': 3}, [call.enable_tilt_effect(3)], False, False),
        (Events.CREATE_BOSS_OCTOPUS_EVENT, {}, [call.create_boss_octopus()], False, True),
    ], ids=event_type_name)
    def test_delegates_event_to_level_and_panels(self, game_with_mocked_components, set_timer_mock, event_type,
                                                 event_attributes, expected_level_calls, header_refreshed,
                                                 dashboard_refreshed):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(event_type, event_attributes))

        assert game.level.method_calls == expected_level_calls
        assert game.header.method_calls == (PANEL_REFRESH_CALLS if header_refreshed else [])
        assert game.dashboard.method_calls == (PANEL_REFRESH_CALLS if dashboard_refreshed else [])
        set_timer_mock.assert_not_called()

    def test_start_teleport_to_next_level_shows_vanishing_point_and_schedules_finish(
            self, game_with_mocked_components, set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.START_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT))

        assert game.level.method_calls == [call.show_player_vanishing_point()]
        set_timer_mock.assert_called_once_with(
            pygame.event.Event(Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT), Game.TELEPORT_TO_NEXT_LEVEL_DELAY_MS)

    def test_finish_teleport_to_next_level_cancels_timer_and_posts_next_level_event(
            self, game_with_mocked_components, set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT))

        set_timer_mock.assert_called_once_with(Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT, 0)
        assert len(pygame.event.get(eventtype=Events.NEXT_LEVEL_EVENT)) == 1

    def test_player_lost_life_shows_tombstone_and_schedules_respawn(self, game_with_mocked_components,
                                                                    set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.PLAYER_LOST_LIFE_EVENT))

        assert game.level.method_calls == [call.show_player_tombstone()]
        set_timer_mock.assert_called_once_with(Events.RESPAWN_PLAYER_EVENT, Game.RESPAWN_AFTER_LOST_LIFE_DELAY_MS)

    def test_teleport_player_shows_vanishing_point_and_schedules_respawn_at_position(
            self, game_with_mocked_components, set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.TELEPORT_PLAYER_EVENT, {'position': POSITION}))

        assert game.level.method_calls == [call.show_player_vanishing_point()]
        set_timer_mock.assert_called_once_with(
            pygame.event.Event(Events.RESPAWN_PLAYER_EVENT, {'position': POSITION}),
            Game.RESPAWN_AFTER_TELEPORT_DELAY_MS)

    def test_respawn_player_cancels_timer_disables_weapon_and_respawns_at_position(
            self, game_with_mocked_components, set_timer_mock):
        game = game_with_mocked_components
        game.game_manager.set_player_is_using_weapon(True)

        game.handle_custom_events(pygame.event.Event(Events.RESPAWN_PLAYER_EVENT, {'position': POSITION}))

        set_timer_mock.assert_called_once_with(Events.RESPAWN_PLAYER_EVENT, 0)
        assert game.game_manager.player_is_using_weapon is False
        assert game.level.method_calls == [call.respawn_player(POSITION)]
        assert game.dashboard.method_calls == PANEL_REFRESH_CALLS

    def test_player_is_not_using_weapon_disables_weapon(self, game_with_mocked_components):
        game = game_with_mocked_components
        game.game_manager.set_player_is_using_weapon(True)

        game.handle_custom_events(pygame.event.Event(Events.PLAYER_IS_NOT_USING_WEAPON_EVENT))

        assert game.game_manager.player_is_using_weapon is False

    def test_game_over_shows_tombstone_and_schedules_summary(self, game_with_mocked_components, set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.GAME_OVER_EVENT))

        assert game.level.method_calls == [call.show_player_tombstone()]
        set_timer_mock.assert_called_once_with(Events.GAME_OVER_SUMMARY_EVENT, Game.END_OF_GAME_SUMMARY_DELAY_MS)

    def test_game_over_summary_cancels_timer_and_shows_game_over_dialog(self, game_with_mocked_components,
                                                                        set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.GAME_OVER_SUMMARY_EVENT))

        set_timer_mock.assert_called_once_with(Events.GAME_OVER_SUMMARY_EVENT, 0)
        assert game.game_manager.game_status == GameStatus.GAME_OVER
        assert isinstance(game.message_dialog, MessageBox)
        assert game.dashboard.method_calls == PANEL_REFRESH_CALLS

    def test_you_win_schedules_summary(self, game_with_mocked_components, set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.YOU_WIN_EVENT))

        assert game.level.method_calls == []
        set_timer_mock.assert_called_once_with(Events.YOU_WIN_SUMMARY_EVENT, Game.END_OF_GAME_SUMMARY_DELAY_MS)

    def test_you_win_summary_cancels_timer_and_shows_you_win_dialog(self, game_with_mocked_components,
                                                                    set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.YOU_WIN_SUMMARY_EVENT))

        set_timer_mock.assert_called_once_with(Events.YOU_WIN_SUMMARY_EVENT, 0)
        assert game.game_manager.game_status == GameStatus.YOU_WIN
        assert isinstance(game.message_dialog, MessageBox)
        assert game.dashboard.method_calls == PANEL_REFRESH_CALLS

    def test_next_level_with_all_enemies_defeated_awards_completion_bonus(self, game_with_mocked_components):
        game = game_with_mocked_components
        level_stats = LevelStats()
        level_stats.record_enemy_spawn(EnemyType.BAT)
        level_stats.record_enemy_kill(EnemyType.BAT, 100)
        game.game_manager.level_stats[-1] = level_stats
        score_before = game.game_manager.score

        game.handle_custom_events(pygame.event.Event(Events.NEXT_LEVEL_EVENT))

        assert game.game_manager.game_status == GameStatus.LEVEL_COMPLETED
        assert game.game_manager.score == score_before + Settings.LEVEL_COMPLETION_BONUS
        assert level_stats.get_bonus_record().awarded == 1
        assert level_stats.get_bonus_record().score == Settings.LEVEL_COMPLETION_BONUS
        assert isinstance(game.message_dialog, MessageBox)

    def test_next_level_with_enemies_left_awards_no_bonus(self, game_with_mocked_components):
        game = game_with_mocked_components
        level_stats = LevelStats()
        level_stats.record_enemy_spawn(EnemyType.BAT)
        level_stats.record_enemy_spawn(EnemyType.BAT)
        level_stats.record_enemy_kill(EnemyType.BAT, 100)
        game.game_manager.level_stats[-1] = level_stats
        score_before = game.game_manager.score

        game.handle_custom_events(pygame.event.Event(Events.NEXT_LEVEL_EVENT))

        assert game.game_manager.game_status == GameStatus.LEVEL_COMPLETED
        assert game.game_manager.score == score_before
        assert level_stats.get_bonus_record().awarded == 0
        assert isinstance(game.message_dialog, MessageBox)

    def test_unrelated_event_touches_nothing(self, game_with_mocked_components, set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE}))

        assert game.level.method_calls == []
        assert game.header.method_calls == []
        assert game.dashboard.method_calls == []
        set_timer_mock.assert_not_called()
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE


# --- Keyboard: menu screens (STUDIO_PAGE, FIRST_PAGE, CREDITS, SECRET_CODE, SECRET_CODE_IS_VALID) ---

FIRST_PAGE_MENU_NEW_GAME = 0
FIRST_PAGE_MENU_SECRET_CODE = 1
FIRST_PAGE_MENU_CREDITS = 2
FIRST_PAGE_MENU_QUIT = 3
SECRET_CODE_LEVEL_INDEX = 1


def key_down_event(key: int, unicode: str = '') -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode)


def message_texts(messages: list) -> list[str]:
    return [message.text for message in messages]


def enter_studio_page(game: Game) -> None:
    game.dispose_first_page()
    game.game_manager.set_studio_page()
    game.load_studio_page()


def enter_credits(game: Game) -> None:
    game.dispose_first_page()
    game.game_manager.set_credits()
    game.load_credits_message_dialog()


def enter_secret_code(game: Game, secret_code_text: str = '') -> None:
    game.dispose_first_page()
    game.game_manager.set_secret_code()
    game.secret_code_text = secret_code_text
    game.load_secret_code_message_dialog()


def enter_secret_code_is_valid(game: Game) -> None:
    game.dispose_first_page()
    game.game_manager.clear_settings_for_first_level(SECRET_CODE_LEVEL_INDEX)
    game.game_manager.set_secret_code_is_valid()
    game.secret_code_text = game.game_manager.LEVELS[SECRET_CODE_LEVEL_INDEX].secret_code
    game.load_secret_code_message_dialog(DialogFactory.create_secret_code_valid_messages())


class TestKeyboardHandlers:
    def test_every_status_except_unknown_has_keyboard_handler(self, game):
        assert set(game.keyboard_handlers) == set(GameStatus) - {GameStatus.UNKNOWN}

    def test_unknown_status_ignores_keys(self, game):
        game.game_manager.game_status = GameStatus.UNKNOWN
        first_page = game.first_page
        menu_dialog = game.menu_dialog

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_ESCAPE))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.UNKNOWN
        assert game.first_page is first_page
        assert game.menu_dialog is menu_dialog
        assert game.message_dialog is None


class TestAppendSecretCodeCharacter:
    @pytest.mark.parametrize('secret_code_text, character, expected_secret_code_text', [
        ('c', '1', 'c1'),
        ('', 'a', 'a'),
        ('a' * (Game.SECRET_CODE_MAX_LENGTH - 1), 'b', 'a' * (Game.SECRET_CODE_MAX_LENGTH - 1) + 'b'),
        ('a' * Game.SECRET_CODE_MAX_LENGTH, 'b', 'a' * Game.SECRET_CODE_MAX_LENGTH),
        ('c', ' ', 'c'),
        ('c', '!', 'c'),
        ('c', 'ą', 'c'),
        ('c', '', 'c'),
    ], ids=['digit', 'first_letter', 'last_allowed_character', 'beyond_max_length', 'space', 'punctuation',
            'non_ascii_letter', 'key_without_character'])
    def test_append_secret_code_character(self, secret_code_text, character, expected_secret_code_text):
        assert Game.append_secret_code_character(secret_code_text, character) == expected_secret_code_text


class TestKeyboardStudioPage:
    @pytest.mark.parametrize('key', [pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_a])
    def test_any_key_opens_first_page(self, game, key):
        enter_studio_page(game)
        assert isinstance(game.studio_page, StudioPage)

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE
        assert game.studio_page is None
        assert isinstance(game.first_page, FirstPage)
        assert isinstance(game.menu_dialog, MenuBox)


class TestKeyboardFirstPage:
    def test_escape_quits_game(self, game):
        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_ESCAPE))

        assert is_running is False
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE

    @pytest.mark.parametrize('key, start_index, expected_index', [
        (pygame.K_DOWN, FIRST_PAGE_MENU_NEW_GAME, FIRST_PAGE_MENU_SECRET_CODE),
        (pygame.K_s, FIRST_PAGE_MENU_NEW_GAME, FIRST_PAGE_MENU_SECRET_CODE),
        (pygame.K_UP, FIRST_PAGE_MENU_SECRET_CODE, FIRST_PAGE_MENU_NEW_GAME),
        (pygame.K_w, FIRST_PAGE_MENU_SECRET_CODE, FIRST_PAGE_MENU_NEW_GAME),
        (pygame.K_DOWN, FIRST_PAGE_MENU_QUIT, FIRST_PAGE_MENU_NEW_GAME),
        (pygame.K_UP, FIRST_PAGE_MENU_NEW_GAME, FIRST_PAGE_MENU_QUIT),
    ], ids=['down', 's', 'up', 'w', 'down_wraps_to_top', 'up_wraps_to_bottom'])
    def test_arrows_move_menu_selection(self, game, key, start_index, expected_index):
        game.menu_dialog.selected_index = start_index

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.menu_dialog.get_selected_index() == expected_index
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE

    @pytest.mark.parametrize('key', [pygame.K_RETURN, pygame.K_SPACE])
    def test_new_game_opens_next_level_dialog(self, game, key):
        game.menu_dialog.selected_index = FIRST_PAGE_MENU_NEW_GAME

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.NEXT_LEVEL
        assert game.first_page is None
        assert game.menu_dialog is None
        assert isinstance(game.message_dialog, MessageBox)
        assert message_texts(game.message_dialog.messages)[0] == 'LEVEL 1'

    def test_secret_code_opens_secret_code_dialog(self, game):
        game.menu_dialog.selected_index = FIRST_PAGE_MENU_SECRET_CODE

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.SECRET_CODE
        assert game.first_page is None
        assert game.menu_dialog is None
        assert isinstance(game.message_dialog, MessageBox)
        assert message_texts(game.message_dialog.messages)[0] == 'SECRET CODE'

    def test_credits_opens_credits_dialog(self, game):
        game.menu_dialog.selected_index = FIRST_PAGE_MENU_CREDITS

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.CREDITS
        assert game.first_page is None
        assert game.menu_dialog is None
        assert isinstance(game.message_dialog, MessageBox)

    def test_quit_quits_game(self, game):
        game.menu_dialog.selected_index = FIRST_PAGE_MENU_QUIT

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        assert is_running is False
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE

    def test_selected_menu_item_is_remembered_after_returning_to_first_page(self, game):
        game.menu_dialog.selected_index = FIRST_PAGE_MENU_CREDITS
        game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_ESCAPE))

        assert game.game_manager.game_status == GameStatus.FIRST_PAGE
        assert game.menu_dialog.get_selected_index() == FIRST_PAGE_MENU_CREDITS


class TestKeyboardCredits:
    def test_escape_returns_to_first_page_and_disposes_dialog(self, game):
        enter_credits(game)

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_ESCAPE))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE
        assert game.message_dialog is None
        assert isinstance(game.first_page, FirstPage)
        assert isinstance(game.menu_dialog, MenuBox)

    @pytest.mark.parametrize('key', [pygame.K_RETURN, pygame.K_SPACE, pygame.K_a])
    def test_other_keys_keep_credits(self, game, key):
        enter_credits(game)
        credits_dialog = game.message_dialog

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.CREDITS
        assert game.message_dialog is credits_dialog


class TestKeyboardSecretCode:
    def test_typing_alphanumeric_character_appends_it_and_refreshes_dialog(self, game):
        enter_secret_code(game, 'c')
        previous_dialog = game.message_dialog

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_1, '1'))

        assert game.secret_code_text == 'c1'
        assert game.message_dialog is not previous_dialog
        assert game.game_manager.game_status == GameStatus.SECRET_CODE

    def test_typing_beyond_max_length_is_ignored(self, game):
        full_secret_code_text = 'a' * Game.SECRET_CODE_MAX_LENGTH
        enter_secret_code(game, full_secret_code_text)

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_b, 'b'))

        assert game.secret_code_text == full_secret_code_text

    @pytest.mark.parametrize('key, unicode', [
        (pygame.K_SPACE, ' '),
        (pygame.K_1, '!'),
        (pygame.K_a, 'ą'),
        (pygame.K_LSHIFT, ''),
    ], ids=['space', 'punctuation', 'non_ascii_letter', 'key_without_character'])
    def test_typing_disallowed_character_is_ignored(self, game, key, unicode):
        enter_secret_code(game, 'c')

        game.handle_keyboard_buttons_down(key_down_event(key, unicode))

        assert game.secret_code_text == 'c'
        assert game.game_manager.game_status == GameStatus.SECRET_CODE

    @pytest.mark.parametrize('secret_code_text, expected_secret_code_text', [
        ('c12', 'c1'),
        ('c', ''),
        ('', ''),
    ], ids=['several_characters', 'one_character', 'empty'])
    def test_backspace_removes_last_character(self, game, secret_code_text, expected_secret_code_text):
        enter_secret_code(game, secret_code_text)

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_BACKSPACE))

        assert game.secret_code_text == expected_secret_code_text
        assert game.game_manager.game_status == GameStatus.SECRET_CODE

    def test_return_with_valid_code_prepares_selected_level(self, game):
        enter_secret_code(game, game.game_manager.LEVELS[SECRET_CODE_LEVEL_INDEX].secret_code)
        previous_level = game.level

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.SECRET_CODE_IS_VALID
        assert game.game_manager.level == SECRET_CODE_LEVEL_INDEX
        assert game.level is not previous_level
        valid_texts = message_texts(DialogFactory.create_secret_code_valid_messages())
        assert message_texts(game.message_dialog.messages)[-len(valid_texts):] == valid_texts

    def test_return_with_invalid_code_shows_error_and_keeps_level(self, game):
        enter_secret_code(game, 'wrongcode')
        previous_level = game.level

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.SECRET_CODE
        assert game.game_manager.level == 0
        assert game.level is previous_level
        assert game.secret_code_text == 'wrongcode'
        invalid_texts = message_texts(DialogFactory.create_secret_code_invalid_messages())
        assert message_texts(game.message_dialog.messages)[-len(invalid_texts):] == invalid_texts

    def test_escape_returns_to_first_page_clears_text_and_disposes_dialog(self, game):
        enter_secret_code(game, 'c1')

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_ESCAPE))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE
        assert game.secret_code_text == ''
        assert isinstance(game.first_page, FirstPage)
        assert isinstance(game.menu_dialog, MenuBox)
        assert game.message_dialog is None


class TestKeyboardSecretCodeIsValid:
    @pytest.mark.parametrize('key', [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE])
    def test_any_key_opens_next_level_dialog_and_clears_text(self, game, key):
        enter_secret_code_is_valid(game)
        secret_code_dialog = game.message_dialog

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.NEXT_LEVEL
        assert game.secret_code_text == ''
        assert isinstance(game.message_dialog, MessageBox)
        assert game.message_dialog is not secret_code_dialog
        assert message_texts(game.message_dialog.messages)[0] == f'LEVEL {SECRET_CODE_LEVEL_INDEX + 1}'


# --- Keyboard: gameplay (GAME_IS_RUNNING, GAME_IS_PAUSED, key release) ---

PAUSE_MENU_RESUME = 0
PAUSE_MENU_RESTART_LEVEL = 1
PAUSE_MENU_QUIT_GAME = 2


def key_up_event(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYUP, key=key)


def enter_game_is_running(game: Game) -> None:
    game.dispose_first_page()
    game.game_manager.set_game_is_running()


def enter_game_is_paused(game: Game) -> None:
    enter_game_is_running(game)
    game.game_manager.switch_pause_state()
    game.load_game_paused_menu()


class TestKeyboardGameIsRunning:
    @pytest.mark.parametrize('key, expected_movement_vector', [
        (pygame.K_DOWN, (0, 1)),
        (pygame.K_s, (0, 1)),
        (pygame.K_UP, (0, -1)),
        (pygame.K_w, (0, -1)),
        (pygame.K_RIGHT, (1, 0)),
        (pygame.K_d, (1, 0)),
        (pygame.K_LEFT, (-1, 0)),
        (pygame.K_a, (-1, 0)),
    ], ids=['down', 's', 'up', 'w', 'right', 'd', 'left', 'a'])
    def test_movement_key_sets_movement_vector_and_is_tracked(self, game, key, expected_movement_vector):
        enter_game_is_running(game)

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.player_movement_vector == expected_movement_vector
        assert game.active_movement_keys == {key}

    def test_two_movement_keys_give_diagonal_movement(self, game):
        enter_game_is_running(game)

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_DOWN))
        game.handle_keyboard_buttons_down(key_down_event(pygame.K_RIGHT))

        assert game.game_manager.player_movement_vector == (1, 1)
        assert game.active_movement_keys == {pygame.K_DOWN, pygame.K_RIGHT}

    @pytest.mark.parametrize('key', [pygame.K_LCTRL, pygame.K_LSHIFT])
    def test_weapon_key_starts_using_weapon(self, game, key):
        enter_game_is_running(game)

        game.handle_keyboard_buttons_down(key_down_event(key))

        assert game.game_manager.player_is_using_weapon is True

    @pytest.mark.parametrize('key, collected_weapons, start_weapon, expected_weapon', [
        (pygame.K_x, [WeaponType.NONE, WeaponType.SWORD, WeaponType.BOW], WeaponType.NONE, WeaponType.SWORD),
        (pygame.K_x, [WeaponType.NONE, WeaponType.BOW], WeaponType.NONE, WeaponType.BOW),
        (pygame.K_x, [WeaponType.NONE, WeaponType.SWORD], WeaponType.SWORD, WeaponType.NONE),
        (pygame.K_z, [WeaponType.NONE, WeaponType.SWORD, WeaponType.BOW], WeaponType.NONE, WeaponType.BOW),
        (pygame.K_x, [WeaponType.NONE], WeaponType.NONE, WeaponType.NONE),
    ], ids=['next', 'next_skips_not_collected', 'next_wraps_around', 'previous_wraps_and_skips',
            'nothing_collected'])
    def test_weapon_change_keys_switch_among_collected_weapons(self, game, key, collected_weapons, start_weapon,
                                                               expected_weapon):
        enter_game_is_running(game)
        game.game_manager.collected_weapons = collected_weapons
        game.game_manager.weapon_type = start_weapon

        game.handle_keyboard_buttons_down(key_down_event(key))

        assert game.game_manager.weapon_type == expected_weapon

    def test_escape_pauses_game_and_resets_movement(self, game):
        enter_game_is_running(game)
        game.handle_keyboard_buttons_down(key_down_event(pygame.K_DOWN))

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_ESCAPE))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.GAME_IS_PAUSED
        assert game.active_movement_keys == set()
        assert game.game_manager.player_movement_vector == (0, 0)
        assert isinstance(game.menu_dialog, MenuBox)
        assert game.menu_dialog.title.text == 'PAUSED'

    def test_other_key_changes_nothing(self, game):
        enter_game_is_running(game)

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_q))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.GAME_IS_RUNNING
        assert game.game_manager.player_movement_vector == (0, 0)
        assert game.active_movement_keys == set()


class TestKeyboardMovementKeyRelease:
    @pytest.mark.parametrize('key', [pygame.K_DOWN, pygame.K_s, pygame.K_UP, pygame.K_w,
                                     pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT, pygame.K_a],
                             ids=['down', 's', 'up', 'w', 'right', 'd', 'left', 'a'])
    def test_releasing_tracked_key_reverts_its_movement(self, game, key):
        enter_game_is_running(game)
        game.handle_keyboard_buttons_down(key_down_event(key))

        game.handle_keyboard_buttons_up(key_up_event(key))

        assert game.game_manager.player_movement_vector == (0, 0)
        assert game.active_movement_keys == set()

    def test_releasing_one_of_two_keys_keeps_the_other_direction(self, game):
        enter_game_is_running(game)
        game.handle_keyboard_buttons_down(key_down_event(pygame.K_DOWN))
        game.handle_keyboard_buttons_down(key_down_event(pygame.K_RIGHT))

        game.handle_keyboard_buttons_up(key_up_event(pygame.K_DOWN))

        assert game.game_manager.player_movement_vector == (1, 0)
        assert game.active_movement_keys == {pygame.K_RIGHT}

    def test_releasing_untracked_key_changes_nothing(self, game):
        # The key was pressed in another state (e.g. pause menu), so GAME_IS_RUNNING never tracked it.
        enter_game_is_running(game)

        game.handle_keyboard_buttons_up(key_up_event(pygame.K_DOWN))

        assert game.game_manager.player_movement_vector == (0, 0)
        assert game.active_movement_keys == set()


class TestKeyboardGameIsPaused:
    @pytest.mark.parametrize('key, start_index, expected_index', [
        (pygame.K_DOWN, PAUSE_MENU_RESUME, PAUSE_MENU_RESTART_LEVEL),
        (pygame.K_s, PAUSE_MENU_RESUME, PAUSE_MENU_RESTART_LEVEL),
        (pygame.K_UP, PAUSE_MENU_RESTART_LEVEL, PAUSE_MENU_RESUME),
        (pygame.K_w, PAUSE_MENU_RESTART_LEVEL, PAUSE_MENU_RESUME),
        (pygame.K_UP, PAUSE_MENU_RESUME, PAUSE_MENU_QUIT_GAME),
    ], ids=['down', 's', 'up', 'w', 'up_wraps_to_bottom'])
    def test_arrows_move_menu_selection(self, game, key, start_index, expected_index):
        enter_game_is_paused(game)
        game.menu_dialog.selected_index = start_index

        game.handle_keyboard_buttons_down(key_down_event(key))

        assert game.menu_dialog.get_selected_index() == expected_index
        assert game.game_manager.game_status == GameStatus.GAME_IS_PAUSED

    @pytest.mark.parametrize('key, selected_index', [
        (pygame.K_ESCAPE, PAUSE_MENU_RESUME),
        (pygame.K_RETURN, PAUSE_MENU_RESUME),
        (pygame.K_SPACE, PAUSE_MENU_RESUME),
    ], ids=['escape', 'resume_with_return', 'resume_with_space'])
    def test_escape_or_resume_continues_game(self, game, key, selected_index):
        enter_game_is_paused(game)
        game.menu_dialog.selected_index = selected_index
        game.active_movement_keys.add(pygame.K_DOWN)
        game.game_manager.set_player_movement(0, 1)

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.GAME_IS_RUNNING
        assert game.menu_dialog is None
        assert game.active_movement_keys == set()
        assert game.game_manager.player_movement_vector == (0, 0)

    def test_restart_level_with_lives_left_takes_life_and_rebuilds_level(self, game):
        enter_game_is_paused(game)
        game.menu_dialog.selected_index = PAUSE_MENU_RESTART_LEVEL
        game.game_manager.set_player_is_using_weapon(True)
        lives_before = game.game_manager.lives
        previous_level = game.level

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        assert game.game_manager.lives == lives_before - 1
        assert game.game_manager.game_status == GameStatus.NEXT_LEVEL
        assert game.level is not previous_level
        assert game.game_manager.player_is_using_weapon is False
        assert game.menu_dialog is None
        assert message_texts(game.message_dialog.messages)[0] == 'LEVEL 1'

    def test_restart_level_with_last_life_posts_game_over_summary(self, game):
        enter_game_is_paused(game)
        game.menu_dialog.selected_index = PAUSE_MENU_RESTART_LEVEL
        game.game_manager.lives = 1
        previous_level = game.level
        pygame.event.clear()

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        assert game.game_manager.lives == 0
        # Current behavior: the status goes back to GAME_IS_RUNNING and GAME_OVER_SUMMARY_EVENT sets GAME_OVER later.
        assert game.game_manager.game_status == GameStatus.GAME_IS_RUNNING
        assert len(pygame.event.get(eventtype=Events.GAME_OVER_SUMMARY_EVENT)) == 1
        assert game.level is previous_level
        assert game.menu_dialog is None

    def test_quit_game_resets_progress_and_returns_to_first_page(self, game):
        enter_game_is_paused(game)
        game.menu_dialog.selected_index = PAUSE_MENU_QUIT_GAME
        game.game_manager.score = 500
        game.game_manager.lives = 1
        previous_level = game.level

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE
        assert game.game_manager.score == 0
        assert game.game_manager.lives == 2
        assert game.game_manager.level == 0
        assert game.level is not previous_level
        assert isinstance(game.first_page, FirstPage)
        assert isinstance(game.menu_dialog, MenuBox)
        assert game.menu_dialog.title is None


# --- Keyboard: end of level and game (NEXT_LEVEL, LEVEL_COMPLETED, GAME_OVER, YOU_WIN, SUMMARY) ---

def enter_next_level(game: Game) -> None:
    game.dispose_first_page()
    game.game_manager.set_next_level()
    game.load_next_level_message_dialog()


def enter_level_completed(game: Game) -> None:
    game.dispose_first_page()
    game.game_manager.set_level_completed()
    game.load_level_completed_message_dialog()


def enter_game_over(game: Game) -> None:
    game.dispose_first_page()
    game.game_manager.set_game_over()
    game.load_game_over_message_dialog()


def enter_you_win(game: Game) -> None:
    game.dispose_first_page()
    game.game_manager.set_you_win()
    game.load_you_win_message_dialog()


def enter_summary(game: Game) -> None:
    game.dispose_first_page()
    game.load_summary_panel(player_won=False)


class TestKeyboardNextLevel:
    @pytest.mark.parametrize('key', [pygame.K_SPACE, pygame.K_RETURN])
    def test_space_or_return_starts_game(self, game, key):
        enter_next_level(game)

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.GAME_IS_RUNNING
        assert game.message_dialog is None

    @pytest.mark.parametrize('key', [pygame.K_ESCAPE, pygame.K_a])
    def test_other_keys_keep_next_level_dialog(self, game, key):
        enter_next_level(game)
        next_level_dialog = game.message_dialog

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.NEXT_LEVEL
        assert game.message_dialog is next_level_dialog


class TestKeyboardLevelCompleted:
    @pytest.mark.parametrize('key', [pygame.K_SPACE, pygame.K_RETURN])
    def test_space_or_return_prepares_next_level(self, game, key):
        enter_level_completed(game)
        game.game_manager.set_player_is_using_weapon(True)
        level_index_before = game.game_manager.level
        level_stats_count_before = len(game.game_manager.level_stats)
        previous_level = game.level

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.NEXT_LEVEL
        assert game.game_manager.level == level_index_before + 1
        assert len(game.game_manager.level_stats) == level_stats_count_before + 1
        assert game.level is not previous_level
        assert game.game_manager.player_is_using_weapon is False
        assert message_texts(game.message_dialog.messages)[0] == f'LEVEL {level_index_before + 2}'

    @pytest.mark.parametrize('key', [pygame.K_ESCAPE, pygame.K_a])
    def test_other_keys_keep_level_completed_dialog(self, game, key):
        enter_level_completed(game)
        level_completed_dialog = game.message_dialog

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.LEVEL_COMPLETED
        assert game.message_dialog is level_completed_dialog


class TestKeyboardGameOverAndYouWin:
    @pytest.mark.parametrize('enter_status, expected_player_won', [
        (enter_game_over, False),
        (enter_you_win, True),
    ], ids=['game_over', 'you_win'])
    @pytest.mark.parametrize('key', [pygame.K_SPACE, pygame.K_RETURN], ids=['space', 'return'])
    def test_space_or_return_opens_summary(self, game, enter_status, expected_player_won, key):
        enter_status(game)

        is_running = game.handle_keyboard_buttons_down(key_down_event(key))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.SUMMARY
        assert game.message_dialog is None
        assert game.summary_panel.current_page_index == 0
        assert game.summary_panel.pages[0].player_won is expected_player_won

    @pytest.mark.parametrize('enter_status, expected_status', [
        (enter_game_over, GameStatus.GAME_OVER),
        (enter_you_win, GameStatus.YOU_WIN),
    ], ids=['game_over', 'you_win'])
    def test_other_key_keeps_dialog(self, game, enter_status, expected_status):
        enter_status(game)
        dialog = game.message_dialog

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_ESCAPE))

        assert is_running is True
        assert game.game_manager.game_status == expected_status
        assert game.message_dialog is dialog
        assert game.summary_panel is None


class TestKeyboardSummary:
    @pytest.mark.parametrize('key', [pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT])
    def test_next_page_keys_go_to_next_page(self, game, key):
        enter_summary(game)

        game.handle_keyboard_buttons_down(key_down_event(key))

        assert game.summary_panel.current_page_index == 1
        assert game.game_manager.game_status == GameStatus.SUMMARY

    def test_next_page_after_last_page_wraps_to_first(self, game):
        enter_summary(game)
        game.summary_panel.current_page_index = len(game.summary_panel.pages) - 1

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_RIGHT))

        assert game.summary_panel.current_page_index == 0

    def test_left_goes_to_previous_page(self, game):
        enter_summary(game)
        game.summary_panel.current_page_index = 1

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_LEFT))

        assert game.summary_panel.current_page_index == 0

    def test_left_on_first_page_wraps_to_last(self, game):
        enter_summary(game)

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_LEFT))

        assert game.summary_panel.current_page_index == len(game.summary_panel.pages) - 1

    def test_escape_resets_game_and_returns_to_first_page(self, game):
        enter_summary(game)
        game.game_manager.score = 500
        game.game_manager.lives = 0
        previous_level = game.level

        is_running = game.handle_keyboard_buttons_down(key_down_event(pygame.K_ESCAPE))

        assert is_running is True
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE
        assert game.summary_panel is None
        assert game.game_manager.score == 0
        assert game.game_manager.lives == 2
        assert game.game_manager.level == 0
        assert game.level is not previous_level
        assert isinstance(game.first_page, FirstPage)
        assert isinstance(game.menu_dialog, MenuBox)


class TestKeyboardPlayerPath:
    def test_from_first_page_to_moving_player(self, game):
        assert game.game_manager.game_status == GameStatus.FIRST_PAGE

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_RETURN))
        assert game.game_manager.game_status == GameStatus.NEXT_LEVEL
        assert message_texts(game.message_dialog.messages)[0] == 'LEVEL 1'

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_SPACE))
        assert game.game_manager.game_status == GameStatus.GAME_IS_RUNNING

        game.handle_keyboard_buttons_down(key_down_event(pygame.K_DOWN))
        assert game.game_manager.player_movement_vector == (0, 1)
