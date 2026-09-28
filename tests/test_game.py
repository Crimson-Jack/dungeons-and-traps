from unittest.mock import Mock, call

import pygame
import pytest

from settings import Settings
from src.enums.enemy_type import EnemyType
from src.enums.game_status import GameStatus
from src.events import Events
from src.game import Game
from src.level import Level
from src.level_stats import LevelStats
from src.panels.dashboard import Dashboard
from src.panels.first_page import FirstPage
from src.panels.header import Header
from src.panels.menu_box import MenuBox
from src.panels.message_box import MessageBox


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
            pygame.event.Event(Events.FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT), 2500)

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
        set_timer_mock.assert_called_once_with(Events.RESPAWN_PLAYER_EVENT, 2000)

    def test_teleport_player_shows_vanishing_point_and_schedules_respawn_at_position(
            self, game_with_mocked_components, set_timer_mock):
        game = game_with_mocked_components

        game.handle_custom_events(pygame.event.Event(Events.TELEPORT_PLAYER_EVENT, {'position': POSITION}))

        assert game.level.method_calls == [call.show_player_vanishing_point()]
        set_timer_mock.assert_called_once_with(
            pygame.event.Event(Events.RESPAWN_PLAYER_EVENT, {'position': POSITION}), 1000)

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
        set_timer_mock.assert_called_once_with(Events.GAME_OVER_SUMMARY_EVENT, 2500)

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
        set_timer_mock.assert_called_once_with(Events.YOU_WIN_SUMMARY_EVENT, 2500)

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
        assert game.game_manager.score == score_before + 1000
        assert level_stats.get_bonus_record().awarded == 1
        assert level_stats.get_bonus_record().score == 1000
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
