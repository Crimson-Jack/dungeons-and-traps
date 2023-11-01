import pygame
import settings
import direction


class GameState:
    def __init__(self):
        self.game_over = False
        self.diamonds = list()
        self.collected_diamonds = 0
        self.max_energy = 800
        self.energy = self.max_energy
        self.max_power = 100
        self.power = 0
        self.player_tile_position = (0, 0)
        self.player_movement_vector = pygame.Vector2()
        self.player_movement_direction = direction.Direction.RIGHT
        self.player_is_using_weapon = False

    def add_diamond(self, diamond):
        self.diamonds.append(diamond)

    def collect_diamond(self):
        self.collected_diamonds += 1
        pygame.event.post(pygame.event.Event(settings.COLLECT_DIAMOND_EVENT))
        if self.collected_diamonds == len(self.diamonds):
            pygame.event.post(pygame.event.Event(settings.EXIT_POINT_IS_OPEN_EVENT))

    def decrease_energy(self):
        self.energy -= 1
        if self.energy < 0:
            self.energy = 0
            self.game_over = True
            pygame.event.post(pygame.event.Event(settings.GAME_OVER_EVENT))
        else:
            pygame.event.post(pygame.event.Event(settings.DECREASE_ENERGY_EVENT))

    def change_power(self, value):
        self.power = value
        if self.power < 0:
            self.power = 0
        if self.power > self.max_power:
            self.power = self.max_power
        pygame.event.post(pygame.event.Event(settings.CHANGE_POWER_EVENT))

    def level_completed(self):
        if self.collected_diamonds == len(self.diamonds):
            # Note: Only for temporary solution
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

    def set_player_is_using_weapon(self, status):
        self.player_is_using_weapon = status

    def set_player_tile_position(self, position):
        # print(position)
        self.player_tile_position = position
        pygame.event.post(pygame.event.Event(settings.PLAYER_TILE_POSITION_CHANGED_EVENT))
