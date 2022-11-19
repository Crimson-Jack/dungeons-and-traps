import pygame


class BlastEffect():
    def __init__(self, game_surface, width, height, steps, color):
        self.game_surface = game_surface
        self.width = width
        self.height = height
        self.step_x = self.width // steps
        self.step_y = self.height // steps
        self.color = color
        self.rectangle = pygame.rect.Rect(0, 0, 0, 0)
        self.visible = False

    def reset_rectangle(self):
        self.rectangle.topleft = (self.width // 2 - self.step_x // 2, self.height // 2 - self.step_y // 2)
        self.rectangle.width = self.step_x
        self.rectangle.height = self.step_y

    def run(self):
        self.reset_rectangle()
        self.visible = True

    def stop(self):
        self.visible = False

    def update(self):
        # Gradually increase the size of the rectangle
        if self.visible:
            if self.rectangle.width < self.width and self.rectangle.height < self.height:
                self.rectangle = self.rectangle.inflate(self.step_x, self.step_y)
            else:
                self.stop()

    def draw(self):
        if self.visible:
            pygame.draw.rect(self.game_surface, self.color, self.rectangle)
