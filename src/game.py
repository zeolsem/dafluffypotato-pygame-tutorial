import math

import pygame, sys

import random
from src import keyboard
from src.entities import Player
from src.level_loader import LevelLoader
from src.particle import spawn_particle
from src.spark import Spark
from src.utils import load_image, load_images, Animation
from src.tilemap import Tilemap
from src.clouds import Clouds


class Game:
    def __init__(self):
        self.projectiles = []
        pygame.display.set_caption("Ninja game by DaFluffyPotato")
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy_idle': Animation(load_images('entities/enemy/idle'), 6),
            'enemy_run': Animation(load_images('entities/enemy/run'), 4),
            'player_idle': Animation(load_images('entities/player/idle'), 6),
            'player_run': Animation(load_images('entities/player/run'), 4),
            'player_jump': Animation(load_images('entities/player/jump')),
            'player_slide': Animation(load_images('entities/player/slide')),
            'player_wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=10, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'spawners': load_images('tiles/spawners'),
            'projectile': load_image('projectile.png'),
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('../data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('../data/sfx/dash.wav'),
            'shoot': pygame.mixer.Sound('../data/sfx/shoot.wav'),
            'hit': pygame.mixer.Sound('../data/sfx/hit.wav'),
            'ambience': pygame.mixer.Sound('../data/sfx/ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['jump'].set_volume(0.7)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)

        self.clock = pygame.time.Clock()
        self.keys = keyboard.Keyboard("wasd").get_keys()

        self.player = Player(self, (50, 50), (8, 15))
        self.player_movement_x = [False, False]
        self.player_movement_y = [False, False]
        self.player.dead = 0
        self.enemies = []

        self.camera_entity = None
        self.set_camera_entity(self.player)
        self.render_scroll = (0, 0)
        self._scroll = [0, 0]
        self.screenshake = 0

        self.tilemap = Tilemap(self)
        self.loader = LevelLoader(self)
        # self.tilemap.load('../maps/map.json')
        self.level = 0
        self.loader.load_level(self.level)

        self.clouds = Clouds(self.assets["clouds"])
        self.sparks = []

        self.events = {
            "quit": 0,
            "up": 0,
            "past_up": 0,  # Used to check if the up key was pressed last frame
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

    def update_enemies(self):
        for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap, (0, 0))
            enemy.render(self.display, offset=self.render_scroll)
            if kill:
                self.enemies.remove(enemy)

    def process_events(self):
        keys = self.keys
        self.events["past_up"] = self.events["up"]
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
                if event.key == keys["lshift"]:
                    self.player.dash(self.events["right"] - self.events["left"])
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
        if self.events["up"] != self.events["past_up"] and self.events["up"]:
            self.player.jump()

    def draw_sparks(self):
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display, offset=self.render_scroll)
            if kill:
                self.sparks.remove(spark)
    def handle_projectiles(self):
        for projectile in self.projectiles.copy():
            projectile[0][0] += projectile[1]
            projectile[2] += 1
            img = self.assets['projectile']
            self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - self.render_scroll[0],
                                    projectile[0][1] - img.get_height() / 2 - self.render_scroll[1]))
            if self.tilemap.solid_check(projectile[0]):
                self.projectiles.remove(projectile)
                for i in range(0, 6):
                    self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 * random.random()))
            elif projectile[2] > 360:
                self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50:
                if pygame.Rect(self.player.get_rect().centerx - 4, self.player.get_rect().centery - 4, 8, 8).collidepoint(projectile[0]):
                    self.projectiles.remove(projectile)
                    self.player.dead += 1
                    self.screenshake = max(32, self.screenshake)
                    for i in range(20):
                        spawn_particle(self, self.player)
                        Spark.spawn_spark(self, projectile)

    def run(self):
        running = True
        pygame.mixer.music.load('../data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.sfx['ambience'].play(-1)
        while running:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets["background"], (0, 0))

            # update game logic
            self.player.update(self.tilemap, (self.player_movement_x[0] - self.player_movement_x[1], 0))

            self.update_camera()

            self.clouds.update()
            self.clouds.render(self.display_2, self.render_scroll)

            self.tilemap.render(self.display, self.render_scroll)

            self.update_enemies() # ALSO RENDERS ENEMIES
            self.player.render(self.display, self.render_scroll)
            # outlines
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                self.display_2.blit(display_sillhouette, (offset[0], offset[1]))

            self.handle_projectiles()

            self.loader.spawn_particles()
            self.loader.draw_particles()

            self.draw_sparks()

            self.process_events()
            self.handle_input()
            running = not self.events["quit"]

            self.loader.eval_transition()
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screenshake = max(0, self.screenshake - 1)

            # self.display_2.blit(display_sillhouette, (0, 0))
            self.display_2.blit(self.display, (0, 0))

            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)
            pygame.display.set_caption("Ninja game by DaFluffyPotato | FPS: " + str(int(self.clock.get_fps())))

        pygame.quit()
        sys.exit()
