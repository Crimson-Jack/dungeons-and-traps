import game_helper
from item_to_collect import ItemToCollect


class Spell(ItemToCollect):
    def __init__(self, image, position, groups, game_state):
        super().__init__(image, position, groups, game_state)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(-10),
                                         game_helper.multiply_by_tile_size_ratio(-10))
