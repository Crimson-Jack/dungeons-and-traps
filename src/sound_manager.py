import pygame

from src.enums.sound_effect import SoundEffect
from src.metaclasses.singleton_meta import SingletonMeta


class SoundManager(metaclass=SingletonMeta):
    """
    Singleton that plays the sound effects. All sound effects of SoundEffect are loaded once, when it is created.
    """

    # Folder in sound/sfx/ with the sound effect files
    SFX_SET = 'set_01'

    def __init__(self) -> None:
        """
        Load all sound effects of SoundEffect from sound/sfx/SFX_SET/.
        """
        self._sfx_collection: dict[SoundEffect, pygame.mixer.Sound] = {}
        self._load_sfx_collection()

    def play_sfx(self, sound_effect: SoundEffect) -> None:
        """
        Play the sound effect on a free channel, or on the channel with the longest playing sound when none is free.

        :param sound_effect: sound effect to play
        """
        # Force argument True returns the channel with the longest playing sound when no channel is free
        channel = pygame.mixer.find_channel(True)
        channel.play(self._sfx_collection[sound_effect])

    def _load_sfx_collection(self) -> None:
        for sound_effect in SoundEffect:
            self._sfx_collection[sound_effect] = pygame.mixer.Sound(f'sound/sfx/{self.SFX_SET}/{sound_effect}.ogg')
