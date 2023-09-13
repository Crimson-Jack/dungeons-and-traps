import pygame
import game_helper
import settings
from obstacle_map_refresh_sprite import ObstacleMapRefreshSprite
from enemy_with_brain import EnemyWithBrain
from breadth_first_search_helper import BreadthFirstSearchHelper


class MonsterEnemy(pygame.sprite.Sprite, EnemyWithBrain, ObstacleMapRefreshSprite):
    def __init__(self, image, position, groups, obstacle_map, game_state):
        super().__init__(groups)
        self.image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.hit_box = self.rect

        # Game state
        self.game_state = game_state

        # Movement variables
        self.obstacle_map = obstacle_map

        # Path variables
        self.all_tiles = []
        self.obstacles = []
        self.create_all_tiles_and_obstacles_lists()
        self.breadth_first_search_helper = BreadthFirstSearchHelper()
        self.path = None

    def create_all_tiles_and_obstacles_lists(self):
        for x in range(len(self.obstacle_map)):
            for y in range(len(self.obstacle_map[x])):
                self.all_tiles.append((y, x))
                if self.obstacle_map[x][y] > 0:
                    self.obstacles.append((y, x))

    def update(self):
        pass

    def refresh_obstacle_map(self):
        # The map has changed - regenerate lists
        self.all_tiles = []
        self.obstacles = []
        self.create_all_tiles_and_obstacles_lists()
        # Calculate a new path
        self.calculate_path_to_player()

    def set_player_tile_position(self):
        # Calculate a new path
        self.calculate_path_to_player()

    def calculate_path_to_player(self):
        start_position = game_helper.get_tile_by_point(self.rect)
        end_position = self.game_state.player_tile_position

        # Get path
        is_end_reached, self.path, frontier, came_from = self.breadth_first_search_helper.search(self.all_tiles,
                                                                                                 self.obstacles,
                                                                                                 start_position,
                                                                                                 end_position)
        # print(self.path)
