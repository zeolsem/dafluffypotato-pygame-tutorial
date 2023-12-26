import pygame, sys

from src import keyboard
from src.entities import PhysicsEntity, Player
from src.utils import load_image, load_images, Animation
from src.tilemap import Tilemap
from src.clouds import Clouds


class Game:
    def __init__(self):
        pygame.display.set_caption("Ninja game by DaFluffyPotato")
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player_idle': Animation(load_images('entities/player/idle'), 6),
            'player_run': Animation(load_images('entities/player/run'), 4),
            'player_jump': Animation(load_images('entities/player/jump')),
            'player_slide': Animation(load_images('entities/player/slide')),
            'player_wall_slide': Animation(load_images('entities/player/wall_slide')),
        }

        self.clock = pygame.time.Clock()
        self.keys = keyboard.Keyboard("wasd").get_keys()

        self._scroll = [0, 0]
        self.render_scroll = (0, 0)

        self.player = Player(self, (50, 50), (8, 15))
        self.player_movement_x = [False, False]
        self.player_movement_y = [False, False]

        self.camera_entity = None
        self.set_camera_entity(self.player)

        self.tilemap = Tilemap(self)

        self.clouds = Clouds(self.assets["clouds"])

        self.events = {
            "quit": 0,
            "up": 0,
            "down": 0,
            "right": 0,
            "left": 0,
        }

    def set_camera_entity(self, entity):
        self.camera_entity = entity

    def update_camera(self):
        self._scroll[0] += (self.camera_entity.get_rect().centerx - self.display.get_width() / 2 - self._scroll[0]) / 10
        self._scroll[1] += (self.camera_entity.get_rect().centery - self.display.get_height() / 2 - self._scroll[1]) / 10
        self.render_scroll = (int(self._scroll[0]), int(self._scroll[1]))

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
            self.display.blit(self.assets["background"], (0, 0))

            self.player.update(self.tilemap, (self.player_movement_x[0] - self.player_movement_x[1], 0))

            self.update_camera()

            self.clouds.update()
            self.clouds.render(self.display, self.render_scroll)
            self.tilemap.render(self.display, self.render_scroll)
            self.player.render(self.display, self.render_scroll)

            self.process_events()
            self.handle_input()
            running = not self.events["quit"]

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
            pygame.display.set_caption("Ninja game by DaFluffyPotato | FPS: " + str(int(self.clock.get_fps())))

        pygame.quit()
        sys.exit()
