from tile_details import TileDetails
import tmx_helper


class KeyAndDoorTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._key_name = tmx_helper.get_property('key_name', '', self.tile, self.layer)

    def __int__(self, key_name):
        self._key_name = key_name

    @property
    def key_name(self):
        return self._key_name

    @classmethod
    def from_properties(cls, key_name):
        instance = cls(None, None)
        instance._key_name = key_name
        return instance
