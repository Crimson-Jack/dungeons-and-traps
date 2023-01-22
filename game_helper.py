import pygame
import settings

# Base tile size - reference tile size - base on this parameter, all other values are calculated
BASE_TILE_SIZE = 64


def calculate_ratio(value):
    return value * settings.TILE_SIZE / BASE_TILE_SIZE


def get_wall_follower_path(obstacle_map, start_position, base_direction):
    # Right direction
    direction = [1, 0]

    if base_direction == pygame.math.Vector2(1, 0):
        direction = [1, 0]
    elif base_direction == pygame.math.Vector2(-1, 0):
        direction = [-1, 0]
    elif base_direction == pygame.math.Vector2(0, 1):
        direction = [0, 1]
    elif base_direction == pygame.math.Vector2(0, -1):
        direction = [0, -1]

    current_position = start_position
    is_end_of_path = False
    path = []

    iteration = 0
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
            iteration += 1

        if iteration >= 2:
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
