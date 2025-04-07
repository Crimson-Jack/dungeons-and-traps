from tile_details import TileDetails
import tmx_helper


class KeyAndDoorTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._key_name = tmx_helper.get_tiled_object_value('key_name', '', self.tile, self.layer)
        self._score = int(tmx_helper.get_tiled_object_value('score', 0, self.tile, self.layer))

    def __int__(self, key_name):
        self._key_name = key_name

    @property
    def key_name(self):
        return self._key_name

    @property
    def score(self):
        return self._score

    @classmethod
    def from_properties(cls, key_name, score):
        instance = cls(None, None)
        instance._key_name = key_name
        instance._score = score
        return instance
