from unittest.mock import Mock

import pygame
import pytest

from settings import Settings
from src.game import Game
from src.level import Level
from src.panels.dashboard import Dashboard
from src.panels.header import Header


def pytest_configure(config):
    # Tests that reach into private members while a refactoring is in progress; review and remove them afterwards
    config.addinivalue_line('markers', 'refactoring: scaffolding test for a refactoring; review and remove afterwards')


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
