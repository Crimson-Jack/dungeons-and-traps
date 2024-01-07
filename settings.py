import pygame
from debug import Debug

# Clock
FPS = 60

# Screen size
WIDTH = 1024
HEIGHT = 600
# Dashboard size
DASHBOARD_HEIGHT = 150

# Tile size
TILE_SIZE = 64

# Events
GAME_OVER_EVENT = pygame.event.custom_type()
COLLECT_DIAMOND_EVENT = pygame.event.custom_type()
COLLECT_KEY_EVENT = pygame.event.custom_type()
DECREASE_ENERGY_EVENT = pygame.event.custom_type()
CHANGE_POWER_EVENT = pygame.event.custom_type()
EXIT_POINT_IS_OPEN_EVENT = pygame.event.custom_type()
NEXT_LEVEL_EVENT = pygame.event.custom_type()
REFRESH_OBSTACLE_MAP_EVENT = pygame.event.custom_type()
PLAYER_TILE_POSITION_CHANGED_EVENT = pygame.event.custom_type()
PLAYER_IS_NOT_USING_WEAPON_EVENT = pygame.event.custom_type()
ADD_TOMBSTONE_EVENT = pygame.event.custom_type()
ADD_PARTICLE_EFFECT_EVENT = pygame.event.custom_type()
PARTICLE_EVENT = pygame.event.custom_type()

# Create debugger
debugger = Debug()
