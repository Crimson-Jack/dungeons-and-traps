import pygame

from settings import Settings
from src.sprites.item_to_collect import ItemToCollect
from src.sprite_helper import SpriteHelper


class Egg(ItemToCollect):
    def __init__(self, position, groups, game_manager):
        super().__init__(groups, game_manager)

        # Sprite animation variables
        self.sprites = SpriteHelper.get_all_egg_sprites()
        self.number_of_sprites = len(self.sprites)
        self.costume_switching_threshold = 100
        self.costume_step_counter = 0
        self.costume_index = 0

        # Image
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

    def collect(self):
        super().kill()

    def update(self):
        if self.number_of_sprites > 1:
            self.change_costume()

        # Increase costume step counter
        self.costume_step_counter += 1

    def change_costume(self):
        # Change costume only if threshold exceeded
        if self.costume_step_counter > self.costume_switching_threshold:

            # Reset counter and increase costume index
            self.costume_step_counter = 0
            self.costume_index += 1

            # If it's the last costume - create a monster
            if self.costume_index >= self.number_of_sprites:
                pygame.event.post(
                    pygame.event.Event(Settings.CREATE_MONSTER_EVENT, {"position": self.rect.topleft}))
                self.kill()
            else:
                # Set new image
                self.image = self.sprites[self.costume_index]