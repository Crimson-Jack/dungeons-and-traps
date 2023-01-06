import pygame
import settings
import direction


class GameState:
    def __init__(self):
        self.game_over = False
        self.required_diamonds = 0
        self.diamonds = 0
        self.max_energy_value = 800
        self.energy = self.max_energy_value
        self.player_movement_vector = pygame.Vector2()
        self.player_movement_direction = direction.Direction.RIGHT

    def set_number_of_required_diamonds(self, value):
        self.required_diamonds = value

    def add_diamond(self):
        self.diamonds += 1
        pygame.event.post(pygame.event.Event(settings.ADD_DIAMOND_EVENT))
        if self.diamonds == self.required_diamonds:
            pygame.event.post(pygame.event.Event(settings.EXIT_POINT_IS_OPEN_EVENT))

    def decrease_energy(self):
        self.energy -= 1
        if self.energy < 0:
            self.energy = 0
            self.game_over = True
            pygame.event.post(pygame.event.Event(settings.GAME_OVER_EVENT))
        else:
            pygame.event.post(pygame.event.Event(settings.DECREASE_ENERGY_EVENT))

    def level_completed(self):
        if self.diamonds == self.required_diamonds:
            # NOTE: Only for temporary solution
            self.game_over = True
            pygame.event.post(pygame.event.Event(settings.NEXT_LEVEL_EVENT))

    def set_player_movement(self, x, y):
        # Set vector
        self.player_movement_vector.x += x
        self.player_movement_vector.y += y

        # Set direction
        if self.player_movement_vector.y == 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = direction.Direction.RIGHT
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = direction.Direction.RIGHT_DOWN
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x == 0:
            self.player_movement_direction = direction.Direction.DOWN
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = direction.Direction.LEFT_DOWN
        elif self.player_movement_vector.y == 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = direction.Direction.LEFT
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = direction.Direction.LEFT_UP
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x == 0:
            self.player_movement_direction = direction.Direction.UP
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = direction.Direction.RIGHT_UP
