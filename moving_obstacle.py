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

    def calculate_new_position(self, movement_direction):
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

        return [(new_position_x, new_position_y), (new_map_x, new_map_y)]

    # Note: enemy_sprites, obstacle_sprites, moving_obstacle_sprites should be moved to the constructor
    def check_if_destination_tile_is_empty(self, new_position_x, new_position_y, enemy_sprites, obstacle_sprites, moving_obstacle_sprites):
        for sprite in enemy_sprites:
            source_hit_box = pygame.rect.Rect(new_position_x, new_position_y, settings.TILE_SIZE, settings.TILE_SIZE)
            if sprite.hit_box.colliderect(source_hit_box):
                return False
        for sprite in obstacle_sprites:
            source_hit_box = pygame.rect.Rect(new_position_x, new_position_y, settings.TILE_SIZE, settings.TILE_SIZE)
            if sprite.hit_box.colliderect(source_hit_box):
                return False
        for sprite in moving_obstacle_sprites:
            source_hit_box = pygame.rect.Rect(new_position_x, new_position_y, settings.TILE_SIZE, settings.TILE_SIZE)
            if sprite.hit_box.colliderect(source_hit_box):
                return False

        return True

    # Note: enemy_sprites, obstacle_sprites, moving_obstacle_sprites should be moved to the constructor
    def move_obstacle_if_allowed(self, movement_direction, enemy_sprites, obstacle_sprites, moving_obstacle_sprites):
        # Get old position
        old_position_x, old_position_y = self.position[0], self.position[1]
        # Calculate old position on the map
        old_map_x = old_position_x // settings.TILE_SIZE
        old_map_y = old_position_y // settings.TILE_SIZE

        # Get new position
        [
            (new_position_x, new_position_y),
            (new_map_x, new_map_y)
        ] = self.calculate_new_position(movement_direction)

        # Execute the movement if it's allowed
        if self.check_if_destination_tile_is_empty(new_position_x, new_position_y, enemy_sprites, obstacle_sprites, moving_obstacle_sprites):
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
            # Obstacle has been moved
            return True
        else:
            # Obstacle has not been moved
            return False


