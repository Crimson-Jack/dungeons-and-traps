from tile_details import TileDetails
import tmx_helper


class TeleportTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._destination = tmx_helper.get_property('destination', '', self.tile, self.layer)
        self._port_name = tmx_helper.get_property('port_name', '', self.tile, self.layer)

    @property
    def destination(self):
        return self._destination

    @property
    def port_name(self):
        return self._port_name
