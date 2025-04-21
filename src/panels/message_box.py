import pygame


class MessageBox:
    def __init__(self, screen, width, height, top_margin, background_color, border_color, messages):
        self.screen = screen
        self.width = width
        self.height = height
        self.background_color = background_color
        self.border_color = border_color
        self.messages = messages

        # Rectangle position - centered
        self.rect_position = (self.screen.get_rect().width // 2 - width // 2,
                              self.screen.get_rect().height // 2 - height // 2)

        # Text position - centered
        self.text_position = (self.screen.get_rect().width // 2,
                              self.screen.get_rect().height // 2 - height // 2 + top_margin)

        self.text_layers = list()
        self.convert_messages_to_text_layers()

    def convert_messages_to_text_layers(self):
        y_offset = 0
        for message in self.messages:
            basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', message.size)
            text_layer = basic_font.render(message.text, True, message.color, self.background_color)
            self.text_layers.append((text_layer, text_layer.get_size()[0] // 2, y_offset))
            y_offset += text_layer.get_size()[1]

    def draw(self):
        rectangle = pygame.rect.Rect(self.rect_position[0], self.rect_position[1], self.width, self.height)
        border = rectangle.inflate(-8, -8)

        pygame.draw.rect(self.screen, self.background_color, rectangle)

        pygame.draw.rect(self.screen, self.background_color, border)
        pygame.draw.rect(self.screen, self.border_color, border, 4)

        for text_layer, x_offset, y_offset in self.text_layers:
            self.screen.blit(text_layer, (self.text_position[0] - x_offset, self.text_position[1] + y_offset))
