import pygame


class BlastEffect:
    def __init__(self, game_surface, steps: int, color, max_size: tuple[int, int]):
        self.game_surface = game_surface
        self.width = max_size[0]
        self.height = max_size[1]
        self.step_x = self.width / steps
        self.step_y = self.height / steps
        self.color = color
        self.visible = False
        self.base_rectangle = pygame.rect.Rect(0, 0, 0, 0)
        self.rectangle = pygame.rect.Rect(0, 0, 0, 0)
        self.counter = 1

    def reset(self):
        self.counter = 1

        # Set base rectangle properties
        self.base_rectangle.width = int(self.step_x)
        self.base_rectangle.height = int(self.step_y)
        top_left_x = int(self.width / 2 - self.step_x / 2)
        top_left_y = int(self.height / 2 - self.step_y / 2)
        self.base_rectangle.topleft = top_left_x, top_left_y

        # Create a copy
        self.rectangle = pygame.rect.Rect(self.base_rectangle)

    def run(self):
        self.reset()
        self.visible = True

    def stop(self):
        self.visible = False

    def update(self):
        if self.visible:
            if self.rectangle.width < self.width and self.rectangle.height < self.height:
                self.rectangle = self.base_rectangle.inflate(self.step_x * self.counter, self.step_y * self.counter)
                self.counter += 1
            else:
                self.stop()

    def draw(self):
        if self.visible:
            pygame.draw.rect(self.game_surface, self.color, self.rectangle)
