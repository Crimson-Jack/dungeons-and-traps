from tile_details import TileDetails
import tmx_helper
import game_helper


class MonsterTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._speed = game_helper.multiply_by_tile_size_ratio(tmx_helper.get_property('speed', 1, self.tile, self.layer))
        self._start_delay = tmx_helper.get_property('start_delay', 10, self.tile, self.layer)
        self._energy = int(tmx_helper.get_property('energy', 100, self.tile, self.layer))
        self._damage_power = int(tmx_helper.get_property('damage_power', 1, self.tile, self.layer))

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
