from src.sprites.spell import Spell
from src.tile_details.spell_tile_details import SpellTileDetails


class LightingSpell(Spell):
    def __init__(self, image, position, groups, game_manager, spell_tile_details: SpellTileDetails):
        super().__init__(image, position, groups, game_manager)

        self.spell_name = spell_tile_details.spell_name

    def collect(self):
        self.game_manager.set_lighting_spell(self.spell_name)
        super().kill()
