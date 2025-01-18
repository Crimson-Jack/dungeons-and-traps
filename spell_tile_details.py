from tile_details import TileDetails
import tmx_helper


class SpellTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._spell_name = tmx_helper.get_property('spell_name', '', self.tile, self.layer)

    @property
    def spell_name(self):
        return self._spell_name
