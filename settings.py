import pygame
from debug import Debug

# Clock
FPS = 60

# Screen size
WIDTH = 800
HEIGHT = 600
# Dashboard size
DASHBOARD_HEIGHT = 120

# Tile size
TILE_SIZE = 64

# Events
GAME_OVER_EVENT = pygame.USEREVENT + 1
ADD_DIAMOND_EVENT = pygame.USEREVENT + 2
DECREASE_ENERGY_EVENT = pygame.USEREVENT + 3
EXIT_POINT_IS_OPEN_EVENT = pygame.USEREVENT + 4
NEXT_LEVEL_EVENT = pygame.USEREVENT + 5
REFRESH_OBSTACLE_MAP_EVENT = pygame.USEREVENT + 6

# Create debugger
debugger = Debug()
