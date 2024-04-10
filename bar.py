import pygame


class Bar:
    def __init__(self, position, width, height, max_value, bar_colors, draw_outline, outline_color,
                 draw_background, background_color, draw_text, text, text_color):
        self.position = position
        self.width = width
        self.height = height
        self.max_value = max_value

        # Bar colors
        self.bar_colors = bar_colors

        # Outline
        self.draw_outline = draw_outline
        self.outline_color = outline_color

        # Background
        self.draw_background = draw_background
        self.background_color = background_color

        # Text
        self.draw_text = draw_text
        self.text = text
        self.text_color = text_color
        # Load font
        if self.draw_text:
            self.basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 18)

    def change_position(self, position):
        self.position = position

    def draw(self, surface, value, offset=None):
        if offset is None:
            offset = pygame.math.Vector2()

        # Create bar rectangle
        bar_width = (self.width * value) / self.max_value
        bar_rectangle = pygame.rect.Rect(self.position + offset, (bar_width, self.height)).inflate(-8, -8)

        # Calculate percent
        percent = int(100 * value / self.max_value)

        # Draw background
        if self.draw_background:
            background = pygame.rect.Rect(self.position + offset, (self.width, self.height))
            pygame.draw.rect(surface, self.background_color, background)

        # Draw bar
        pygame.draw.rect(surface, self.bar_colors.get_color(percent), bar_rectangle)

        # Blit the text
        if self.draw_text and percent >= 10:
            # Create text
            rendered_text = self.basic_font.render(f'{self.text} {percent}%', True, self.text_color)

            # Set text position
            text_rect = rendered_text.get_rect()
            rendered_text_position = [self.position[0] + bar_width // 2 - text_rect.width // 2,
                                      self.position[1] + self.height // 2 - text_rect.height // 2]

            # Change text and adjust position if it's too long
            if rendered_text.get_rect().width + 50 > bar_width:
                rendered_text = self.basic_font.render(f'{percent}%', True, self.text_color)
                text_rect = rendered_text.get_rect()
                rendered_text_position[0] = self.position[0] + bar_width // 2 - text_rect.width // 2

            surface.blit(rendered_text, rendered_text_position)

        # Draw outline
        if self.draw_outline:
            outline = pygame.rect.Rect(self.position + offset, (self.width, self.height))
            pygame.draw.rect(surface, self.outline_color, outline, 1)
