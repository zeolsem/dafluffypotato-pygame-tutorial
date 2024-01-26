import math
import os
import random
import pygame

from entities import Enemy
from particle import Particle


class LevelLoader:
    def __init__(self, game):
        self.render_scroll = None
        self._scroll = None
        self.particles = []
        self.game = game
        self.leaf_spawners = []
        self.transition = -30

    def load_level(self, map_id):
        self.game.tilemap.load(os.path.normpath('data/maps/' + str(map_id) + '.json'))
        print('loaded map ' + str(map_id))
        self.game.loader.particles.clear()
        self.game.projectiles.clear()

        self._scroll = self.game._scroll = [0, 0]
        self.render_scroll = self.game.render_scroll = (0, 0)

        for tree in self.game.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.game.enemies = []
        for spawner in self.game.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.game.player.pos = spawner['pos']
            else:
                self.game.enemies.append(Enemy(self.game, spawner['pos'], (8, 15)))

        self.game.projectiles = []
        self.game.particles = []

        self.game.player.dead = 0
        self.game.player.air_time = 0
        self.transition = -30

    def eval_transition(self):
        if not len(self.game.enemies):
            self.transition += 1
            if self.transition > 30:
                self.game.level = min(self.game.level + 1, len(os.listdir(os.path.normpath('data/maps'))) - 1)
                self.load_level(self.game.level)
        if self.transition < 0:
            self.transition += 1

        if self.transition:
            transition_surf = pygame.Surface(self.game.display.get_size())
            circle_center = (self.game.display.get_width()//2, self.game.display.get_height()//2)
            pygame.draw.circle(transition_surf, (255, 255, 255), circle_center, (30 - abs(self.transition)) * 8)
            transition_surf.set_colorkey((255, 255, 255))
            self.game.display.blit(transition_surf, (0, 0))

    def spawn_particles(self):
        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = [rect.x + random.random() * rect.width, rect.y + random.random() * rect.height]
                self.particles.append(Particle(self.game, 'leaf', pos, velocity=[0.1, 0.3], frame=random.randint(0, 20)))

    def draw_particles(self):
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.game.display, offset=self.game.render_scroll)
            if particle.type == 'leaf':
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            if kill:
                self.particles.remove(particle)
