import pygame
import custom_draw_sprite
import settings
import game_helper


class ExitPoint(custom_draw_sprite.CustomDrawSprite):
    def __init__(self, image, position, groups, visible):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect.inflate(game_helper.calculate_with_ratio(-30), game_helper.calculate_with_ratio(-30))
        self.visible = visible

    def custom_draw(self, game_surface, offset):
        # Draw sprite if visible
        if self.visible:
            offset_position = self.rect.topleft + offset
            game_surface.blit(self.image, offset_position)
