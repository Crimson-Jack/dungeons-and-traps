from src.enums.search_path_algorithm import SearchPathAlgorithm
from src.game_helper import GameHelper
from src.tile_details.tile_details import TileDetails
from src.tmx_helper import TmxHelper


class MonsterTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._speed = GameHelper.multiply_by_tile_size_ratio(TmxHelper.get_tiled_object_value('speed', 5, self.tile, self.layer))
        self._start_delay = TmxHelper.get_tiled_object_value('start_delay', 5, self.tile, self.layer)
        self._energy = int(TmxHelper.get_tiled_object_value('energy', 500, self.tile, self.layer))
        self._damage_power = int(TmxHelper.get_tiled_object_value('damage_power', 6, self.tile, self.layer))
        self._score = int(TmxHelper.get_tiled_object_value('score', 300, self.tile, self.layer))
        self._search_path_algorithm = TmxHelper.get_tiled_object_value('search_path_algorithm', SearchPathAlgorithm.BREADTH_FIRST_SEARCH, self.tile, self.layer)

    @property
    def speed(self):
        return self._speed

    @property
    def start_delay(self):
        return self._start_delay

    @property
    def energy(self):
        return self._energy

    @property
    def damage_power(self):
        return self._damage_power

    @property
    def score(self):
        return self._score

    @property
    def search_path_algorithm(self):
        return self._search_path_algorithm
