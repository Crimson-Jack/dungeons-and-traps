# Note: This file is just a draft for testing purposes
import pygame, sys
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
    __number_of_sprites = 8

    def __init__(self, position_x, position_y):
        super().__init__()

        self.step_counter = 0
        self.costume_index = 0
        self.hero_size = 100

        self.load_all_srites()
        self.rect.center = (position_x, position_y)

        self.is_moving = False

    def load_all_srites(self):
        self.all_sprites = {'left': [], 'right': [], 'up': [], 'down': [], 'right_down': [], 'left_down': [],
                            'left_up': [], 'right_up': []}

        # Sprite - hero stand
        # Default - right
        hero_image = pygame.image.load('top-view-hero-movement/img/manBlue_stand.png')
        hero_image = pygame.transform.scale(hero_image, (self.hero_size, self.hero_size))
        self.all_sprites['right'].append(hero_image)
        self.all_sprites['left'].append(pygame.transform.rotate(hero_image, 180))
        self.all_sprites['up'].append(pygame.transform.rotate(hero_image, 90))
        self.all_sprites['down'].append(pygame.transform.rotate(hero_image, 270))
        # Sprite - rotated (45 degrees) hero stand
        # Default = right down
        hero_image_rotated = pygame.image.load(f'top-view-hero-movement/img/manBlue_stand_ang45.png')
        hero_image_rotated = pygame.transform.scale(hero_image_rotated, (self.hero_size, self.hero_size))
        self.all_sprites['right_down'].append(hero_image_rotated)
        self.all_sprites['right_up'].append(pygame.transform.rotate(hero_image_rotated, 90))
        self.all_sprites['left_up'].append(pygame.transform.rotate(hero_image_rotated, 180))
        self.all_sprites['left_down'].append(pygame.transform.rotate(hero_image_rotated, 270))

        # Sprites - hero walk
        for num in range(1, self.__number_of_sprites):
            hero_image = pygame.image.load(f'top-view-hero-movement/img/manBlue_walk{num}.png')
            hero_image = pygame.transform.scale(hero_image, (self.hero_size, self.hero_size))
            self.all_sprites['right'].append(hero_image)
            self.all_sprites['left'].append(pygame.transform.rotate(hero_image, 180))
            self.all_sprites['up'].append(pygame.transform.rotate(hero_image, 90))
            self.all_sprites['down'].append(pygame.transform.rotate(hero_image, 270))
            # Sprites - rotated (45 degrees) hero walk
            hero_image_rotated = pygame.image.load(f'top-view-hero-movement/img/manBlue_walk{num}_ang45.png')
            hero_image_rotated = pygame.transform.scale(hero_image_rotated, (self.hero_size, self.hero_size))
            self.all_sprites['right_down'].append(hero_image_rotated)
            self.all_sprites['right_up'].append(pygame.transform.rotate(hero_image_rotated, 90))
            self.all_sprites['left_up'].append(pygame.transform.rotate(hero_image_rotated, 180))
            self.all_sprites['left_down'].append(pygame.transform.rotate(hero_image_rotated, 270))

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
        costume_switching_threshold = 3

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

hero = Hero(200, 200)
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
    screen.fill((200, 200, 200))
    main_sprites.update()
    main_sprites.draw(screen)

    clock.tick(60)