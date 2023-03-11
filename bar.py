import pygame


class Bar:
    def __init__(self, dashboard_surface, position, width, height, max_value, label, color=None):
        self.dashboard_surface = dashboard_surface
        self.position = position
        self.width = width
        self.height = height
        self.max_value = max_value
        self.label = label

        # Color
        self.accent_color = color
        # Colors
        if self.accent_color is None:
            self.accent_color_100 = (0, 51, 0)
            self.accent_color_80 = (51, 102, 0)
            self.accent_color_60 = (102, 102, 0)
            self.accent_color_40 = (102, 51, 0)
            self.accent_color_20 = (102, 0, 0)

        self.outline_color = (135, 135, 135)
        self.text_color = (180, 180, 180)

        # Fonts
        self.basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 18)

        # Create outline rectangle
        self.outline = pygame.rect.Rect(position, (width, height))

    def draw(self, value):
        # Create bar rectangle
        bar_width = (self.width * value) / self.max_value
        bar_rectangle = pygame.rect.Rect(self.position, (bar_width, self.height)).inflate(-8, -8)

        # Calculate percent
        percent = int(100 * value / self.max_value)

        # Text
        if self.label is None:
            text = None
        else:
            # Create text
            text = self.basic_font.render(f'{self.label} {percent} %', True, self.text_color)

            # Set text position
            text_rect = text.get_rect()
            text_position = [self.position[0] + bar_width - text_rect.width - 10,
                             self.position[1] + self.height // 2 - text_rect.height // 2]

            # Change text and adjust position if it's too long
            if text_position[0] < text.get_rect().width:
                text = self.basic_font.render(f'{percent} %', True, self.text_color)
                text_position[0] = self.position[0] + bar_width + 10

        if self.accent_color is None:
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
        else:
            accent_color = self.accent_color

        # Draw bar, blit the text and draw outline
        pygame.draw.rect(self.dashboard_surface, accent_color, bar_rectangle)
        if self.label:
            self.dashboard_surface.blit(text, text_position)
        pygame.draw.rect(self.dashboard_surface, self.outline_color, self.outline, 1)

