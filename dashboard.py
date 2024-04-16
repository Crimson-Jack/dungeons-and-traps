import pygame
import game_helper
import settings
import sprite_helper
from bar import Bar
from color_set import ColorSet
from diamond import Diamond
from key import Key
from key_and_door_tile_details import KeyAndDoorTileDetails
from diamond_tile_details import DiamondTileDetails


class Dashboard:
    def __init__(self, screen, dashboard_surface, game_state):
        self.screen = screen
        self.dashboard_surface = dashboard_surface
        self.game_state = game_state

        # Life image
        self.life_image = sprite_helper.get_life_sprite()

        # Fonts
        self.text_color = settings.TEXT_COLOR
        self.basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 24)
        self.text_adjustment = 2
        self.margin = 16

        # Background and border
        self.border = self.dashboard_surface.get_rect()
        self.border = self.border.inflate(-8, -8)
        self.dashboard_surface.fill(settings.SURFACE_COLOR)
        pygame.draw.rect(self.dashboard_surface, settings.BACKGROUND_COLOR, self.border)
        pygame.draw.rect(self.dashboard_surface, settings.BORDER_COLOR, self.border, 4)
        self.inner_background_color = settings.BACKGROUND_COLOR

        # Surfaces
        self.left_top_surface = pygame.Surface(
            (settings.WIDTH // 2 - self.margin, settings.DASHBOARD_HEIGHT // 2 - self.margin // 2))
        self.right_top_surface = pygame.Surface(
            (settings.WIDTH // 2 - self.margin, settings.DASHBOARD_HEIGHT // 2 - self.margin // 2))
        self.left_bottom_surface = pygame.Surface(
            (settings.WIDTH // 2 - self.margin, settings.DASHBOARD_HEIGHT // 2 - self.margin // 2))
        self.right_bottom_surface = pygame.Surface(
            (settings.WIDTH // 2 - self.margin, settings.DASHBOARD_HEIGHT // 2 - self.margin // 2))

        # Energy bar
        self.energy_bar_margin = 20
        bar_width = self.right_top_surface.get_width() - 2 * self.energy_bar_margin
        bar_height = 25
        bar_left = self.energy_bar_margin
        bar_top = self.right_top_surface.get_height() // 2 - (bar_height // 2)
        bar_colors = ColorSet([
                ((0, 20), (255, 60, 0)),        # Red
                ((21, 40), (255, 158, 87)),     # Dark orange
                ((41, 60), (243, 244, 180)),    # Rotten green
                ((61, 80), (189, 244, 180)),    # Light green
                ((81, 100), (122, 231, 104))    # Dark green
            ])
        self.energy_bar = Bar((bar_left, bar_top), bar_width, bar_height, self.game_state.player_max_energy,
                              bar_colors, True, settings.BORDER_COLOR, True,
                              settings.SURFACE_COLOR, True, 'Energy', settings.BAR_TEXT_COLOR)

    def clean(self):
        self.left_top_surface.fill(self.inner_background_color)
        self.right_top_surface.fill(self.inner_background_color)
        self.left_bottom_surface.fill(self.inner_background_color)
        self.right_bottom_surface.fill(self.inner_background_color)

    def draw(self):
        self.draw_energy_bar(self.left_top_surface)
        self.draw_keys(self.right_top_surface)
        self.draw_lives(self.left_bottom_surface)
        self.draw_diamonds(self.right_bottom_surface)

        # Blit each surface to the dashboard
        self.dashboard_surface.blit(self.left_top_surface, (self.margin // 2, self.margin // 2))
        self.dashboard_surface.blit(self.right_top_surface, (settings.WIDTH // 2 + self.margin // 2, self.margin // 2))
        self.dashboard_surface.blit(self.left_bottom_surface, (self.margin // 2, settings.DASHBOARD_HEIGHT // 2))
        self.dashboard_surface.blit(self.right_bottom_surface, (settings.WIDTH // 2 + self.margin // 2, settings.DASHBOARD_HEIGHT // 2))

        # Blit dashboard to the main screen
        self.screen.blit(self.dashboard_surface, (0, settings.HEIGHT - settings.DASHBOARD_HEIGHT))

    def draw_lives(self, surface):
        lives_counter_text = self.basic_font.render(f'Lives', True, self.text_color)
        surface.blit(lives_counter_text, (self.margin * 2, self.left_top_surface.get_height() // 2 - lives_counter_text.get_rect().height // 2 - self.text_adjustment))

        count = 0
        for item in range(self.game_state.lives):
            surface.blit(self.life_image, (self.margin * 3 + lives_counter_text.get_width() + (count * game_helper.BASE_TILE_SIZE), 0))
            count += 1

    def draw_energy_bar(self, surface):
        self.energy_bar.draw(surface, self.game_state.player_energy)

    def draw_keys(self, surface):
        keys_text = self.basic_font.render(f'Keys', True, self.text_color)
        surface.blit(keys_text, (self.margin * 2, self.right_bottom_surface.get_height() // 2 - keys_text.get_rect().height // 2 - self.text_adjustment))

        count = 0
        for item in self.game_state.keys:
            if item.alive():
                # Copy sprite for dashboard - semi transparent
                transparent_image = Key(item.base_size_image, item.rect.topleft, list(), KeyAndDoorTileDetails.from_properties(item.key_name))
                transparent_image.base_size_image.set_alpha(100)
                surface.blit(transparent_image.base_size_image, (self.margin * 3 + keys_text.get_width() + (count * game_helper.BASE_TILE_SIZE), 0))
            else:
                # Use original sprite
                surface.blit(item.base_size_image, (self.margin * 3 + keys_text.get_width() + (count * game_helper.BASE_TILE_SIZE), 0))
            count += 1

    def draw_diamonds(self, surface):
        diamonds_text = self.basic_font.render(f'Gems', True, self.text_color, )
        surface.blit(diamonds_text, (self.margin * 2, self.right_bottom_surface.get_height() // 2 - diamonds_text.get_rect().height // 2 - self.text_adjustment))

        count = 0
        for item in self.game_state.diamonds:
            if item.alive():
                # Copy sprite for dashboard - semi transparent
                transparent_image = Diamond(item.base_size_image, item.rect.topleft, list(), DiamondTileDetails.from_properties(item.score))
                transparent_image.base_size_image.set_alpha(100)
                surface.blit(transparent_image.base_size_image, (self.margin * 3 + diamonds_text.get_width() + (count * game_helper.BASE_TILE_SIZE), 0))
            else:
                # Use original sprite
                surface.blit(item.base_size_image, (self.margin * 3 + diamonds_text.get_width() + (count * game_helper.BASE_TILE_SIZE), 0))
            count += 1
