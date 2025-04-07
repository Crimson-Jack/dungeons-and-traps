from tile_details import TileDetails
import tmx_helper
import game_helper


class SpiderTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._speed = game_helper.multiply_by_tile_size_ratio(tmx_helper.get_tiled_object_value('speed', 1, self.tile, self.layer))
        self._net_length = int(tmx_helper.get_tiled_object_value('net_length', 1, self.tile, self.layer))
        self._motion_schedule = game_helper.convert_string_to_tuple(tmx_helper.get_tiled_object_value('motion_schedule', '', self.tile, self.layer))
        self._energy = int(tmx_helper.get_tiled_object_value('energy', 100, self.tile, self.layer))
        self._damage_power = int(tmx_helper.get_tiled_object_value('damage_power', 1, self.tile, self.layer))
        self._score = int(tmx_helper.get_tiled_object_value('score', 0, self.tile, self.layer))

    @property
    def speed(self):
        return self._speed

    @property
    def net_length(self):
        return self._net_length

    @property
    def motion_schedule(self):
        return self._motion_schedule

    @property
    def energy(self):
        return self._energy

    @property
    def damage_power(self):
        return self._damage_power

    @property
    def score(self):
        return self._score
