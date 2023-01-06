# Use key arrows (up, down) to change animations (actions: right, left, up, down)
import pygame
import animations_spritesheet

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Spritesheets - animations')

sprite_sheet_image = pygame.image.load('player.png').convert_alpha()
sprite_sheet = animations_spritesheet.AnimationsSpriteSheet(sprite_sheet_image)

BG = (150, 150, 150)
BLACK = (0, 0, 0)

# Create animation list
animation_list = []
animation_steps = [1, 4, 1, 4, 1, 4, 1, 4]
action = 0
last_update = pygame.time.get_ticks()
animation_cooldown = 150
frame = 0

animation_row = 0
for animation in animation_steps:
    temp_img_list = []
    for animation_step in range(animation):
        temp_img_list.append(sprite_sheet.get_image(animation_row, animation_step, 16, 16, 3, BLACK))
    animation_list.append(temp_img_list)
    animation_row += 1

run = True
while run:
    print(f'Action: {action} | Frame: {frame}')

    # Update background
    screen.fill(BG)

    # Update animation
    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame += 1
        if frame >= len(animation_list[action]):
            frame = 0
        last_update = current_time

    # Show frame image
    screen.blit(animation_list[action][frame], (SCREEN_WIDTH // 2 - (16 * 3) // 2, SCREEN_HEIGHT // 2 - (16 * 3) // 2))

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN and action > 0:
                action -= 1
                frame = 0
            if event.key == pygame.K_UP and action < len(animation_list) - 1:
                action += 1
                frame = 0

    pygame.display.update()

pygame.quit()
