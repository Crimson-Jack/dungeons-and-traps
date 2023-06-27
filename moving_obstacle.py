import pygame
import game_helper
import settings
import direction
from custom_draw_sprite import CustomDrawSprite
from bar import Bar


class MovingObstacle(CustomDrawSprite):
    def __init__(self, image, position, groups, obstacle_map_items, collision_sprites, game_state):
        super().__init__(groups)
        self.position = position
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.obstacle_map_items = obstacle_map_items
        self.collision_sprites = collision_sprites
        self.game_state = game_state

        # Power variables to move obstacle
        self.power = 0
        self.power_step = 5
        self.power_needed_to_move_obstacle = self.game_state.max_power

        # Create power bar
        bar_width = settings.TILE_SIZE
        bar_height = game_helper.multiply_by_tile_size_ratio(12)
        bar_left, bar_top = self.get_bar_position()
        self.power_bar = Bar((bar_left, bar_top), bar_width, bar_height, self.game_state.max_power, None, (102, 51, 0))

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

    def check_if_destination_tile_is_empty(self, new_position_x, new_position_y):
        for collision_sprite_group in self.collision_sprites:
            for sprite in collision_sprite_group:
                source_hit_box = pygame.rect.Rect(new_position_x, new_position_y, settings.TILE_SIZE,
                                                  settings.TILE_SIZE)
                if sprite.hit_box.colliderect(source_hit_box):
                    return False
        return True

    def move_obstacle_if_allowed(self, movement_direction):
        # Increase power
        self.increase_power()

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
        if self.check_if_destination_tile_is_empty(new_position_x, new_position_y):
            if self.power > self.power_needed_to_move_obstacle:
                # Set new coordinates
                self.position = [new_position_x, new_position_y]
                # Set a new bar position
                bar_left, bar_top = self.get_bar_position()
                self.power_bar.change_position((bar_left, bar_top))
                # Change position
                self.rect.x = int(self.position[0])
                self.rect.y = int(self.position[1])
                # Change obstacle map
                self.obstacle_map_items[old_map_y][old_map_x] = 0
                self.obstacle_map_items[new_map_y][new_map_x] = 1
                # Raise event to refresh obstacle map
                pygame.event.post(pygame.event.Event(settings.REFRESH_OBSTACLE_MAP_EVENT))
                # Reset power
                self.reset_power()
                # Obstacle has been moved
                return True
        else:
            # Obstacle has not been moved
            return False

    def decrease_power(self):
        if self.power > 0:
            self.power -= self.power_step // 2
            self.game_state.change_power(self.power)

    def increase_power(self):
        if self.power <= self.power_needed_to_move_obstacle:
            self.power += self.power_step
            self.game_state.change_power(self.power)

    def reset_power(self):
        self.power = self.game_state.max_power // 3
        self.game_state.change_power(self.power)

    def update(self):
        super().update()
        self.decrease_power()

    def custom_draw(self, game_surface, offset):
        if self.power > 0:
            self.power_bar.draw(game_surface, self.power, offset)

        offset_position = self.rect.topleft + offset
        game_surface.blit(self.image, offset_position)

    def get_bar_position(self):
        bar_left = self.position[0]
        bar_top = self.position[1] - game_helper.multiply_by_tile_size_ratio(16)
        return bar_left, bar_top

