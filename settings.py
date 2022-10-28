import pygame
from debug import Debug

# Clock
FPS = 60

# Screen size
WIDTH = 960
HEIGHT = 600
# Dashboard size
DASHBOARD_HEIGHT = 120
# Tile size
TILE_SIZE = 64

# Events
GAME_OVER_EVENT = pygame.USEREVENT + 1
ADD_DIAMOND_EVENT = pygame.USEREVENT + 2
DECREASE_ENERGY_EVENT = pygame.USEREVENT + 3

# Create debugger
debugger = Debug()