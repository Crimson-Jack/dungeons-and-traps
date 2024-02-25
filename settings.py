import pygame
from debug import Debug

# Clock
FPS = 60

# Screen size
WIDTH = 1080
HEIGHT = 720
# Header size
HEADER_HEIGHT = 84
# Dashboard size
DASHBOARD_HEIGHT = 150

# Tile size
TILE_SIZE = 64

# Colors
ENEMY_PARTICLE_COLORS = [(240, 89, 65), (190, 49, 68), (135, 35, 65), (34, 9, 44)]
OBSTACLE_PARTICLE_COLORS = [(255, 255, 255), (240, 240, 240), (230, 230, 230), (220, 220, 220)]

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
