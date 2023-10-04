import pygame
from os import path
import numpy as np
from settings import *
import spritesheet
vec = pygame.math.Vector2

class Pellet(pygame.sprite.Sprite):
    def __init__(self, app, pos, superpellet):
        self.app = app
        pygame.sprite.Sprite.__init__(self)
        self.superpellet = superpellet
        self.load_graphics()
        self.image = self.pe_animation[0]
        self.image = pygame.transform.scale(self.image, (8 * SCALE, 8 * SCALE))
        self.image.set_colorkey(BLACK)
        self.grid_pos = pos
        self.sprite_offset = 0 * SCALE
        self.coord_pos = ORIGIN + self.grid_pos * TILE_SIZE - (self.sprite_offset, self.sprite_offset)
        self.rect = pygame.Rect(self.coord_pos.x, self.coord_pos.y, 1, 1)

        self.animation_frame = 0
        self.animation_delay = 10
        self.animation_timer = self.animation_delay // self.app.game_speed

    def update(self):
        if self.superpellet:
            self.animation_timer -= 1
            if self.animation_timer < 0:
                self.animation_timer = self.animation_delay // self.app.game_speed
                self.animation_frame = np.mod(self.animation_frame + 1, 2)
                self.image = self.pe_animation[self.animation_frame]
                self.image = pygame.transform.scale(self.image, (8 * SCALE, 8 * SCALE))


    def load_graphics(self):
        if self.superpellet == False:
            pe_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'pellet_sprite.png'))
            pe_sprite_coords = [(0, 0, 8, 8)]
        else:
            pe_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'superpellet_sprite.png'))
            pe_sprite_coords = [(0, 0, 8, 8), (8, 0, 8, 8)]

        self.pe_animation = pe_spritesheet.image_list(pe_sprite_coords, colorkey=BLACK)