from tile_details import TileDetails
import tmx_helper
import game_helper


class GhostTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._speed = game_helper.multiply_by_tile_size_ratio(tmx_helper.get_property('speed', 1, self.tile, self.layer))

    @property
    def speed(self):
        return self._speed
