from unittest.mock import Mock

import pygame
import pytest

import src.sprites.bow_powerup
import src.sprites.energy_powerup
import src.sprites.explosion_powerup
import src.sprites.life_powerup
import src.sprites.sword_powerup
from settings import Settings
from src.sprites.bow_powerup import BowPowerup
from src.sprites.energy_powerup import EnergyPowerup
from src.sprites.explosion_powerup import ExplosionPowerup
from src.sprites.life_powerup import LifePowerup
from src.sprites.powerup_factory import PowerupFactory
from src.sprites.sword_powerup import SwordPowerup
from src.tile_details.powerup_tile_details import PowerupTileDetails

POWERUP_VOLUME = 7
POSITION = (64, 128)


# SoundManager loads sound files through pygame.mixer, which is irrelevant for creating powerups
@pytest.fixture(autouse=True)
def sound_manager_mock(monkeypatch):
    for powerup_module in (src.sprites.bow_powerup, src.sprites.energy_powerup, src.sprites.explosion_powerup,
                           src.sprites.life_powerup, src.sprites.sword_powerup):
        monkeypatch.setattr(powerup_module, 'SoundManager', Mock())


def create_tile_details(powerup_name: str) -> Mock:
    return Mock(spec=PowerupTileDetails, powerup_name=powerup_name, powerup_volume=POWERUP_VOLUME)


def create_powerup(powerup_name: str, groups: list | None = None, game_manager: Mock | None = None):
    return PowerupFactory.create(create_tile_details(powerup_name),
                                 image=pygame.Surface((16, 16)),
                                 position=POSITION,
                                 groups=groups if groups is not None else [],
                                 game_manager=game_manager if game_manager is not None else Mock())


class TestPowerupFactory:
    @pytest.mark.parametrize(('powerup_name', 'expected_class'), [
        ('sword', SwordPowerup),
        ('bow', BowPowerup),
        ('explosion', ExplosionPowerup),
        ('energy', EnergyPowerup),
        ('life', LifePowerup),
    ])
    def test_creates_powerup_of_given_name(self, powerup_name, expected_class):
        powerup = create_powerup(powerup_name)

        assert type(powerup) is expected_class

    @pytest.mark.parametrize('powerup_name', ['sword', 'bow', 'explosion', 'energy', 'life'])
    def test_powerup_gets_position_groups_and_game_manager(self, powerup_name):
        group = pygame.sprite.Group()
        game_manager = Mock()

        powerup = create_powerup(powerup_name, groups=[group], game_manager=game_manager)

        assert powerup.rect.topleft == POSITION
        assert powerup.rect.size == (Settings.TILE_SIZE, Settings.TILE_SIZE)
        assert powerup in group
        assert powerup.game_manager is game_manager

    def test_bow_gets_powerup_volume_as_number_of_arrows(self):
        assert create_powerup('bow').number_of_arrows == POWERUP_VOLUME

    def test_explosion_gets_powerup_volume_as_number_of_explosions(self):
        assert create_powerup('explosion').number_of_explosions == POWERUP_VOLUME

    def test_energy_gets_powerup_volume_as_volume(self):
        assert create_powerup('energy').volume == POWERUP_VOLUME

    def test_unknown_powerup_name_raises_value_error(self):
        with pytest.raises(ValueError, match='Unknown powerup name'):
            create_powerup('unknown-powerup')
