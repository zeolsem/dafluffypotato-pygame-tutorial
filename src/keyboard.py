import pygame


class Keyboard():
    def __init__(self, layout):
        self.layout = {}
        if layout == "wasd":
            self.layout = {
                "up": pygame.K_w,
                "down": pygame.K_s,
                "left": pygame.K_a,
                "right": pygame.K_d,
            }
        elif layout == "arrows":
            self.layout = {
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
            }

        self.layout["lshift"] = pygame.K_LSHIFT
        self.layout["g"] = pygame.K_g
        self.layout["o"] = pygame.K_o
        self.layout["t"] = pygame.K_t
        # debug only
        self.layout["n"] = pygame.K_n

    def get_keys(self):
        return self.layout
