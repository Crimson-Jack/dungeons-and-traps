import pygame
import settings
from wall import Wall
from ground import Ground
from diamond import Diamond
from spider_enemy import SpiderEnemy
from ghost_enemy import GhostEnemy
from player import Player
from camera_group import CameraGroup
from y_sort_camera_group import YSortCameraGroup


class Level:
    def __init__(self, screen, game_surface, game_state):
        # Set screen and game_surface
        self.screen = screen
        self.game_surface = game_surface

        # Set up sprite groups
        self.background_sprites = CameraGroup(game_surface)
        self.visible_sprites = YSortCameraGroup(game_surface)
        self.enemy_sprites = CameraGroup(game_surface)
        self.obstacle_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()

        # Set obstacle map
        self.obstacle_map = self.get_obstacle_map()

        # TODO: Refactor, implement for each Ghost object and add starting path to algorithm
        #  The first test for finding wall follower path
        #  Use F1 (debugger) to display this test
        start_position = [10, 1]
        end_position = [9, 1]
        direction = [1, 0]
        self.wall_follower_path = self.get_wall_follower_path(self.obstacle_map, start_position, end_position, direction)

        # Set game state
        self.game_state = game_state

        # Create sprites
        self.player = self.create_sprites_and_get_player()

    def get_obstacle_map(self):
        # Create obstacle map
        map_rows = []
        for row_index, row in enumerate(settings.WORLD_MAP):
            map_columns = []
            for col_index, col in enumerate(row):
                if col == 'x':
                    map_columns.append(1)
                else:
                    map_columns.append(0)
            map_rows.append(map_columns)

        return map_rows

    def get_wall_follower_path(self, obstacle_map, start_position, end_position, direction):
        path = []
        current_position = start_position
        is_end_of_path = False
        count = 0

        while not is_end_of_path and count < 200:
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

            if not obstacle_map[next_position[1]][next_position[0]] and obstacle_map[next_position_left[1]][next_position_left[0]]:
                # Move
                current_position = next_position
            elif not obstacle_map[next_position[1]][next_position[0]] and not obstacle_map[next_position_left[1]][next_position_left[0]]:
                # Move
                current_position = next_position
                # Turn -90 degree
                vector = pygame.math.Vector2(direction)
                new_vector = pygame.math.Vector2.rotate(vector, -90)
                direction = [int(new_vector[0]), int(new_vector[1])]
            elif obstacle_map[next_position[1]][next_position[0]]:
                # Turn -90 degree
                vector = pygame.math.Vector2(direction)
                new_vector = pygame.math.Vector2.rotate(vector, 90)
                direction = [int(new_vector[0]), int(new_vector[1])]

            path.append(current_position)

            if end_position in path:
                is_end_of_path = True

            count += 1
        return path

    def create_sprites_and_get_player(self):
        # Create sprites and get player sprite
        player = None
        for row_index, row in enumerate(settings.WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * settings.TILE_SIZE
                y = row_index * settings.TILE_SIZE
                if col == 'x':
                    # Add tile to visible and obstacle sprites group
                    Wall((x, y), [self.visible_sprites, self.obstacle_sprites])
                if col == 'bg':
                    # Add tile to background sprites group
                    Ground((x, y), [self.background_sprites])
                if col == 'd':
                    # Add tile to visible and collectable sprites group
                    Diamond((x, y), [self.visible_sprites, self.collectable_sprites])
                if col.find('s') >= 0:
                    # TODO: Improve parsing process
                    # Add tile to enemy sprites group
                    SpiderEnemy((x, y), [self.enemy_sprites], int(col[1]), int(col[2]))
                if col == 'g':
                    GhostEnemy((x, y), [self.enemy_sprites], self.obstacle_map)
                if col == 'p':
                    # Add player to visible group
                    player = Player((x, y), [self.visible_sprites], self.obstacle_sprites, self.collectable_sprites,
                                    self.enemy_sprites, self.game_state)
        return player

    def run(self):
        # Run Update method foreach sprite from the group
        self.visible_sprites.update()
        self.enemy_sprites.update()

        # Draw all visible sprites
        self.background_sprites.custom_draw(self.player)
        self.visible_sprites.custom_draw(self.player)
        self.enemy_sprites.custom_draw(self.player)

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
                    self.game_surface.blit(temp_surface, temp_rect)
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
                self.game_surface.blit(temp_surface, temp_rect)
                temp_count += 1

        # Blit game_surface on the main screen
        self.screen.blit(self.game_surface, (0, 0))

        # Read inputs and display variables if debugger is enabled
        settings.debugger.input()
        settings.debugger.show()

    def game_over(self):
        half_width = self.screen.get_size()[0] // 2
        half_height = self.screen.get_size()[1] // 2

        accent_color = (255, 255, 255)
        background_color = (100, 100, 100)
        basic_font = pygame.font.Font('freesansbold.ttf', 50)

        game_over = basic_font.render('GAME OVER', True, accent_color, background_color)
        game_over_size = game_over.get_size()
        self.screen.blit(game_over, (half_width - game_over_size[0] // 2, half_height - game_over_size[1] // 2))
