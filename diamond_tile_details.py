from tile_details import TileDetails
import tmx_helper


class DiamondTileDetails(TileDetails):
    def __init__(self, tile, layer):
        super().__init__(tile, layer)

        self._score = int(tmx_helper.get_property('score', 0, self.tile, self.layer))

    @property
    def score(self):
        return self._score

    @classmethod
    def from_properties(cls, score):
        instance = cls(None, None)
        instance._score = score
        return instance
