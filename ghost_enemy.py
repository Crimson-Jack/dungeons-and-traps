import pygame
import settings


class GhostEnemy(pygame.sprite.Sprite):
    def __init__(self, image, position, groups, speed, obstacle_map, tile_start_position):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Set obstacle map
        self.obstacle_map = obstacle_map

        # Left hand wall follower path
        self.wall_follower_path = self.get_wall_follower_path(self.obstacle_map, tile_start_position)
        self.movement_index = -1

        # Create movement variables
        self.direction = pygame.math.Vector2((1, 0))
        self.speed = speed
        self.current_position_on_map = [(self.rect.right // settings.TILE_SIZE) - 1, (self.rect.bottom // settings.TILE_SIZE) - 1]
        self.new_position_on_map = list(self.current_position_on_map)
        self.set_new_direction()

        # Real position is required to store the real distance, which is then casted to integer
        self.real_x_position = float(self.hit_box.x)
        self.real_y_position = float(self.hit_box.y)

    def get_wall_follower_path(self, obstacle_map, start_position):
        # Right direction
        direction = [1, 0]
        current_position = start_position
        is_end_of_path = False
        path = []

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
                    # Turn 90 degree
                    vector = pygame.math.Vector2(direction)
                    new_vector = pygame.math.Vector2.rotate(vector, 90)
                    direction = [int(new_vector[0]), int(new_vector[1])]

        return path

    def move(self):
        # Calculate real y position
        self.real_x_position += float(self.direction.x * self.speed)
        self.real_y_position += float(self.direction.y * self.speed)

        # Cast real position to integer
        self.hit_box.x = int(self.real_x_position)
        self.hit_box.y = int(self.real_y_position)

        # Set the movement offset
        self.rect.center = self.hit_box.center

        # Adjust offset
        # This is necessary for offsets that are not TILE_SIZE dividers
        x_remainder = self.rect.right % settings.TILE_SIZE
        y_remainder = self.rect.bottom % settings.TILE_SIZE

        if x_remainder < self.speed:
            self.hit_box.x = self.hit_box.x - x_remainder
            self.rect.center = self.hit_box.center

        if y_remainder < self.speed:
            self.hit_box.y = self.hit_box.y - y_remainder
            self.rect.center = self.hit_box.center

        # Recognize the moment when ghost moves to a new area
        # In this case TILE_SIZE is a divisor of "right" or "bottom"
        if self.rect.right % settings.TILE_SIZE == 0:
            self.new_position_on_map[0] = (self.rect.right // settings.TILE_SIZE) - 1

        if self.rect.bottom % settings.TILE_SIZE == 0:
            self.new_position_on_map[1] = (self.rect.bottom // settings.TILE_SIZE) - 1

        # If position was changed, change position and determine new direction
        if self.current_position_on_map != self.new_position_on_map:
            # Change current position (x or y or both)
            if self.current_position_on_map[0] != self.new_position_on_map[0]:
                self.current_position_on_map[0] = self.new_position_on_map[0]
            if self.current_position_on_map[1] != self.new_position_on_map[1]:
                self.current_position_on_map[1] = self.new_position_on_map[1]

            self.set_new_direction()

    def set_new_direction(self):
        # Determine new direction
        # Get previous position from the path
        previous_position = self.wall_follower_path[self.movement_index]

        # Increase movement index in the path
        if self.movement_index < len(self.wall_follower_path) - 1:
            # Move to the next index
            self.movement_index += 1
        else:
            # Reset index - the loop is closed - start from the beginning
            self.movement_index = 0

        # Get next position from the path
        next_position = self.wall_follower_path[self.movement_index]

        # Calculate new direction vector based on previous and next position
        self.direction.x = next_position[0] - previous_position[0]
        self.direction.y = next_position[1] - previous_position[1]

    def update(self):
        self.move()


