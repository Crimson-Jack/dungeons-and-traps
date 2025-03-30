import settings
import pygame
from spritesheet import SpriteSheet


SCALE = int(settings.TILE_SIZE), int(settings.TILE_SIZE)
KEY_COLOR = 0, 0, 0


def get_sprite_sheet(path, source_size, scale, key_color):
    sprite_sheet = SpriteSheet(
        pygame.image.load(path).convert_alpha(),
        source_size,
        source_size,
        scale,
        key_color
    )

    return sprite_sheet


def get_all_player_sprites(number_of_sprites):
    sprite_sheet = get_sprite_sheet('img/player.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = {
        'left': [],
        'right': [],
        'up': [],
        'down': [],
        'right_down': [],
        'left_down': [],
        'left_up': [],
        'right_up': []}

    # Sprites with the state: standing
    sprites['right'].append(sprite_sheet.get_image(0, 0))
    sprites['left'].append(sprite_sheet.get_image(2, 0))
    sprites['up'].append(sprite_sheet.get_image(4, 0))
    sprites['down'].append(sprite_sheet.get_image(6, 0))
    sprites['right_down'].append(sprite_sheet.get_image(6, 0))
    sprites['right_up'].append(sprite_sheet.get_image(4, 0))
    sprites['left_down'].append(sprite_sheet.get_image(6, 0))
    sprites['left_up'].append(sprite_sheet.get_image(4, 0))

    # Sprites with the state: walking
    for number in range(0, number_of_sprites):
        sprites['right'].append(sprite_sheet.get_image(1, number))
        sprites['left'].append(sprite_sheet.get_image(3, number))
        sprites['up'].append(sprite_sheet.get_image(5, number))
        sprites['down'].append(sprite_sheet.get_image(7, number))
        sprites['right_down'].append(sprite_sheet.get_image(7, number))
        sprites['right_up'].append(sprite_sheet.get_image(5, number))
        sprites['left_down'].append(sprite_sheet.get_image(7, number))
        sprites['left_up'].append(sprite_sheet.get_image(5, number))

    return sprites


def get_life_sprite():
    sprite_sheet = get_sprite_sheet('img/misc.png', settings.SOURCE_TILE_SIZE, (64, 64), KEY_COLOR)
    return sprite_sheet.get_image(1, 2)


def get_all_arrow_sprites():
    sprite_sheet = get_sprite_sheet('img/arrow.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = {
        'left': [],
        'right': [],
        'up': [],
        'down': []}

    sprites['right'].append(sprite_sheet.get_image(0, 0))
    sprites['left'].append(sprite_sheet.get_image(1, 0))
    sprites['up'].append(sprite_sheet.get_image(2, 0))
    sprites['down'].append(sprite_sheet.get_image(3, 0))

    return sprites


def get_all_sword_sprites():
    sprite_sheet = get_sprite_sheet('img/sword.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = {
        'left': [],
        'right': [],
        'up': [],
        'down': []}

    sprites['right'].append(sprite_sheet.get_image(0, 0))
    sprites['right'].append(sprite_sheet.get_image(0, 1))
    sprites['right'].append(sprite_sheet.get_image(0, 2))
    sprites['right'].append(sprite_sheet.get_image(0, 3))
    sprites['right'].append(sprite_sheet.get_image(0, 3))
    sprites['right'].append(sprite_sheet.get_image(0, 3))
    sprites['right'].append(sprite_sheet.get_image(0, 3))
    sprites['right'].append(sprite_sheet.get_image(0, 3))

    sprites['left'].append(sprite_sheet.get_image(1, 0))
    sprites['left'].append(sprite_sheet.get_image(1, 1))
    sprites['left'].append(sprite_sheet.get_image(1, 2))
    sprites['left'].append(sprite_sheet.get_image(1, 3))
    sprites['left'].append(sprite_sheet.get_image(1, 3))
    sprites['left'].append(sprite_sheet.get_image(1, 3))
    sprites['left'].append(sprite_sheet.get_image(1, 3))
    sprites['left'].append(sprite_sheet.get_image(1, 3))

    sprites['up'].append(sprite_sheet.get_image(2, 0))
    sprites['up'].append(sprite_sheet.get_image(2, 1))
    sprites['up'].append(sprite_sheet.get_image(2, 2))
    sprites['up'].append(sprite_sheet.get_image(2, 3))
    sprites['up'].append(sprite_sheet.get_image(2, 3))
    sprites['up'].append(sprite_sheet.get_image(2, 3))
    sprites['up'].append(sprite_sheet.get_image(2, 3))
    sprites['up'].append(sprite_sheet.get_image(2, 3))

    sprites['down'].append(sprite_sheet.get_image(3, 0))
    sprites['down'].append(sprite_sheet.get_image(3, 1))
    sprites['down'].append(sprite_sheet.get_image(3, 2))
    sprites['down'].append(sprite_sheet.get_image(3, 3))
    sprites['down'].append(sprite_sheet.get_image(3, 3))
    sprites['down'].append(sprite_sheet.get_image(3, 3))
    sprites['down'].append(sprite_sheet.get_image(3, 3))
    sprites['down'].append(sprite_sheet.get_image(3, 3))

    return sprites


def get_all_tombstone_sprites():
    sprite_sheet = get_sprite_sheet('img/skull.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = list()
    sprites.append(sprite_sheet.get_image(0, 0))
    sprites.append(sprite_sheet.get_image(0, 1))
    sprites.append(sprite_sheet.get_image(0, 2))
    sprites.append(sprite_sheet.get_image(0, 3))

    return sprites


def get_all_vanishing_point_sprites():
    sprite_sheet = get_sprite_sheet('img/vanishing-point.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = list()
    sprites.append(sprite_sheet.get_image(0, 0))
    sprites.append(sprite_sheet.get_image(0, 1))
    sprites.append(sprite_sheet.get_image(0, 2))
    sprites.append(sprite_sheet.get_image(0, 3))
    sprites.append(sprite_sheet.get_image(0, 4))
    sprites.append(sprite_sheet.get_image(0, 5))
    sprites.append(sprite_sheet.get_image(0, 6))
    sprites.append(sprite_sheet.get_image(0, 7))

    return sprites


def get_all_bow_sprites():
    sprite_sheet = get_sprite_sheet('img/bow.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = {
        'left': [],
        'right': [],
        'up': [],
        'down': []}

    sprites['right'].append(sprite_sheet.get_image(0, 0))
    sprites['left'].append(sprite_sheet.get_image(1, 0))
    sprites['up'].append(sprite_sheet.get_image(2, 0))
    sprites['down'].append(sprite_sheet.get_image(3, 0))

    return sprites


def add_spider_sprites_in_damaged_state(name, number_of_sprites, number_of_rows, sprites):
    sprite_sheet = get_sprite_sheet(f'img/{name}.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    for cell in range(0, number_of_sprites):
        for row in range(0, number_of_rows):
            sprites[cell].append(sprite_sheet.get_image(row + 1, cell))

    return sprites


def get_monster_sprite_in_damaged_state(name):
    sprite_sheet = get_sprite_sheet(f'img/{name}.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)
    return sprite_sheet.get_image(1, 0)


def get_sword_images_to_header_view():
    sprite_sheet = get_sprite_sheet(f'img/misc.png', settings.SOURCE_TILE_SIZE, (64, 64), KEY_COLOR)

    images = list()
    images.append(sprite_sheet.get_image(2, 0))
    images.append(sprite_sheet.get_image(2, 1))
    images.append(sprite_sheet.get_image(2, 2))
    images.append(sprite_sheet.get_image(2, 3))
    images.append(sprite_sheet.get_image(2, 4))

    return images


def get_bow_image_to_header_view():
    sprite_sheet = get_sprite_sheet(f'img/misc.png', settings.SOURCE_TILE_SIZE, (64, 64), KEY_COLOR)
    return sprite_sheet.get_image(1, 1)


def get_octopus_sprite_in_damaged_state(name):
    octopus_source_tile_size = settings.SOURCE_TILE_SIZE * 3
    octopus_scale = int(settings.TILE_SIZE * 3), int(settings.TILE_SIZE * 3)
    sprite_sheet = get_sprite_sheet(f'img/{name}.png', octopus_source_tile_size, octopus_scale, KEY_COLOR)
    return sprite_sheet.get_image(1, 0)


def get_all_fire_ball_enemy_sprites():
    sprite_sheet = get_sprite_sheet('img/fireball.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = list()

    sprites.append(sprite_sheet.get_image(0, 0))
    sprites.append(sprite_sheet.get_image(0, 1))
    sprites.append(sprite_sheet.get_image(0, 2))
    sprites.append(sprite_sheet.get_image(0, 3))

    return sprites
