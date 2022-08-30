import pygame


class Debug:
    def __init__(self, x=10, y=10):
        self.enabled = False
        self.text_color = 'Black'
        self.info_list = []
        self.x = x
        self.y = y
        pygame.init()
        self.font = pygame.font.Font(None, 26)

    def add_info(self, info):
        self.info_list.append(info)

    def show(self):

        if self.enabled:
            display_surface = pygame.display.get_surface()
            y_position = 0
            for info in self.info_list:
                debug_surface = self.font.render(str(info), True, self.text_color)
                debug_surface.set_alpha(150)
                debug_rect = debug_surface.get_rect(topleft=(self.x, self.y + y_position))
                display_surface.blit(debug_surface, debug_rect)
                y_position += 20

        # Clear list
        self.info_list.clear()

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_F1]:
            self.enabled = True
            self.text_color = 'Black'
        elif keys[pygame.K_F2]:
            self.enabled = True
            self.text_color = "White"
        elif keys[pygame.K_ESCAPE]:
            self.enabled = False


