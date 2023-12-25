import pygame, sys

from src import keyboard
from src.entities import PhysicsEntity
from src.utils import load_image

class Game:
    def __init__(self):
        pygame.display.set_caption("Ninja game by DaFluffyPotato")
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.keys = keyboard.Keyboard("wasd").get_keys()

        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))
        self.player_movement_x = [False, False]
        self.player_movement_y = [False, False]

        self.assets = {
            'player': load_image('entities/player.png')
        }

        self.events = {
            "quit": 0,
            "up": 0,
            "down": 0,
            "right": 0,
            "left": 0,
        }

    def process_events(self):
        keys = self.keys
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.events["quit"] = 1
            if event.type == pygame.KEYDOWN:
                if event.key == keys["up"]:
                    self.events["up"] = 1
                if event.key == keys["down"]:
                    self.events["down"] = 1
                if event.key == keys["right"]:
                    self.events["right"] = 1
                if event.key == keys["left"]:
                    self.events["left"] = 1
            if event.type == pygame.KEYUP:
                if event.key == keys["up"]:
                    self.events["up"] = 0
                if event.key == keys["down"]:
                    self.events["down"] = 0
                if event.key == keys["right"]:
                    self.events["right"] = 0
                if event.key == keys["left"]:
                    self.events["left"] = 0

    def handle_input(self):
        self.player_movement_x = [self.events["right"], self.events["left"]]
        self.player_movement_y = [self.events["up"], self.events["down"]]

    def run(self):
        running = True
        while running:
            self.screen.fill((14, 219, 248))

            self.player.update((self.player_movement_x[0] - self.player_movement_x[1], 0))
            self.player.render(self.screen)

            self.process_events()
            self.handle_input()
            running = not self.events["quit"]
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()
