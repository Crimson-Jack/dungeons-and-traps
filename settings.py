import pygame
from debug import Debug

# Clock
FPS = 60

# Screen size
FULL_SCREEN_MODE = False
WIDTH = 1080
HEIGHT = 600
# Header size
HEADER_HEIGHT = 80
# Dashboard size
DASHBOARD_HEIGHT = 144

# Tile size
TILE_SIZE = 64
# Source (originate) tile size
SOURCE_TILE_SIZE = 16

# Colors
ENEMY_PARTICLE_COLORS = [(240, 89, 65), (190, 49, 68), (135, 35, 65), (34, 9, 44)]
OBSTACLE_PARTICLE_COLORS = [(255, 255, 255), (240, 240, 240), (230, 230, 230), (220, 220, 220)]
MESSAGE_BACKGROUND_COLOR = 38, 66, 98
MESSAGE_BORDER_COLOR = 95, 112, 143
SURFACE_COLOR = 100, 100, 100
BACKGROUND_COLOR = 120, 120, 120
BORDER_COLOR = 70, 70, 70
TEXT_COLOR = 208, 208, 208
HIGHLIGHTED_TEXT_COLOR = 255, 255, 255
BAR_TEXT_COLOR = 50, 50, 50

# Events
GAME_OVER_EVENT = pygame.event.custom_type()
GAME_OVER_SUMMARY_EVENT = pygame.event.custom_type()
COLLECT_DIAMOND_EVENT = pygame.event.custom_type()
COLLECT_KEY_EVENT = pygame.event.custom_type()
DECREASE_NUMBER_OF_ARROWS_EVENT = pygame.event.custom_type()
CHANGE_ENERGY_EVENT = pygame.event.custom_type()
CHANGE_WEAPON_EVENT = pygame.event.custom_type()
EXIT_POINT_IS_OPEN_EVENT = pygame.event.custom_type()
NEXT_LEVEL_EVENT = pygame.event.custom_type()
REFRESH_OBSTACLE_MAP_EVENT = pygame.event.custom_type()
PLAYER_TILE_POSITION_CHANGED_EVENT = pygame.event.custom_type()
PLAYER_IS_NOT_USING_WEAPON_EVENT = pygame.event.custom_type()
ADD_TOMBSTONE_EVENT = pygame.event.custom_type()
ADD_PARTICLE_EFFECT_EVENT = pygame.event.custom_type()
PARTICLE_EVENT = pygame.event.custom_type()
PLAYER_LOST_LIFE_EVENT = pygame.event.custom_type()
RESPAWN_PLAYER_EVENT = pygame.event.custom_type()
COLLECT_LIFE_EVENT = pygame.event.custom_type()
CHANGE_SCORE_EVENT = pygame.event.custom_type()

# Create debugger
debugger = Debug()
