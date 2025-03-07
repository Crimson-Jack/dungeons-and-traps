import pygame
import settings
import game_helper
from teleport_tile_details import TeleportTileDetails


class Teleport(pygame.sprite.Sprite):
    def __init__(self, image, position, groups, details: TeleportTileDetails):
        super().__init__(*groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(int(game_helper.multiply_by_tile_size_ratio(-60)),
                                         int(game_helper.multiply_by_tile_size_ratio(-60)))
        self.destination = details.destination
        self.port_name = details.port_name
        self.selected = False

    def select(self):
        self.selected = True

    def unselect(self):
        self.selected = False

    def check_is_selected(self):
        return self.selected
