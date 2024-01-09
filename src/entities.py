import pygame


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
                if rect.top > e_rect.top - e_rect.height/4:
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

        self.velocity[1] = min(5.0, self.velocity[1] + 0.1)
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0.0

        self.velocity[0] *= 0.95
        self.animation.update()

    def render(self, surf, offset):
        pos = (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), pos)


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.jumps = 2
        self.wall_slide = False

    def update(self, tilemap, movement):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 2

        if self.slideable and (((self.collisions["left"] or self.collisions["right"]) and self.air_time > 4) or (self.wall_slide and self.velocity[0] == 0)):
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

    def jump(self):
        if self.wall_slide:
            if self.flip:
                self.velocity[0] = 3.0
                self.velocity[1] = -2.0
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip:
                self.velocity[0] = -3.0
                self.velocity[1] = -2.0
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] = -3.0
            self.jumps -= 1
            self.air_time = 5
            return True
        return False
