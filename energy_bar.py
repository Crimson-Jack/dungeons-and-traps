import pygame


class EnergyBar:
    def __init__(self, dashboard_surface, position, width, height, max_energy_value):
        self.dashboard_surface = dashboard_surface
        self.position = position
        self.width = width
        self.height = height
        self.max_energy_value = max_energy_value

        # Colors and fonts
        self.accent_color_100 = (0, 51, 0)
        self.accent_color_80 = (51, 102, 0)
        self.accent_color_60 = (102, 102, 0)
        self.accent_color_40 = (102, 51, 0)
        self.accent_color_20 = (102, 0, 0)
        self.outline_color = (135, 135, 135)
        self.text_color = (180, 180, 180)
        self.basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 18)

        # Create outline rectangle
        self.outline = pygame.rect.Rect(position, (width, height))

    def draw(self, value):
        # Create bar rectangle
        energy_bar_width = (self.width * value) / self.max_energy_value
        energy_bar = pygame.rect.Rect(self.position, (energy_bar_width, self.height)).inflate(-8, -8)

        # Text with percent
        percent = int(100 * value / self.max_energy_value)
        energy_text = self.basic_font.render(f'Energy {percent} %', True, self.text_color)
        # Set text position
        energy_text_rect = energy_text.get_rect()
        energy_text_position = [self.position[0] + energy_bar_width - energy_text_rect.width - 10, self.position[1] + self.height // 2 - energy_text_rect.height // 2]
        if energy_text_position[0] < energy_text.get_rect().width:
            energy_text_position[0] = self.position[0] + energy_bar_width + 10

        # Choose bar color
        if percent > 80:
            accent_color = self.accent_color_100
        elif percent > 60:
            accent_color = self.accent_color_80
        elif percent > 40:
            accent_color = self.accent_color_60
        elif percent > 20:
            accent_color = self.accent_color_40
        elif percent >= 0:
            accent_color = self.accent_color_20

        # Draw bar, blit the text and draw outline
        pygame.draw.rect(self.dashboard_surface, accent_color, energy_bar)
        self.dashboard_surface.blit(energy_text, energy_text_position)
        pygame.draw.rect(self.dashboard_surface, self.outline_color, self.outline, 1)

