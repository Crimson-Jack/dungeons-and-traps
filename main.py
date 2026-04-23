import asyncio

import pygame
import sys
from src.game import Game


def main():
    # Initialize and run the game
    game = Game()
    asyncio.run(game.run())
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
