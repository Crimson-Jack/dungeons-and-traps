from spell import Spell
from spell_tile_details import SpellTileDetails


class LightingSpell(Spell):
    def __init__(self, image, position, groups, game_state, spell_tile_details: SpellTileDetails):
        super().__init__(image, position, groups, game_state)

        self.spell_name = spell_tile_details.spell_name

    def collect(self):
        self.game_state.set_lighting_spell(self.spell_name)
        super().kill()
