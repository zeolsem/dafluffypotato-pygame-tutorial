import random
import math
import pygame
from src.particle import Particle, spawn_particle
from src.spark import Spark


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0.0, 0.0]
        self.acceleration = 0.0
        self.max_speed = 2.0
        self.wall_slide = False
        self.slideable = False
        self.on_ground = False

        self.action = ''
        self.animation = None
        self.set_action("idle")
        self.anim_offset = (-3, -3)
        self.flip = False
        self.last_movement = [0, 0]

        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

    def get_rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.animation = self.game.assets[self.type + '_' + self.action].copy()

    def update(self, tilemap, movement):
        acceleration = movement[0]
        self.velocity[0] += acceleration * 0.16
        self.velocity[0] = min(self.max_speed, max(-self.max_speed, self.velocity[0]))
        # frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

        if self.velocity[0] > 0:
            self.flip = False
        elif self.velocity[0] < 0:
            self.flip = True

        self.pos[0] += self.velocity[0]
        e_rect = self.get_rect()
        approx_rect = self.get_rect()
        approx_rect.left -= 1
        approx_rect.top -= 1
        approx_rect.width += 2
        approx_rect.height += 1
        self.slideable = False
        for rect in tilemap.physics_rects_around(self.pos):
            if e_rect.colliderect(rect):
                if (movement[0] > 0 and self.velocity[0] >= 0) or self.velocity[0] > 0:
                    self.flip = False
                    e_rect.right = rect.left
                    self.collisions["right"] = True
                elif (movement[0] < 0 and self.velocity[0] <= 0) or self.velocity[0] < 0:
                    self.flip = True
                    e_rect.left = rect.right
                    self.collisions["left"] = True
                else:
                    self.wall_slide = False
                self.pos[0] = e_rect.x
            if approx_rect.colliderect(rect):
                if rect.top > e_rect.top - e_rect.height / 4:
                    self.slideable = True
                if rect.x > e_rect.x:
                    self.flip = False
                    self.collisions["right"] = True
                elif rect.x < e_rect.x:
                    self.flip = True
                    self.collisions["left"] = True
            else:
                self.wall_slide = False
            self.wall_slide = self.slideable

        if self.collisions["left"] or self.collisions["right"]:
            self.velocity[0] = 0.0

        self.pos[1] += self.velocity[1]
        e_rect = self.get_rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if e_rect.colliderect(rect):
                if self.velocity[1] > 0:
                    e_rect.bottom = rect.top
                    self.collisions["down"] = True
                elif self.velocity[1] < 0:
                    e_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = e_rect.y

        self.last_movement = movement

        self.velocity[1] = min(5.0, self.velocity[1] + 0.15)
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0.0

        self.velocity[0] *= 0.95
        self.animation.update()

    def render(self, surf, offset):
        pos = (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), pos)


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "enemy", pos, size)

        self.max_speed = 0.8
        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if tilemap.solid_check((self.get_rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
            if self.collisions["left"] or self.collisions["right"]:
                self.flip = not self.flip
        else:
            self.flip = not self.flip
            self.velocity[0] = 0

        # handle shooting
        if self.walking:
            movement = (-0.5 if self.flip else 0.5, movement[1])
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[1]) < 16:
                    if self.flip and dis[0] < 0:
                        self.game.projectiles.append([[self.get_rect().centerx - 7, self.get_rect().centery], -3, 0])
                        for i in range(7):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi,
                                                          2 * random.random()))
                    if not self.flip and dis[0] > 0:
                        self.game.projectiles.append([[self.get_rect().centerx + 7, self.get_rect().centery], 3, 0])
                        for i in range(7):
                            self.game.sparks.append(
                                Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 * random.random()))

        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
            self.velocity[0] = random.random() * 2 - 1

        super().update(tilemap, movement=movement)

        # set animation
        if movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

        if abs(self.game.player.dashing) >= 50:
            if self.get_rect().colliderect(self.game.player.get_rect()):
                self.enemy_death()
                return True

    def enemy_death(self):
        self.game.screenshake = max(24, self.game.screenshake)
        for i in range(0, 15):
            # add sparks
            angle = random.random() * math.pi * 2
            self.game.sparks.append(Spark(self.get_rect().center, angle, 2 + random.random()))
            # add particles
            speed = random.random() * 5
            velocity = [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5]
            p = Particle(self.game, 'particle', self.get_rect().center, velocity, frame=random.randint(0, 7))
            self.game.particles.append(p)
        # add 'slashing' sparks
        self.game.sparks.append(Spark(self.get_rect().center, 0, 5))
        self.game.sparks.append(Spark(self.get_rect().center, math.pi, 5))

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        gun_pos = (self.get_rect().centerx - offset[0], self.get_rect().centery - offset[1])
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (gun_pos[0] - 4, gun_pos[1]))
        else:
            surf.blit(self.game.assets['gun'], (gun_pos[0], gun_pos[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.jumps = 2
        self.max_speed = 2.0
        self.wall_slide = False
        self.dashing = 0
        self.dead = 0

    def update(self, tilemap, movement):
        # Handle the player's death
        if self.air_time > 150:
            self.game.screenshake = max(16, self.game.screenshake)
            self.dead += 1

        if self.dead:
            self.dead += 1
            self.game.loader.transition += 1
            if self.dead > 30:
                self.game.loader.load_level(self.game.level)
                self.dead = 0
            return

        # limit velocity
        self.velocity[0] = min(max(-self.max_speed, self.velocity[0]), self.max_speed)
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 2
            self.on_ground = True
        else:
            self.on_ground = False

        # stop player sliding if he's on the floor
        for rect in tilemap.physics_rects_around(self.pos):
            if rect.top <= self.get_rect().bottom and abs(rect.centerx - self.get_rect().centerx) < 8:
                self.slideable = False

        if self.slideable and (((self.collisions["left"] or self.collisions["right"]) and self.air_time > 4) or (
                self.wall_slide and self.velocity[0] == 0)):
            if not self.wall_slide:
                self.velocity[1] *= 0.8
            self.wall_slide = True
            self.velocity[1] = min(0.5, self.velocity[1])
            self.set_action("wall_slide")
        else:
            self.wall_slide = False

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action("jump")
            elif movement[0] != 0:
                self.set_action("run")
            else:
                self.set_action("idle")

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        else:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.max_speed = 8
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 50:
                self.velocity[0] *= 0.2
            p_vel = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.loader.particles.append(
                Particle(self.game, 'particle', self.get_rect().center, p_vel, frame=random.randint(0, 7)))
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                spawn_particle(self.game, self)

        if not self.collisions["down"] and self.jumps >= 2 and self.air_time > 5:
            self.jumps -= 1

    def render(self, surf, offset=(0, 0)):
        if self.dead:
            return
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)
        else:
            pass

    def jump(self):
        if self.wall_slide:
            if self.flip:
                self.velocity[0] = 3.0
            elif not self.flip:
                self.velocity[0] = -3.0
            self.velocity[1] = -3.0
            self.air_time = 5
            self.jumps = max(0, self.jumps - 1)
            return True
        elif self.jumps:
            self.velocity[1] = -3.7
            self.jumps -= 1
            self.air_time = 5
            return True
        return False

    def dash(self, direction):
        if self.dead:
            return
        if not self.dashing:
            if direction == 1:
                self.dashing = 60
            elif direction == -1:
                self.dashing = -60
            else:
                self.dashing = 60 * (-1 if self.flip else 1)
