import pygame
import settings
import direction


class MovingObstacle(pygame.sprite.Sprite):
    def __init__(self, image, position, groups, obstacle_map):
        super().__init__(groups)
        self.position = position
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.obstacle_map = obstacle_map

    def move_object(self, movement_direction):
        is_blocked = False

        # Get old position
        old_position_x, old_position_y = self.position[0], self.position[1]
        # Calculate old position on the map
        old_map_x = old_position_x // settings.TILE_SIZE
        old_map_y = old_position_y // settings.TILE_SIZE

        # Check if movement is possible
        new_position_x, new_position_y = 0, 0

        # Calculate a new position
        if movement_direction == direction.Direction.RIGHT:
            new_position_x = self.position[0] + settings.TILE_SIZE
            new_position_y = self.position[1]
        elif movement_direction == direction.Direction.LEFT:
            new_position_x = self.position[0] - settings.TILE_SIZE
            new_position_y = self.position[1]
        elif movement_direction == direction.Direction.UP:
            new_position_x = self.position[0]
            new_position_y = self.position[1] - settings.TILE_SIZE
        elif movement_direction == direction.Direction.DOWN:
            new_position_x = self.position[0]
            new_position_y = self.position[1] + settings.TILE_SIZE
        elif movement_direction == direction.Direction.RIGHT_UP:
            is_blocked = True
        elif movement_direction == direction.Direction.RIGHT_DOWN:
            is_blocked = True
        elif movement_direction == direction.Direction.LEFT_UP:
            is_blocked = True
        elif movement_direction == direction.Direction.LEFT_DOWN:
            is_blocked = True

        # Calculate new position on the map
        new_map_x = new_position_x // settings.TILE_SIZE
        new_map_y = new_position_y // settings.TILE_SIZE

        if self.obstacle_map[new_map_y][new_map_x] == 0:
            # Set new coordinates
            self.position = [new_position_x, new_position_y]
            # Change position
            self.rect.x = int(self.position[0])
            self.rect.y = int(self.position[1])
            # Change obstacle map
            self.obstacle_map[old_map_y][old_map_x] = 0
            self.obstacle_map[new_map_y][new_map_x] = 1
            # Raise event to refresh obstacle map
            pygame.event.post(pygame.event.Event(settings.REFRESH_OBSTACLE_MAP_EVENT))
        else:
            is_blocked = True

        return is_blocked




