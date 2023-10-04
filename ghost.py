import pygame
from os import path
import numpy as np
from settings import *
import spritesheet
vec = pygame.math.Vector2

class Ghost(pygame.sprite.Sprite):
    def __init__(self, app, pos, color, ai):
        self.app = app
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.col = RED
        if self.color == 'blue':
            self.col = BLUE
        elif self.color == 'pink':
            self.col = PINK
        elif self.color == 'orange':
            self.col = ORANGE
        self.ai = ai
        self.load_graphics()
        self.image = self.gh_left_animation[0]
        self.image = pygame.transform.scale(self.image, (16 * SCALE, 16 * SCALE))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.grid_pos = pos
        self.x = int(self.grid_pos.x)
        self.y = int(self.grid_pos.y)
        self.sprite_offset = vec(4 * SCALE, 4 * SCALE)
        self.coord_pos = ORIGIN + self.grid_pos*TILE_SIZE - self.sprite_offset
        self.rect.x = self.coord_pos.x
        self.rect.y = self.coord_pos.y

        self.max_speed = 1 * SCALE
        self.speed = self.max_speed
        self.move = True
        self.move_time = int(8 * SCALE // (self.speed*self.app.game_speed) - 1)
        self.move_timer = self.move_time
        self.move_dir = 180

        self.target = vec(0,0)           # I add vec(0,0) to copy the value, not reference, of player.grid_pos
        self.mode = 'in_box'
        self.frightened = False
        self.frightened_timer = 0
        self.frightened_time = 500

        self.move_animation_delay = 6
        self.frightened_animation_delay = 8
        self.animation_frame = 0
        self.animation_delay = self.move_animation_delay
        self.animation_timer = self.animation_delay // self.app.game_speed
        self.animation_pause_timer = 0

        self.in_box = True
        self.points = 0


    def update(self):
        self.x = int(np.mod(self.grid_pos.x, 28))
        self.y = int(np.mod(self.grid_pos.y, 31))
        self.animation_logic()
        if self.app.player_alive and not self.app.game_pause:
            self.movement()
            if self.mode == 'chase':
                if self.grid_pos.y == 14 and (self.grid_pos.x <= 1 or self.grid_pos.x >= 26):
                    self.speed = .5 * self.max_speed
                else:
                    self.speed = self.max_speed
            elif self.mode == 'frightened':
                self.speed = .6 * self.max_speed
                self.frightened_action()
            elif self.mode == 'return':
                self.speed = 1.4 * self.max_speed
                self.animation_pause_timer = 0
            if self.mode == 'in_box':
                self.sprite_offset.x = 1 * SCALE
            else:
                self.sprite_offset.x = 4 * SCALE

    def animation_logic(self):
        if self.move and self.app.player_alive and not self.app.game_pause:
            if self.animation_pause_timer <= 0:
                self.animation_timer -= 1
            else:
                self.animation_frame = 0
                self.animation_pause_timer -= 1
        if self.animation_timer < 0:
            if self.mode == 'chase' or self.mode == 'in_box':
                self.animation_timer = self.animation_delay // self.app.game_speed
                self.animation_frame = np.mod(self.animation_frame + 1, 2)
                self.animate('move')
            elif self.mode == 'frightened':
                self.animation_timer = self.frightened_animation_delay // self.app.game_speed
                self.animation_frame = np.mod(self.animation_frame + 1, 4)
                self.animate('frightened')
            elif self.mode == 'return':
                self.animation_timer = self.animation_delay // self.app.game_speed
                self.animation_frame = np.mod(self.animation_frame + 1, 1)
                self.animate('return')
        if self.mode == 'eaten':
            self.animation_timer = 0
            self.animate('eaten')

    def movement(self):
        if self.move:
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
            self.x = int(np.mod(self.grid_pos.x, 28))
            self.y = int(np.mod(self.grid_pos.y, 31))

            self.move_timer -= 1
            if self.move_timer < 0:
                self.move = False
                self.move_timer = int(8 * SCALE // (self.speed*self.app.game_speed) - 1)
                self.snap_to_grid()
                self.choose_target()
                self.choose_direction()
                self.move = True

            if self.grid_pos == vec(13,11) and self.mode == 'return':
                self.mode = 'chase'


    def snap_to_grid(self):
        self.coord_pos = ORIGIN + self.grid_pos*TILE_SIZE - self.sprite_offset
        self.rect.x = self.coord_pos.x
        self.rect.y = self.coord_pos.y

    def jump_to_position(self, pos):
        self.grid_pos = pos + vec(0,0) # the +vec(0,0) is to de-reference grid_pos from pos
        self.snap_to_grid()

    def distance_to_tile(self, dist):
        snap_x = ORIGIN.x + self.grid_pos.x * TILE_SIZE - self.sprite_offset.x
        snap_y = ORIGIN.y + self.grid_pos.y * TILE_SIZE - self.sprite_offset.y
        if np.abs(self.coord_pos.x - snap_x) < dist and np.abs(self.coord_pos.y - snap_y) < dist:
            return True
        else:
            return False

    def choose_direction(self):
        up_dist = 10000
        left_dist = 10000
        down_dist = 10000
        right_dist = 10000
        min_dist = 10000
        if self.move_dir != 270 and self.app.map[np.mod(self.y - 1, 31)][self.x] == 0:
            up_dist = (self.target.x - self.grid_pos.x)*(self.target.x - self.grid_pos.x) + (self.target.y - (self.grid_pos.y-1))*(self.target.y - (self.grid_pos.y-1))
        if self.move_dir != 0 and self.app.map[self.y][np.mod(self.x - 1, 28)] == 0:
            left_dist = (self.target.x - (self.grid_pos.x-1))*(self.target.x - (self.grid_pos.x-1)) + (self.target.y - self.grid_pos.y)*(self.target.y - self.grid_pos.y)
        if self.move_dir != 90 and self.app.map[np.mod(self.y + 1, 31)][self.x] == 0:
            down_dist = (self.target.x - self.grid_pos.x)*(self.target.x - self.grid_pos.x) + (self.target.y - (self.grid_pos.y+1))*(self.target.y - (self.grid_pos.y+1))
        if self.move_dir != 180 and self.app.map[self.y][np.mod(self.x + 1, 28)] == 0:
            right_dist = (self.target.x - (self.grid_pos.x+1)) * (self.target.x - (self.grid_pos.x+1)) + (self.target.y - self.grid_pos.y) * (self.target.y - self.grid_pos.y)
        min_dist = right_dist
        self.move_dir = 0
        if down_dist <= min_dist:
            min_dist = down_dist
            self.move_dir = 270
        if left_dist <= min_dist:
            min_dist = left_dist
            self.move_dir = 180
        if up_dist <= min_dist:
            min_dist = up_dist
            self.move_dir = 90


    def choose_target(self):
        t = vec(0,0)
        if self.mode == 'chase':
            if self.ai == 'blinky':
                t = self.app.player.grid_pos
            elif self.ai == 'pinky':
                t = self.app.player.grid_pos + 4*self.app.player.direction
            elif self.ai == 'inky':
                t = 2*self.app.player.grid_pos - self.app.blinky.grid_pos + 4*self.app.player.direction
            elif self.ai == 'clyde':
                diff = self.grid_pos - self.app.player.grid_pos
                if diff.length() >= 8:
                   t = self.app.player.grid_pos
                else:
                    t = vec(2,30)
        elif self.mode == 'frightened':
            rand_dir = np.random.randint(0,4)
            if rand_dir == 0:
                t = self.grid_pos + vec(5,0)
            elif rand_dir == 1:
                t = self.grid_pos + vec(0,-5)
            elif rand_dir == 2:
                t = self.grid_pos + vec(-5,0)
            elif rand_dir == 3:
                t = self.grid_pos + vec(0,5)
        elif self.mode == 'return':
            t = vec(13, 11)
        elif self.mode == 'in_box':
            if self.ai == 'blinky':
                t = PINKY_START_GRID_POS
            elif self.ai == 'pinky':
                t = PINKY_START_GRID_POS
            elif self.ai == 'inky':
                t = INKY_START_GRID_POS
            elif self.ai == 'clyde':
                t = CLYDE_START_GRID_POS
        if t.x > 27:
            t.x = 27
        if t.x < 0:
            t.x = 0
        if t.y > 30:
            t.y = 30
        if t.y < 0:
            t.y = 0
        self.target = t

    def initiate(self, pos):
        self.mode = 'chase'
        self.jump_to_position(pos)
        self.move_dir = 180
        self.move = True
        self.move_timer = self.move_time
        self.image = self.gh_left_animation[0]
        self.image = pygame.transform.scale(self.image, (16 * SCALE, 16 * SCALE))
        self.animation_delay = self.move_animation_delay
        self.animation_frame = 0
        self.animation_pause_timer = 0
        self.animation_timer = self.animation_delay // self.app.game_speed
        self.speed = 1*SCALE
        self.move_time = int(8 * SCALE // (self.speed * self.app.game_speed) - 1)
        self.frightened = False

    def frightened_action(self):
        if not self.frightened:
            self.frightened = True
            self.mode = 'frightened'
            self.move_dir = np.mod(self.move_dir + 180, 360)
            self.move_timer = self.move_time - self.move_timer
            self.animation_pause_timer = int(self.frightened_timer // 2)
            self.animation_frame = 0
            self.animate('frightened')
        self.frightened_timer -= 1
        if self.frightened_timer < 0:
            self.frightened = False
            self.mode = 'chase'

    def return_start(self):
        self.mode = 'return'
        self.snap_to_grid()
        self.move_timer = int(8 * SCALE // (self.speed * self.app.game_speed) - 1)
        self.snap_to_grid()
        self.choose_target()
        self.choose_direction()
        self.move = True


    def load_graphics(self):
        gh_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'red_ghost.png'))
        if self.color == 'red':
            gh_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'red_ghost.png'))
        if self.color == 'pink':
            gh_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'pink_ghost.png'))
        if self.color == 'blue':
            gh_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'blue_ghost.png'))
        if self.color == 'orange':
            gh_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'orange_ghost.png'))
        gh_right0 = (0, 0, 16, 16)
        gh_right1 = (16, 0, 16, 16)
        gh_right_coords = [gh_right0, gh_right1]
        gh_up0 = (64, 0, 16, 16)
        gh_up1 = (80, 0, 16, 16)
        gh_up_coords = [gh_up0, gh_up1]
        gh_left0 = (32, 0, 16, 16)
        gh_left1 = (48, 0, 16, 16)
        gh_left_coords = [gh_left0, gh_left1]
        gh_down0 = (96, 0, 16, 16)
        gh_down1 = (112, 0, 16, 16)
        gh_down_coords = [gh_down0, gh_down1]

        gh_frightened_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'frightened_ghost.png'))
        gh_frightened_coords = [(0, 0, 16, 16), (16, 0, 16, 16), (32, 0, 16, 16), (48, 0, 16, 16)]

        gh_return_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'return_ghost.png'))
        gh_return_right_coords = [(0, 0, 16,16)]
        gh_return_left_coords = [(16, 0, 16, 16)]
        gh_return_up_coords = [(32, 0, 16, 16)]
        gh_return_down_coords = [(48, 0, 16, 16)]

        points_spritesheet = spritesheet.Spritesheet(path.join(self.app.graphics_folder, 'bonus_points_sprite.png'))
        points_coords = [(0, 0, 16, 16), (16, 0, 16, 16), (32, 0, 16, 16), (48, 0, 16, 16)]

        self.gh_right_animation = gh_spritesheet.image_list(gh_right_coords, colorkey=BLACK)
        self.gh_up_animation = gh_spritesheet.image_list(gh_up_coords, colorkey=BLACK)
        self.gh_left_animation = gh_spritesheet.image_list(gh_left_coords, colorkey=BLACK)
        self.gh_down_animation = gh_spritesheet.image_list(gh_down_coords, colorkey=BLACK)
        self.gh_frightened_animation = gh_frightened_spritesheet.image_list(gh_frightened_coords, colorkey=BLACK)
        self.gh_return_right_animation = gh_return_spritesheet.image_list(gh_return_right_coords, colorkey=BLACK)
        self.gh_return_up_animation = gh_return_spritesheet.image_list(gh_return_up_coords, colorkey=BLACK)
        self.gh_return_left_animation = gh_return_spritesheet.image_list(gh_return_left_coords, colorkey=BLACK)
        self.gh_return_down_animation = gh_return_spritesheet.image_list(gh_return_down_coords, colorkey=BLACK)
        self.points_animation = points_spritesheet.image_list(points_coords, colorkey=BLACK)

    def animate(self, animation):
        if animation == "move":
            if self.move_dir == 0:
                self.image = self.gh_right_animation[self.animation_frame]
            elif self.move_dir == 90:
                self.image = self.gh_up_animation[self.animation_frame]
            elif self.move_dir == 180:
                self.image = self.gh_left_animation[self.animation_frame]
            elif self.move_dir == 270:
                self.image = self.gh_down_animation[self.animation_frame]
        elif animation == 'frightened':
            self.image = self.gh_frightened_animation[self.animation_frame]
        elif animation == 'return':
            if self.move_dir == 0:
                self.image = self.gh_return_right_animation[self.animation_frame]
            elif self.move_dir == 90:
                self.image = self.gh_return_up_animation[self.animation_frame]
            elif self.move_dir == 180:
                self.image = self.gh_return_left_animation[self.animation_frame]
            elif self.move_dir == 270:
                self.image = self.gh_return_down_animation[self.animation_frame]
        elif animation == 'eaten':
            frame = 0
            if self.points == 200:
                frame = 0
            elif self.points == 400:
                frame = 1
            elif self.points == 800:
                frame = 2
            elif self.points == 1600:
                frame = 3
            self.image = self.points_animation[frame]
        self.image = pygame.transform.scale(self.image, (16 * SCALE, 16 * SCALE))