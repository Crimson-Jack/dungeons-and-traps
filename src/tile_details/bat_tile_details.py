from src.tile_details.tile_details import TileDetails
import tmx_helper
import game_helper


class BatTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._speed = game_helper.multiply_by_tile_size_ratio(tmx_helper.get_tiled_object_value('speed', 1, self.tile, self.layer))
        self._start_delay = tmx_helper.get_tiled_object_value('start_delay', 10, self.tile, self.layer)
        self._energy = int(tmx_helper.get_tiled_object_value('energy', 100, self.tile, self.layer))
        self._damage_power = int(tmx_helper.get_tiled_object_value('damage_power', 1, self.tile, self.layer))
        self._score = int(tmx_helper.get_tiled_object_value('score', 0, self.tile, self.layer))
        self._points_path = game_helper.convert_string_to_list_of_tuples(
            tmx_helper.get_tiled_object_value('points_path', '', self.tile, self.layer))

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
    def points_path(self):
        return self._points_path
