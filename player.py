import pygame
from os import path
import numpy as np
from settings import *
import spritesheet
vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        self.app = app
        pygame.sprite.Sprite.__init__(self)
        self.load_graphics()
        self.image = self.pl_left_animation[0]
        self.image = pygame.transform.scale(self.image, (16 * SCALE, 16 * SCALE))
        self.image.set_colorkey(BLACK)

        self.grid_pos = pos
        self.x = int(self.grid_pos.x)
        self.y = int(self.grid_pos.y)
        self.sprite_offset = vec(4 * SCALE, 4 * SCALE)
        self.coord_pos = ORIGIN + self.grid_pos*TILE_SIZE - self.sprite_offset
        self.rect = pygame.Rect(self.coord_pos.x, self.coord_pos.y, 8*SCALE, 8*SCALE)

        self.speed = 1 * SCALE
        self.move = True
        self.move_time = int(8 * SCALE // (self.speed*self.app.game_speed) - 1)
        self.move_timer = self.move_time
        self.move_pause_timer = 0
        self.move_dir = 180
        self.direction = vec(-1,0)

        self.move_animation_delay = 2
        self.death_animation_delay = 12
        self.animation_frame = 0
        self.animation_delay = self.move_animation_delay
        self.animation_timer = self.animation_delay // self.app.game_speed
        self.death_timer = 13*self.death_animation_delay


    def update(self):
        self.x = int(np.mod(self.grid_pos.x, 28))
        self.y = int(np.mod(self.grid_pos.y, 31))
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_BACKSPACE]:
            if self.app.state == 'playing':
                self.app.game_restart()
        elif keystate[pygame.K_p]:
            self.app.game_pause = True
        if self.app.player_alive and not self.app.game_pause:
            if keystate[pygame.K_a] or keystate[pygame.K_LEFT]:
                self.left_press()
            elif keystate[pygame.K_d] or keystate[pygame.K_RIGHT]:
                self.right_press()
            elif keystate[pygame.K_w] or keystate[pygame.K_UP]:
                self.up_press()
            elif keystate[pygame.K_s] or keystate[pygame.K_DOWN]:
                self.down_press()
            self.movement()
        if not self.app.player_alive:
            self.die()

    def movement(self):
        if self.move_pause_timer > 0:
            self.move = False
            self.move_pause()

        if self.move:
            self.animation_timer -= 1
            if self.animation_timer < 0:
                self.animation_timer = self.animation_delay//self.app.game_speed
                self.animation_frame = np.mod(self.animation_frame + 1, 4)
                self.animate("move")

            if self.move_dir == 0:
                self.coord_pos.x = np.mod(self.coord_pos.x + self.speed*self.app.game_speed, 28*TILE_SIZE)
            elif self.move_dir == 90:
                self.coord_pos.y = np.mod(self.coord_pos.y - self.speed*self.app.game_speed, 32*TILE_SIZE)
            elif self.move_dir == 180:
                self.coord_pos.x = np.mod(self.coord_pos.x - self.speed*self.app.game_speed, 28*TILE_SIZE)
            elif self.move_dir == 270:
                self.coord_pos.y = np.mod(self.coord_pos.y + self.speed*self.app.game_speed, 32*TILE_SIZE)

            self.rect.x = self.coord_pos.x
            self.rect.y = self.coord_pos.y
            self.grid_pos.x = int((self.coord_pos.x + 8 * SCALE - ORIGIN.x) // TILE_SIZE)
            self.grid_pos.y = int((self.coord_pos.y + 8 * SCALE - ORIGIN.y) // TILE_SIZE)
            if self.move_dir == 0:
                self.direction = vec(1, 0)
            elif self.move_dir == 90:
                self.direction = vec(0, -1)
            elif self.move_dir == 180:
                self.direction = vec(-1, 0)
            elif self.move_dir == 270:
                self.direction = vec(0, 1)

            self.move_timer -= 1
            if self.move_timer < 0:
                self.move_timer = self.move_time
                self.snap_to_grid()
                if self.move_dir == 0 and self.app.map[self.y][np.mod(self.x + 1, 28)] == 1:
                    self.move = False
                elif self.move_dir == 90 and self.app.map[np.mod(self.y - 1, 31)][self.x] == 1:
                    self.move = False
                elif self.move_dir == 180 and self.app.map[self.y][np.mod(self.x - 1, 28)] == 1:
                    self.move = False
                elif self.move_dir == 270 and self.app.map[np.mod(self.y + 1, 31)][self.x] == 1:
                    self.move = False


    def snap_to_grid(self):
        self.coord_pos = ORIGIN + self.grid_pos*TILE_SIZE - self.sprite_offset
        self.rect.x = self.coord_pos.x
        self.rect.y = self.coord_pos.y

    def jump_to_position(self, pos):
        self.grid_pos = pos + vec(0,0)
        self.snap_to_grid()

    def distance_to_tile(self, dist):
        snap_x = ORIGIN.x + self.grid_pos.x * TILE_SIZE - self.sprite_offset.x
        snap_y = ORIGIN.y + self.grid_pos.y * TILE_SIZE - self.sprite_offset.y
        if np.abs(self.coord_pos.x - snap_x) < dist and np.abs(self.coord_pos.y - snap_y) < dist:
            return True
        else:
            return False


    def left_press(self):
        if self.app.map[self.y][np.mod(self.x - 1, 28)] == 0 and self.move_dir != 180:
            if self.move_dir == 90 or self.move_dir == 270:
                if self.distance_to_tile(3*SCALE):
                    self.snap_to_grid()
                    self.move_dir = 180
                    self.move_timer = self.move_time
                    self.move = True
            elif self.move_dir == 0:
                self.move_dir = 180
                self.move_timer = self.move_time - self.move_timer      # we add only the time elapsed since leaving last grid point to timer
                self.move = True
            elif self.move_dir == -1:
                self.move_dir = 180
                self.move_timer = self.move_time
                self.move = True

    def right_press(self):
        if self.app.map[self.y][np.mod(self.x + 1, 28)] == 0 and self.move_dir != 0:
            if self.move_dir == 90 or self.move_dir == 270:
                if self.distance_to_tile(3*SCALE):
                    self.snap_to_grid()
                    self.move_dir = 0
                    self.move_timer = self.move_time
                    self.move = True
            elif self.move_dir == 180:
                self.move_dir = 0
                self.move_timer = self.move_time - self.move_timer
                self.move = True
            elif self.move_dir == -1:
                self.move_dir = 0
                self.move_timer = self.move_time
                self.move = True

    def up_press(self):
        if self.app.map[np.mod(self.y - 1, 31)][self.x] == 0 and self.move_dir != 90:
            if self.move_dir == 0 or self.move_dir == 180:
                if self.distance_to_tile(3*SCALE):
                    self.snap_to_grid()
                    self.move_dir = 90
                    self.move_timer = self.move_time
                    self.move = True
            elif self.move_dir == 270:
                self.move_dir = 90
                self.move_timer = self.move_time - self.move_timer
                self.move = True
            elif self.move_dir == -1:
                self.move_dir = 90
                self.move_timer = self.move_time
                self.move = True

    def down_press(self):
        if self.app.map[np.mod(self.y + 1, 31)][self.x] == 0 and self.move_dir != 270:
            if self.move_dir == 0 or self.move_dir == 180:
                if self.distance_to_tile(3*SCALE):
                    self.snap_to_grid()
                    self.move_dir = 270
                    self.move_timer = self.move_time
                    self.move = True
            elif self.move_dir == 90:
                self.move_dir = 270
                self.move_timer = self.move_time - self.move_timer
                self.move = True
            elif self.move_dir == -1:
                self.move_dir = 270
                self.move_timer = self.move_time
                self.move = True

    def load_graphics(self):
        pl_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'pacman_sprite.png'))
        pl_right0 = (0, 0, 16, 16)
        pl_right1 = (16, 0, 16, 16)
        pl_right2 = (32, 0, 16, 16)
        pl_right3 = (48, 0, 16, 16)
        pl_right_coords = [pl_right0, pl_right1, pl_right2, pl_right3]
        pl_up0 = (0, 16, 16, 16)
        pl_up1 = (16, 16, 16, 16)
        pl_up2 = (32, 16, 16, 16)
        pl_up3 = (48, 16, 16, 16)
        pl_up_coords = [pl_up0, pl_up1, pl_up2, pl_up3]
        pl_left0 = (0, 32, 16, 16)
        pl_left1 = (16, 32, 16, 16)
        pl_left2 = (32, 32, 16, 16)
        pl_left3 = (48, 32, 16, 16)
        pl_left_coords = [pl_left0, pl_left1, pl_left2, pl_left3]
        pl_down0 = (0, 48, 16, 16)
        pl_down1 = (16, 48, 16, 16)
        pl_down2 = (32, 48, 16, 16)
        pl_down3 = (48, 48, 16, 16)
        pl_down_coords = [pl_down0, pl_down1, pl_down2, pl_down3]

        pl_die_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'pacman_die_sprite.png'))
        pl_die0 = (0, 0, 16, 16)
        pl_die1 = (16, 0, 16, 16)
        pl_die2 = (32, 0, 16, 16)
        pl_die3 = (48, 0, 16, 16)
        pl_die4 = (64, 0, 16, 16)
        pl_die5 = (80, 0, 16, 16)
        pl_die6 = (96, 0, 16, 16)
        pl_die7 = (112, 0, 16, 16)
        pl_die8 = (128, 0, 16, 16)
        pl_die9 = (144, 0, 16, 16)
        pl_die10 = (160, 0, 16, 16)
        pl_die11 = (176, 0, 16, 16)
        pl_die12 = (192, 0, 16, 16)
        pl_die_coords = [pl_die0, pl_die1, pl_die2, pl_die3, pl_die4, pl_die5, pl_die6, pl_die7, pl_die8, pl_die9, pl_die10, pl_die11, pl_die12]

        self.pl_right_animation = pl_spritesheet.image_list(pl_right_coords, colorkey=BLACK)
        self.pl_up_animation = pl_spritesheet.image_list(pl_up_coords, colorkey=BLACK)
        self.pl_left_animation = pl_spritesheet.image_list(pl_left_coords, colorkey=BLACK)
        self.pl_down_animation = pl_spritesheet.image_list(pl_down_coords, colorkey=BLACK)
        self.pl_die = pl_die_spritesheet.image_list(pl_die_coords, colorkey=BLACK)

    def die(self):
        if self.app.player_alive:
            self.app.player_alive = False
            self.animation_delay = self.death_animation_delay
            self.death_timer = 13*self.death_animation_delay
            self.animation_frame = 0
        self.animation_timer -= 1
        if self.animation_timer < 0:
            self.animation_timer = self.animation_delay // self.app.game_speed
            self.animation_frame = np.mod(self.animation_frame + 1, 13)
            self.animate("death")
        self.death_timer -= 1
        if self.death_timer < 0:
            self.animation_delay = self.move_animation_delay
            self.app.level_restart()

    def initiate(self, pos):
        self.jump_to_position(pos)
        self.move_dir = 180
        self.direction = vec(-1, 0)
        self.move = True
        self.move_timer = self.move_time
        self.image = self.pl_left_animation[0]
        self.image = pygame.transform.scale(self.image, (16 * SCALE, 16 * SCALE))
        self.animation_delay = self.move_animation_delay
        self.animation_frame = 0
        self.animation_timer = self.animation_delay // self.app.game_speed

    def move_pause(self):
        self.move_pause_timer -= 1
        if self.move_pause_timer <= 0:
            self.move = True

    def animate(self, animation):
        if animation == "move":
            if self.move_dir == 0:
                self.image = self.pl_right_animation[self.animation_frame]
            elif self.move_dir == 90:
                self.image = self.pl_up_animation[self.animation_frame]
            elif self.move_dir == 180:
                self.image = self.pl_left_animation[self.animation_frame]
            elif self.move_dir == 270:
                self.image = self.pl_down_animation[self.animation_frame]
        elif animation == 'death':
            self.image = self.pl_die[self.animation_frame]
        self.image = pygame.transform.scale(self.image, (16*SCALE, 16*SCALE))