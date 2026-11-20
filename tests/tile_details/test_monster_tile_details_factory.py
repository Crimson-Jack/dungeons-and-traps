import pytest

from src.enums.search_path_algorithm import SearchPathAlgorithm
from src.game_helper import GameHelper
from src.tile_details.monster_tile_details import MonsterTileDetails
from src.tile_details.monster_tile_details_factory import MonsterTileDetailsFactory

# Settings of the monsters hatched from eggs:
# (monster name, speed before the tile size ratio, start delay, energy, damage power, score)
MONSTER_SETTINGS = [
    ('monster-enemy-blue-deaf', 3.2, 20, 100, 2, 50),
    ('monster-enemy-green-deaf', 5.0, 10, 200, 4, 170),
    ('monster-enemy-red-deaf', 6.5, 5, 500, 1, 300),
]


class TestMonsterTileDetailsFactory:
    @pytest.mark.parametrize(('monster_name', 'speed', 'start_delay', 'energy', 'damage_power', 'score'),
                             MONSTER_SETTINGS)
    def test_creates_monster_tile_details_with_settings_of_given_monster(
            self, monster_name, speed, start_delay, energy, damage_power, score):
        tile_details = MonsterTileDetailsFactory.create(monster_name)

        assert type(tile_details) is MonsterTileDetails
        assert tile_details.speed == GameHelper.multiply_by_tile_size_ratio(speed)
        assert tile_details.start_delay == start_delay
        assert tile_details.energy == energy
        assert tile_details.damage_power == damage_power
        assert tile_details.score == score

    @pytest.mark.parametrize('monster_name', [monster_settings[0] for monster_settings in MONSTER_SETTINGS])
    def test_monster_uses_greedy_search_and_attacks_only_when_visible(self, monster_name):
        tile_details = MonsterTileDetailsFactory.create(monster_name)

        assert tile_details.search_path_algorithm == SearchPathAlgorithm.GREEDY_BEST_FIRST_SEARCH
        assert tile_details.attack_only_when_visible is True

    @pytest.mark.parametrize('monster_name', [monster_settings[0] for monster_settings in MONSTER_SETTINGS])
    def test_monster_tile_details_have_no_tile_and_layer(self, monster_name):
        tile_details = MonsterTileDetailsFactory.create(monster_name)

        assert tile_details.tile is None
        assert tile_details.layer is None

    def test_unknown_monster_name_raises_value_error(self):
        with pytest.raises(ValueError, match='Unknown name: monster-enemy-unknown'):
            MonsterTileDetailsFactory.create('monster-enemy-unknown')
