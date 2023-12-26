import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0.0, 0.0]

        self.action = ''
        self.animation = None
        self.set_action("idle")
        self.anim_offset = (-3, -3)
        self.flip = False

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
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

        self.pos[0] += frame_movement[0]
        e_rect = self.get_rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if e_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    e_rect.right = rect.left
                    self.collisions["right"] = True
                elif frame_movement[0] < 0:
                    e_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = e_rect.x

        self.pos[1] += frame_movement[1]
        e_rect = self.get_rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if e_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    e_rect.bottom = rect.top
                    self.collisions["down"] = True
                elif frame_movement[1] < 0:
                    e_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = e_rect.y

        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True

        self.velocity[1] = min(5.0, self.velocity[1] + 0.1)
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0.0

        self.animation.update()

    def render(self, surf, offset):
        pos = (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), pos)


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0

    def update(self, tilemap, movement):
        super().update(tilemap, movement=movement)
        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
        if self.air_time > 4:
            self.set_action("jump")
        elif movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")
