import pygame
import settings
from enemy import Enemy


class GhostEnemy(Enemy):
    def __init__(self, position, groups, speed, obstacle_map, tile_start_position):
        super().__init__(groups)
        image = pygame.image.load('img/tile_0121.png').convert_alpha()
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(0, 0)

        # Set obstacle map
        self.obstacle_map = obstacle_map

        # Left hand wall follower path
        self.wall_follower_path = self.get_wall_follower_path(self.obstacle_map, tile_start_position)
        self.movement_index = 0

        # Create movement variables
        self.direction = pygame.math.Vector2((1, 0))
        self.speed = speed
        self.current_position_on_map = [(self.rect.right // settings.TILE_SIZE) - 1, (self.rect.bottom // settings.TILE_SIZE) - 1]
        self.new_position_on_map = [(self.rect.right // settings.TILE_SIZE) - 1, (self.rect.bottom // settings.TILE_SIZE) - 1]

    def get_wall_follower_path(self, obstacle_map, start_position):
        # Right direction
        direction = [1, 0]
        current_position = start_position
        is_end_of_path = False
        path = []
        count = 0

        while not is_end_of_path:
            next_position = [current_position[0] + direction[0], current_position[1] + direction[1]]

            # If Right direction
            if direction == [1, 0]:
                next_position_left = [next_position[0], next_position[1] - 1]
            # If Up direction
            elif direction == [0, -1]:
                next_position_left = [next_position[0] - 1, next_position[1]]
            # Elif left direction
            elif direction == [-1, 0]:
                next_position_left = [next_position[0], next_position[1] + 1]
            # Elif down direction
            elif direction == [0, 1]:
                next_position_left = [next_position[0] + 1, next_position[1]]

            if len(path) > 0 and next_position == path[0]:
                is_end_of_path = True

            if not is_end_of_path:
                if not obstacle_map[next_position[1]][next_position[0]] and obstacle_map[next_position_left[1]][next_position_left[0]]:
                    # Move
                    current_position = next_position
                    # Add position to the path
                    path.append(current_position)
                elif not obstacle_map[next_position[1]][next_position[0]] and not obstacle_map[next_position_left[1]][next_position_left[0]]:
                    # Move
                    current_position = next_position
                    # Turn -90 degree
                    vector = pygame.math.Vector2(direction)
                    new_vector = pygame.math.Vector2.rotate(vector, -90)
                    direction = [int(new_vector[0]), int(new_vector[1])]
                    # Add position to the path
                    path.append(current_position)
                elif obstacle_map[next_position[1]][next_position[0]]:
                    # Turn -90 degree
                    vector = pygame.math.Vector2(direction)
                    new_vector = pygame.math.Vector2.rotate(vector, 90)
                    direction = [int(new_vector[0]), int(new_vector[1])]

        return path

    def move(self):
        # Set the movement offset
        self.hitbox.x += self.direction.x * self.speed
        self.hitbox.y += self.direction.y * self.speed
        self.rect.center = self.hitbox.center
        
        if self.rect.right % settings.TILE_SIZE == 0:
            self.new_position_on_map[0] = (self.rect.right // settings.TILE_SIZE) - 1

        if self.rect.bottom % settings.TILE_SIZE == 0:
            self.new_position_on_map[1] = (self.rect.bottom // settings.TILE_SIZE) - 1

        if self.current_position_on_map != self.new_position_on_map:
            if self.current_position_on_map[0] != self.new_position_on_map[0]:
                self.current_position_on_map[0] = self.new_position_on_map[0]
            if self.current_position_on_map[1] != self.new_position_on_map[1]:
                self.current_position_on_map[1] = self.new_position_on_map[1]

            print(f'x={self.current_position_on_map[0]}')
            print(f'y={self.current_position_on_map[1]}')

            # Determine new direction
            previous_position = self.wall_follower_path[self.movement_index]

            # Increase movement index in the path
            if self.movement_index < len(self.wall_follower_path) - 1:
                # Move to the next index
                self.movement_index += 1
            else:
                # Reset index - the loop is closed - start from the beginning
                self.movement_index = 0

            next_position = self.wall_follower_path[self.movement_index]


            self.direction.x = next_position[0] - previous_position[0]
            self.direction.y = next_position[1] - previous_position[1]

    def update(self):
        self.move()

    def custom_draw(self, game_surface, offset):

        # TODO: Remove after tests
        # Draw obstacle info
        if settings.debugger.enabled:
            temp_font = pygame.font.Font(None, 26)
            key_row = 0
            key_column = 0
            for map_row in self.obstacle_map:
                for map_column in map_row:
                    temp_surface = temp_font.render(str(map_column), True, (255, 255, 255))
                    temp_rect = temp_surface.get_rect(topleft=(key_column * settings.TILE_SIZE + 26, key_row * settings.TILE_SIZE +26))
                    game_surface.blit(temp_surface, temp_rect)
                    key_column += 1
                key_row += 1
                key_column = 0

        # TODO: Remove after tests
        # Draw wall follower path
        if settings.debugger.enabled:
            temp_font = pygame.font.Font(None, 26)
            temp_count = 0
            for point in self.wall_follower_path:
                temp_surface = temp_font.render(str(f"[{temp_count}]"), True, (255, 255, 255))
                temp_rect = temp_surface.get_rect(
                    topleft=(point[0] * settings.TILE_SIZE + 3, point[1] * settings.TILE_SIZE + 3))
                game_surface.blit(temp_surface, temp_rect)
                temp_count += 1
