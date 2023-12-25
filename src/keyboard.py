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

    def get_keys(self):
        return self.layout