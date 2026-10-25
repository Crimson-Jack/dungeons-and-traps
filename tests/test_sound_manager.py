from unittest.mock import Mock

import pygame
import pytest

from src.enums.sound_effect import SoundEffect
from src.metaclasses.singleton_meta import SingletonMeta
from src.sound_manager import SoundManager

# Every test resets the Singleton through the private instances of SingletonMeta
pytestmark = pytest.mark.refactoring


def sound_file_path(sound_effect):
    return f'sound/sfx/{SoundManager.SFX_SET}/{sound_effect}.ogg'


# A new SoundManager for every test, so each one loads the sounds through its own mocks
@pytest.fixture(autouse=True)
def reset_sound_manager_instance():
    SingletonMeta._instances.pop(SoundManager, None)
    yield
    SingletonMeta._instances.pop(SoundManager, None)


# Each mocked sound is its file path, so a played sound shows which file it was loaded from
@pytest.fixture
def sound_mock(monkeypatch):
    sound_mock = Mock(side_effect=lambda path: path)
    monkeypatch.setattr(pygame.mixer, 'Sound', sound_mock)
    return sound_mock


@pytest.fixture
def channel_mock(monkeypatch):
    channel_mock = Mock()
    monkeypatch.setattr(pygame.mixer, 'find_channel', Mock(return_value=channel_mock))
    return channel_mock


class TestSoundManagerLoading:
    def test_loads_sound_of_every_sound_effect_from_sfx_set(self, sound_mock):
        SoundManager()
        loaded_paths = [call.args[0] for call in sound_mock.call_args_list]
        assert loaded_paths == [sound_file_path(sound_effect) for sound_effect in SoundEffect]

    def test_second_creation_returns_same_instance_without_loading_again(self, sound_mock):
        first_sound_manager = SoundManager()
        second_sound_manager = SoundManager()
        assert second_sound_manager is first_sound_manager
        assert sound_mock.call_count == len(SoundEffect)


class TestSoundManagerPlaySfx:
    def test_plays_sound_of_sound_effect_on_found_channel(self, sound_mock, channel_mock):
        SoundManager().play_sfx(SoundEffect.COLLECT_DIAMOND)
        channel_mock.play.assert_called_once_with(sound_file_path(SoundEffect.COLLECT_DIAMOND))

    def test_finds_channel_with_force(self, sound_mock, channel_mock):
        SoundManager().play_sfx(SoundEffect.COLLECT_KEY)
        pygame.mixer.find_channel.assert_called_once_with(True)
