import pygame
from os import path
from settings import *
import spritesheet
vec = pygame.math.Vector2

class Points(pygame.sprite.Sprite):
    def __init__(self, app, pos, score):
        self.app = app
        pygame.sprite.Sprite.__init__(self)
        self.load_graphics()
        if score == 200:
            self.frame = 0
        elif score == 400:
            self.frame = 1
        elif score == 800:
            self.frame = 2
        elif score == 1600:
            self.frame = 3
        self.image = self.sc_animation[self.frame]
        self.image = pygame.transform.scale(self.image, (8 * SCALE, 16 * SCALE))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = pos.x
        self.rect.y = pos.y

        self.timer = 60

    def update(self):
        self.timer -= 1
        if self.timer < 0:
            self.kill()


    def load_graphics(self):
        sc_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'bonus_points_sprite.png'))
        self.sc_animation = sc_spritesheet.image_list([(0, 0, 8, 16), (16, 0, 8, 16), (32, 0, 8, 16), (48, 0, 8, 16)], colorkey=BLACK)