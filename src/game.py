import pygame, sys

from src import keyboard
from src.entities import PhysicsEntity
from src.utils import load_image, load_images
from src.tilemap import Tilemap


class Game:
    def __init__(self):
        pygame.display.set_caption("Ninja game by DaFluffyPotato")
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        self.keys = keyboard.Keyboard("wasd").get_keys()

        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))
        self.player_movement_x = [False, False]
        self.player_movement_y = [False, False]

        self.tilemap = Tilemap(self)

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
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
                    self.player.velocity[1] = -3.0 # TODO: CHANGE THIS CODE WTF
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
            self.display.fill((14, 219, 248))

            self.tilemap.render(self.display)

            self.player.update(self.tilemap, (self.player_movement_x[0] - self.player_movement_x[1], 0))
            self.player.render(self.display)

            self.process_events()
            self.handle_input()
            running = not self.events["quit"]

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()
