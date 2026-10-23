from unittest.mock import Mock

import pygame
import pytest

import src.game_manager
from settings import Settings
from src.custom_event_controller import CustomEventController
from src.game import Game
from src.game_manager import GameManager
from src.keyboard_controller import KeyboardController
from src.level import Level
from src.panels.dashboard import Dashboard
from src.panels.header import Header
from src.screen_manager import ScreenManager


class GameUnderTest:
    """Real game for integration tests; the only place that reads the private components of Game."""

    def __init__(self, game: Game) -> None:
        self.game = game

    @property
    def game_manager(self) -> GameManager:
        return self.game._game_manager

    @property
    def screen_manager(self) -> ScreenManager:
        return self.game._screen_manager

    @property
    def keyboard_controller(self) -> KeyboardController:
        return self.game._keyboard_controller

    @property
    def custom_event_controller(self) -> CustomEventController:
        return self.game._custom_event_controller


def pytest_configure(config):
    # Tests that reach into private members while a refactoring is in progress; review and remove them afterwards
    config.addinivalue_line('markers', 'refactoring: scaffolding test for a refactoring; review and remove afterwards')


# Game() calls pygame.init() and loads level 1 in its constructor, so the SDL drivers must be
# switched to dummy before construction and Pygame must be shut down after every test.
@pytest.fixture
def new_game(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER', 'dummy')
    monkeypatch.setattr(Settings, 'FULL_SCREEN_MODE', False)

    game = GameUnderTest(Game())
    yield game

    pygame.event.clear()
    pygame.quit()


# Most integration tests start from the first page, as the player does after the studio and loading pages
@pytest.fixture
def game(new_game):
    new_game.screen_manager.dispose_studio_page()
    new_game.screen_manager.show_first_page()
    return new_game


# Replaces the level and both panels with mocks so custom events can be checked by the calls the controllers make.
@pytest.fixture
def game_with_mocked_components(game):
    game.screen_manager.level = Mock(spec=Level)
    game.screen_manager.header = Mock(spec=Header)
    game.screen_manager.dashboard = Mock(spec=Dashboard)
    pygame.event.clear()
    return game


@pytest.fixture
def set_timer_mock(monkeypatch):
    set_timer_mock = Mock()
    monkeypatch.setattr(pygame.time, 'set_timer', set_timer_mock)
    return set_timer_mock


# SoundManager loads sound files through pygame.mixer, which is irrelevant for the game state
@pytest.fixture
def game_manager(monkeypatch):
    monkeypatch.setattr(src.game_manager, 'SoundManager', Mock())
    return GameManager()


# pygame.event.post needs an initialized pygame; the mock records the posted events instead
@pytest.fixture
def post_event_mock(monkeypatch):
    post_event_mock = Mock()
    monkeypatch.setattr(pygame.event, 'post', post_event_mock)
    return post_event_mock
