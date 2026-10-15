import pygame

from src.camera_group import CameraGroup
from src.camera_group_with_y_sort import CameraGroupWithYSort


class LevelSpriteGroups:
    """Owns the sprite groups of a level: five visible layers drawn back to front and the functional groups."""

    def __init__(self, game_surface: pygame.Surface, size_of_map: tuple[int, int]) -> None:
        """
        Create the empty visible and functional groups.

        :param game_surface: surface the visible groups draw on
        :param size_of_map: map size in tiles
        """
        # Set up visible groups
        self.bottom_background_layer = CameraGroup(game_surface, size_of_map)
        self.bottom_sprites_layer = CameraGroup(game_surface, size_of_map)
        self.middle_sprites_layer = CameraGroupWithYSort(game_surface, size_of_map)
        self.top_sprites_layer = CameraGroup(game_surface, size_of_map)
        self.the_highest_sprites_layer = CameraGroup(game_surface, size_of_map)

        # Set up functional groups
        self.exit_points = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.moving_obstacle_sprites = pygame.sprite.Group()
        self.removable_obstacle_sprites = pygame.sprite.Group()
        self.passage_sprites = pygame.sprite.Group()
        self.teleport_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.hostile_force_sprites = pygame.sprite.Group()
