import game_helper
from diamond_tile_details import DiamondTileDetails
from item_to_collect import ItemToCollect


class Diamond(ItemToCollect):
    def __init__(self, image, position, groups, game_state, details: DiamondTileDetails):
        super().__init__(image, position, groups, game_state)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(-35),
                                         game_helper.multiply_by_tile_size_ratio(-35))

        self.score = details.score

    def collect(self):
        self.game_state.collect_diamond(self)
        super().kill()
