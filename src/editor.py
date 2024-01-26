import os

import pygame
import sys

import keyboard
from utils import load_images
from tilemap import Tilemap

RENDER_SCALE = 4


class Editor:
    def __init__(self):
        pygame.display.set_caption("editor")
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))

        self.assets = {
            'decor': load_images(os.path.normpath('tiles/decor')),
            'grass': load_images(os.path.normpath('tiles/grass')),
            'large_decor': load_images(os.path.normpath('tiles/large_decor')),
            'stone': load_images(os.path.normpath('tiles/stone')),
            'spawners': load_images(os.path.normpath('tiles/spawners')),
        }

        self.clock = pygame.time.Clock()
        self.keys = keyboard.Keyboard("wasd").get_keys()
        self.mpos = (0, 0)

        self.render_scroll = (0, 0)

        self.player_movement_x = [False, False]
        self.player_movement_y = [False, False]

        self.camera_movement = [False, False, False, False]
        self.camera_pos = [0, 0]

        self.tilemap = Tilemap(self, tile_size=16)

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.ongrid = True

        self.events = {
            "quit": 0,
            "up": 0,
            "down": 0,
            "right": 0,
            "left": 0,
            "clicking": 0,
            "right_clicking": 0,
            "shift": 0,
            "g": 0,
        }

    def update_camera(self):
        self.camera_pos[0] += (self.camera_movement[1] - self.camera_movement[0]) * 2
        self.camera_pos[1] += (self.camera_movement[3] - self.camera_movement[2]) * 2
        self.render_scroll = (int(self.camera_pos[0]), int(self.camera_pos[1]))

    def process_events(self):
        keys = self.keys
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.events["quit"] = 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.events["clicking"] = 1
                    if not self.ongrid:
                        pos = (int(self.mpos[0] + self.render_scroll[0] - self.tilemap.tile_size // 2), int(self.mpos[1] + self.render_scroll[1] - self.tilemap.tile_size // 2))
                        self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': pos})
                if event.button == 3:
                    self.events["right_clicking"] = 1
                if self.events["shift"]:
                    if event.button == 4:
                        self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                    if event.button == 5:
                        self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                else:
                    if event.button == 4:
                        self.tile_variant = 0
                        self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                    if event.button == 5:
                        self.tile_variant = 0
                        self.tile_group = (self.tile_group + 1) % len(self.tile_list)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.events["clicking"] = 0
                if event.button == 3:
                    self.events["right_clicking"] = 0

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
                    self.events["shift"] = 1
                if event.key == keys["g"]:
                    self.events["g"] = not self.events["g"]
                    self.ongrid = self.events["g"]
                if event.key == keys["o"]:
                    self.save()
                if event.key == keys["t"]:
                    self.tilemap.autotile()

            if event.type == pygame.KEYUP:
                if event.key == keys["up"]:
                    self.events["up"] = 0
                if event.key == keys["down"]:
                    self.events["down"] = 0
                if event.key == keys["right"]:
                    self.events["right"] = 0
                if event.key == keys["left"]:
                    self.events["left"] = 0
                if event.key == keys["lshift"]:
                    self.events["shift"] = 0

    def handle_input(self):
        self.camera_movement = [self.events["left"], self.events["right"], self.events["up"], self.events["down"]]

    def run(self):
        print("select map to edit")
        for i, map_name in enumerate(sorted(os.listdir(os.path.normpath('data/maps')))):
            print(str(i) + ': ' + map_name)
        level = input("map id: ")
        self.tilemap.load(os.path.normpath('data/maps/' + str(level) + '.json'))
        running = True
        while running:
            self.display.fill((0, 0, 0))

            self.tilemap.render(self.display, self.render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant]
            current_tile_img.set_alpha(100)

            self.mpos = pygame.mouse.get_pos()
            self.mpos = [self.mpos[0] / RENDER_SCALE, self.mpos[1] / RENDER_SCALE]
            tile_pos = (int(self.mpos[0] + self.render_scroll[0]) // self.tilemap.tile_size, int(self.mpos[1] + self.render_scroll[1]) // self.tilemap.tile_size)

            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.render_scroll[0], tile_pos[1] * self.tilemap.tile_size - self.render_scroll[1]))
            else:
                self.display.blit(current_tile_img, (self.mpos[0] - self.tilemap.tile_size // 2, self.mpos[1] - self.tilemap.tile_size // 2))

            if self.events["clicking"] and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.events["right_clicking"]:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_rect = pygame.Rect(tile['pos'][0] - self.render_scroll[0], tile['pos'][1] - self.render_scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_rect.collidepoint(self.mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5,5))

            self.process_events()
            self.update_camera()
            self.handle_input()

            self.tilemap.render(self.display, self.render_scroll)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

            running = not self.events["quit"]

        pygame.quit()
        sys.exit()

    def save(self):
        self.tilemap.save(os.path.normpath('data/maps/{}.json'.format(input("map name: "))))


if __name__ == "__main__":
    Editor().run()
