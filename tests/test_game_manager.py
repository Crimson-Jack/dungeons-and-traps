from unittest.mock import Mock

import pytest

import src.game_manager
from src.game_manager import GameManager


# SoundManager loads sound files through pygame.mixer, which is irrelevant for the game state
@pytest.fixture
def game_manager(monkeypatch):
    monkeypatch.setattr(src.game_manager, 'SoundManager', Mock())
    return GameManager()


def create_key(key_name):
    return Mock(key_name=key_name)


class TestIsKeyCollected:
    def test_returns_false_when_no_key_is_collected(self, game_manager):
        assert game_manager.is_key_collected('red') is False

    def test_returns_true_when_key_with_given_name_is_collected(self, game_manager):
        game_manager.collected_keys = [create_key('blue'), create_key('red')]

        assert game_manager.is_key_collected('red') is True

    def test_returns_false_when_only_keys_with_other_names_are_collected(self, game_manager):
        game_manager.collected_keys = [create_key('blue'), create_key('green')]

        assert game_manager.is_key_collected('red') is False
