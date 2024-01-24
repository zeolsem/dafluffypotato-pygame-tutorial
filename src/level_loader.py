import math
import random
import pygame

from src.entities import Enemy
from src.particle import Particle


class LevelLoader:
    def __init__(self, game):
        self.render_scroll = None
        self._scroll = None
        self.particles = []
        self.game = game
        self.leaf_spawners = []

    def load_level(self, map_id):
        self.game.tilemap.load('../data/maps/' + str(map_id) + '.json')

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

    def spawn_particle(self):
        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = [rect.x + random.random() * rect.width, rect.y + random.random() * rect.height]
                self.particles.append(Particle(self, 'leaf', pos, velocity=[0.1, 0.3], frame=random.randint(0, 20)))

    def draw_particles(self):
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.game.display, offset=self.game.render_scroll)
            if particle.type == 'leaf':
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            if kill:
                self.particles.remove(particle)
