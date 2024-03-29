import pygame
import settings
import weapon_type


class Header:
    def __init__(self, screen, header_surface, game_state):
        self.screen = screen
        self.header_surface = header_surface
        self.game_state = game_state

        # Fonts
        self.accent_color = (187, 187, 204)
        self.basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 32)
        self.margin = 16

        # Background and border
        self.border = self.header_surface.get_rect()
        self.border = self.border.inflate(-8, -8)
        self.header_surface.fill((64, 78, 107))
        pygame.draw.rect(self.header_surface, (42, 53, 70), self.border)
        pygame.draw.rect(self.header_surface, (244, 244, 244), self.border, 4)
        self.inner_background_color = 42, 53, 70

        # Surfaces
        self.left_surface = pygame.Surface(
            (settings.WIDTH // 3 - self.margin, settings.HEADER_HEIGHT - self.margin))
        self.center_surface = pygame.Surface(
            (settings.WIDTH // 3 - self.margin, settings.HEADER_HEIGHT - self.margin))
        self.right_surface = pygame.Surface(
            (settings.WIDTH // 3 - self.margin, settings.HEADER_HEIGHT - self.margin))

    def clean(self):
        self.left_surface.fill(self.inner_background_color)
        self.center_surface.fill(self.inner_background_color)
        self.right_surface.fill(self.inner_background_color)

    def draw(self):
        # Left
        level_text = self.basic_font.render(f'Level', True, self.accent_color)
        self.left_surface.blit(level_text, (self.margin, self.left_surface.get_height() // 2 - level_text.get_rect().height // 2))
        self.header_surface.blit(self.left_surface, (self.margin // 2, self.margin // 2))

        # Center
        weapon_type_string = "-"
        if self.game_state.weapon_type == weapon_type.WeaponType.SWORD:
            weapon_type_string = "S"
        elif self.game_state.weapon_type == weapon_type.WeaponType.BOW:
            weapon_type_string = f"B ({self.game_state.number_of_arrows})"

        weapon_text = self.basic_font.render(f'Weapon {weapon_type_string}', True, self.accent_color)
        self.center_surface.blit(weapon_text, (self.margin, self.center_surface.get_height() // 2 - weapon_text.get_rect().height // 2))
        self.header_surface.blit(self.center_surface, (settings.WIDTH // 3 + self.margin // 2, self.margin // 2))

        # Right
        score_text = self.basic_font.render(f'Score', True, self.accent_color)
        self.right_surface.blit(score_text, (self.margin, self.right_surface.get_height() // 2 - score_text.get_rect().height // 2))
        self.header_surface.blit(self.right_surface, (settings.WIDTH * 2 // 3 + self.margin // 2, self.margin // 2))

        # Blit dashboard to the main screen
        self.screen.blit(self.header_surface, (0, 0))
