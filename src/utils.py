import pygame
import os

BASE_IMG_PATH = os.path.realpath("../data/images/") + os.sep


def load_image(path, editor=0):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0,0,0))
    return img


def load_images(path, editor=0):

    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        img = load_image(path + os.sep + img_name, editor)
        images.append(img)
    return images


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (len(self.images) * self.img_duration)
        else:
            self.frame = min(self.frame + 1, len(self.images) * self.img_duration - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]
