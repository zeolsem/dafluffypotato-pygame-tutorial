import pygame
from src.game import Game


def return_cwd():
    import os
    return os.getcwd()


def main():
    pygame.init()
    Game().run()


if __name__ == "__main__":
    main()

