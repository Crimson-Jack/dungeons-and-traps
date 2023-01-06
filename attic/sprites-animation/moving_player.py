# Note: This file is just a draft for testing purposes
import pygame, sys
import moving_player_spritesheet
from enum import IntEnum


class Direction(IntEnum):
    RIGHT = 1
    LEFT = 2
    DOWN = 3
    UP = 4
    RIGHT_UP = 14
    RIGHT_DOWN = 13
    LEFT_UP = 24
    LEFT_DOWN = 23


class Hero(pygame.sprite.Sprite):
    __hero_speed = 3
    __number_of_sprites = 5

    def __init__(self, position_x, position_y, hero_scale):
        super().__init__()

        self.colour_key = (0, 0, 0)

        self.step_counter = 0
        self.costume_index = 0
        self.hero_scale = hero_scale

        self.load_all_srites()
        self.rect.center = (position_x, position_y)

        self.is_moving = False

    def load_all_srites(self):
        self.all_sprites = {'left': [], 'right': [], 'up': [], 'down': [], 'right_down': [], 'left_down': [],
                            'left_up': [], 'right_up': []}

        sprite_sheet_image = pygame.image.load('player.png').convert_alpha()
        sprite_sheet = moving_player_spritesheet.MovingPlayerSpriteSheet(sprite_sheet_image)

        # Sprite - hero stand
        self.all_sprites['right'].append(sprite_sheet.get_image(0, 0, 16, 16, self.hero_scale, self.colour_key))
        self.all_sprites['left'].append(sprite_sheet.get_image(2, 0, 16, 16, self.hero_scale, self.colour_key))
        self.all_sprites['up'].append(sprite_sheet.get_image(4, 0, 16, 16, self.hero_scale, self.colour_key))
        self.all_sprites['down'].append(sprite_sheet.get_image(6, 0, 16, 16, self.hero_scale, self.colour_key))

        self.all_sprites['right_down'].append(sprite_sheet.get_image(6, 0, 16, 16, self.hero_scale, self.colour_key))
        self.all_sprites['right_up'].append(sprite_sheet.get_image(4, 0, 16, 16, self.hero_scale, self.colour_key))
        self.all_sprites['left_down'].append(sprite_sheet.get_image(6, 0, 16, 16, self.hero_scale, self.colour_key))
        self.all_sprites['left_up'].append(sprite_sheet.get_image(4, 0, 16, 16, self.hero_scale, self.colour_key))

        # Sprites - hero walk
        for num in range(0, self.__number_of_sprites):

            self.all_sprites['right'].append(sprite_sheet.get_image(1, num, 16, 16, self.hero_scale, self.colour_key))
            self.all_sprites['left'].append(sprite_sheet.get_image(3, num, 16, 16, self.hero_scale, self.colour_key))
            self.all_sprites['up'].append(sprite_sheet.get_image(5, num, 16, 16, self.hero_scale, self.colour_key))
            self.all_sprites['down'].append(sprite_sheet.get_image(7, num, 16, 16, self.hero_scale, self.colour_key))

            self.all_sprites['right_down'].append(sprite_sheet.get_image(7, num, 16, 16, self.hero_scale, self.colour_key))
            self.all_sprites['right_up'].append(sprite_sheet.get_image(5, num, 16, 16, self.hero_scale, self.colour_key))
            self.all_sprites['left_down'].append(sprite_sheet.get_image(7, num, 16, 16, self.hero_scale, self.colour_key))
            self.all_sprites['left_up'].append(sprite_sheet.get_image(5, num, 16, 16, self.hero_scale, self.colour_key))

        self.image = self.all_sprites['right'][0]
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def move(self, direction):
        if self.is_moving == False:
            self.is_moving = True
            self.direction = direction
            self.step_counter += 1

    def change_position(self):
        if self.is_moving == False:
            return

        # Default translation
        dx = 0
        dy = 0
        costume_switching_threshold = 4

        if self.direction == Direction.RIGHT or self.direction == Direction.RIGHT_UP or self.direction == Direction.RIGHT_DOWN:
            dx += self.__hero_speed
        if self.direction == Direction.LEFT or self.direction == Direction.LEFT_UP or self.direction == Direction.LEFT_DOWN:
            dx -= self.__hero_speed

        if self.direction == Direction.DOWN or self.direction == Direction.LEFT_DOWN or self.direction == Direction.RIGHT_DOWN:
            dy += self.__hero_speed
        if self.direction == Direction.UP or self.direction == Direction.LEFT_UP or self.direction == Direction.RIGHT_UP:
            dy -= self.__hero_speed

        # Handle animation
        if self.step_counter > costume_switching_threshold:
            self.step_counter = 0
            self.costume_index += 1
            if self.costume_index >= self.__number_of_sprites:
                self.costume_index = 1

            if self.direction == Direction.RIGHT:
                self.image = self.all_sprites['right'][self.costume_index]
            if self.direction == Direction.LEFT:
                self.image = self.all_sprites['left'][self.costume_index]
            if self.direction == Direction.UP:
                self.image = self.all_sprites['up'][self.costume_index]
            if self.direction == Direction.DOWN:
                self.image = self.all_sprites['down'][self.costume_index]
            if self.direction == Direction.RIGHT_UP:
                self.image = self.all_sprites['right_up'][self.costume_index]
            if self.direction == Direction.RIGHT_DOWN:
                self.image = self.all_sprites['right_down'][self.costume_index]
            if self.direction == Direction.LEFT_UP:
                self.image = self.all_sprites['left_up'][self.costume_index]
            if self.direction == Direction.LEFT_DOWN:
                self.image = self.all_sprites['left_down'][self.costume_index]

        # Update coordinates
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        self.change_position()


pygame.init()
clock = pygame.time.Clock()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Top view | hero movement")
BG = (150, 150, 150)
hero_scale = 10

hero = Hero(screen_width // 2, screen_height // 2, hero_scale)
main_sprites = pygame.sprite.Group()
main_sprites.add(hero)

while True:
    direction = Direction.DOWN

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    key = pygame.key.get_pressed()
    hero.is_moving = False

    if (key[pygame.K_RIGHT] and key[pygame.K_LEFT]) or (key[pygame.K_UP] and key[pygame.K_DOWN]):
        hero.is_moving = False
    else:
        if key[pygame.K_LEFT] and key[pygame.K_UP]:
            hero.move(Direction.LEFT_UP)
        if key[pygame.K_LEFT] and key[pygame.K_DOWN]:
            hero.move(Direction.LEFT_DOWN)
        if key[pygame.K_RIGHT] and key[pygame.K_UP]:
            hero.move(Direction.RIGHT_UP)
        if key[pygame.K_RIGHT] and key[pygame.K_DOWN]:
            hero.move(Direction.RIGHT_DOWN)

        if key[pygame.K_RIGHT]:
            hero.move(Direction.RIGHT)
        if key[pygame.K_LEFT]:
            hero.move(Direction.LEFT)
        if key[pygame.K_UP]:
            hero.move(Direction.UP)
        if key[pygame.K_DOWN]:
            hero.move(Direction.DOWN)

    pygame.display.flip()
    screen.fill(BG)
    main_sprites.update()
    main_sprites.draw(screen)

    clock.tick(60)