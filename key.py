import game_helper
from key_and_door_tile_details import KeyAndDoorTileDetails
from item_to_collect import ItemToCollect


class Key(ItemToCollect):
    def __init__(self, image, position, groups, game_state, details: KeyAndDoorTileDetails):
        super().__init__(image, position, groups, game_state)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(-35),
                                         game_helper.multiply_by_tile_size_ratio(-35))
        self.key_name = details.key_name
        self.score = details.score

    def collect(self):
        self.game_state.collect_key(self)
        super().kill()
