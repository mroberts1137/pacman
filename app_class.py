import pygame, sys
import os
from array import *
import numpy as np
from settings import *
from player import *
from ghost import *
from pellet import *
from points import *

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
vec = pygame.math.Vector2


class App:
    def __init__(self):
        self.game_folder = path.dirname(__file__)
        self.graphics_folder = path.join(self.game_folder, "Graphics")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.game_speed = 1
        self.draw_grid_flag = False
        self.draw_map_flag = False
        self.draw_entities_flag = False
        self.draw_targets_flag = False

        self.game_pause = False
        self.player_alive = True
        self.level_start = False
        self.level_end = False
        self.pause_timer = 0

        self.score = 0
        self.bonus_score = 200
        self.level = 1

        self.load_graphics()

        # map is 28 x 31
        self.map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                               [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                               [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                               [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                               [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                               [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                               [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                               [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 2, 2, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                               [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                               [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                               [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
                               [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                               [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                               [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                               [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
                               [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                               [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                               [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

        self.entity_map = np.zeros((31,28), dtype=int)

        self.pellet_map_initial = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0],
                           [0, 5, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 5, 0],
                           [0, 6, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 6, 0],
                           [0, 5, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 5, 0],
                           [0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0],
                           [0, 5, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 5, 0],
                           [0, 5, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 5, 0],
                           [0, 5, 5, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 5, 5, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0],
                           [0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0],
                           [0, 5, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 5, 0],
                           [0, 5, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 5, 0],
                           [0, 6, 5, 5, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 5, 5, 6, 0],
                           [0, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, 0],
                           [0, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, 0],
                           [0, 5, 5, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 0, 0, 5, 5, 5, 5, 5, 5, 0],
                           [0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0],
                           [0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0],
                           [0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.pellet_map = np.zeros((31,28), dtype=int)

        self.all_sprites = pygame.sprite.Group()
        self.ghosts = pygame.sprite.Group()
        self.pellets = pygame.sprite.Group()

        self.initiate_pellets()

        self.player = Player(self, PLAYER_START_GRID_POS)
        self.blinky = Ghost(self, BLINKY_START_GRID_POS, 'red', 'blinky')
        self.pinky = Ghost(self, PINKY_START_GRID_POS, 'pink', 'pinky')
        self.inky = Ghost(self, INKY_START_GRID_POS, 'blue', 'inky')
        self.clyde = Ghost(self, CLYDE_START_GRID_POS, 'orange', 'clyde')



        self.all_sprites.add(self.player)
        self.all_sprites.add(self.blinky)
        self.all_sprites.add(self.pinky)
        self.all_sprites.add(self.inky)
        self.all_sprites.add(self.clyde)

        self.ghosts.add(self.blinky)
        self.ghosts.add(self.pinky)
        self.ghosts.add(self.inky)
        self.ghosts.add(self.clyde)



    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

############################################ HELPER FUNCTIONS ########################################

    def clear_entity_map(self):
        for j in range(31):
            for i in range(28):
                self.entity_map[j][i] = 0

    def game_restart(self):
        self.state = 'start'
        self.game_pause = False
        self.initiate_pellets()

    def level_restart(self):
        self.game_pause = True
        self.level_start = True
        self.level_end = False
        self.player_alive = True
        self.pause_timer = 120
        self.player.initiate(PLAYER_START_GRID_POS)
        self.blinky.initiate(BLINKY_START_GRID_POS)
        self.pinky.initiate(PINKY_START_GRID_POS)
        self.inky.initiate(INKY_START_GRID_POS)
        self.clyde.initiate(CLYDE_START_GRID_POS)

    def pause_delay(self):
        self.pause_timer -= 1
        if self.pause_timer <= 0:
            self.game_pause = False
            for g in self.ghosts:
                if g.mode == 'eaten':
                    g.return_start()
            if self.level_start:
                self.level_start = False
            if self.level_end:
                self.level_end = False
                self.level += 1
                self.level_restart()
                self.initiate_pellets()

    def initiate_pellets(self):
        for p in self.pellets:
            p.kill()
        for j in range(31):
            for i in range(28):
                if self.pellet_map_initial[j][i] == 5:
                    self.pellet_map[j][i] = 5
                    pellet = Pellet(self, vec(i,j), False)
                    self.all_sprites.add(pellet)
                    self.pellets.add(pellet)
                elif self.pellet_map_initial[j][i] == 6:
                    self.pellet_map[j][i] = 6
                    pellet = Pellet(self, vec(i,j), True)
                    self.all_sprites.add(pellet)
                    self.pellets.add(pellet)


############################################ INTRO FUNCTIONS ########################################

    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                self.level_restart()
                self.state = 'playing'

    def start_update(self):
        pass

    def start_draw(self):
        self.screen.fill(BLACK)
        self.draw_text(self.screen, (WIDTH//2, HEIGHT//2), TEXT_SIZE, WHITE, FONT, 'PRESS SPACE TO START', centered=True)
        pygame.display.update()


############################################ PLAYING FUNCTIONS ########################################

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def playing_update(self):
        self.all_sprites.update()
        self.clear_entity_map()
        pac = vec(int(np.mod(self.player.grid_pos.x,28)), int(np.mod(self.player.grid_pos.y,31)))
        self.entity_map[int(pac.y)][int(pac.x)] = 3
        for g in self.ghosts:
            ghost = vec(int(np.mod(g.grid_pos.x, 28)), int(np.mod(g.grid_pos.y, 31)))
            self.entity_map[int(ghost.y)][int(ghost.x)] = 4
            if self.player.alive:
                if pac == ghost or pac == ghost + vec(1,0) or pac == ghost + vec(0,1) or pac == ghost + vec(-1,0) or pac == ghost + vec(0,-1):
                    if g.mode == 'chase':
                        self.player.die()
                    elif g.mode == 'frightened':
                        g.mode = 'eaten'
                        self.pause_timer = 60
                        g.frightened = False
                        self.score += self.bonus_score
                        g.points = self.bonus_score
                        self.bonus_score *= 2

        for p in pygame.sprite.spritecollide(self.player, self.pellets, True):
            self.score += 10
            self.player.move_pause_timer = 1
            if p.superpellet:
                self.player.move_pause_timer = 3
                for g in self.ghosts:
                    if not g.mode == 'return':
                        g.frightened_timer = g.frightened_time // self.game_speed
                        g.animation_pause_timer = int(g.frightened_timer // 2)
                        g.animation_frame = 0
                        g.animate('frightened')
                        g.frightened_action()
                        self.bonus_score = 200
        if len(self.pellets) == 0 and not self.level_end:
            self.pause_timer = 180
            self.level_end = True

        if self.pause_timer > 0:
            self.game_pause = True
            self.pause_delay()


    def playing_draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.bkg, (0, 20*SCALE))
        self.draw_text(self.screen, (2, 16), TEXT_SIZE, WHITE, FONT, 'SCORE:' + str(self.score))
        self.draw_text(self.screen, (200, 6), TEXT_SIZE, WHITE, FONT, 'Alive: ' + str(self.player_alive) + ', Pause:' + str(self.game_pause) + ', ' + str(self.pause_timer) + 'Move Timer: ' + str(self.player.move_timer) + 'Move: ' + str(self.player.move_pause_timer))
        self.draw_text(self.screen, (100, 6), TEXT_SIZE, WHITE, FONT, str(self.player.grid_pos))
        self.draw_text(self.screen, (100, 26), TEXT_SIZE, WHITE, FONT, 'mode: ' + str(self.blinky.mode) + ', frightened: ' + str(self.blinky.frightened) + ', frightened_timer: ' + str(self.blinky.frightened_timer))
        if self.draw_grid_flag:
            self.draw_grid()
        if self.draw_map_flag:
            self.draw_map()
        self.all_sprites.draw(self.screen)
        if self.draw_entities_flag:
            self.draw_entities()
        if self.draw_targets_flag:
            self.draw_targets()
        pygame.display.update()


############################################ DRAWING FUNCTIONS ########################################

    def draw_text(self, screen, pos, size, color, font_name, text1, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(text1, False, color)
        text_size = text.get_size()
        pos = list(pos)
        if centered:
            pos[0] = pos[0] - text_size[0]//2
            pos[1] = pos[1] - text_size[1] // 2
        screen.blit(text, pos)

    def load_graphics(self):
        self.bkg = pygame.image.load(path.join(self.graphics_folder, 'maze.png')).convert()
        self.bkg = pygame.transform.scale(self.bkg, (BKG_WIDTH, BKG_HEIGHT))

    def draw_grid(self):
        for x in range(30):
            pygame.draw.line(self.screen, GRAY, (TOP_LEFT_X + x*TILE_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + x*TILE_SIZE, TOP_LEFT_Y + 31*TILE_SIZE))
        for y in range(32):
            pygame.draw.line(self.screen, GRAY, (TOP_LEFT_X, TOP_LEFT_Y + y*TILE_SIZE), (TOP_LEFT_X + 28*TILE_SIZE, TOP_LEFT_Y + y*TILE_SIZE))

    def draw_map(self):
        #0 = free
        #1 = wall
        #2 = gate
        #3 = pacman
        #4 = ghost
        #5 = pellet
        #6 = super pellet
        for j in range(31):
            for i in range(28):
                if self.map[j][i] == 1:
                    pygame.draw.rect(self.screen, BLUE, (TOP_LEFT_X + i*TILE_SIZE, TOP_LEFT_Y + j*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def draw_entities(self):
        for j in range(31):
            for i in range(28):
                if self.entity_map[j][i] == 3:
                    pygame.draw.rect(self.screen, YELLOW, (TOP_LEFT_X + i*TILE_SIZE, TOP_LEFT_Y + j*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                if self.entity_map[j][i] == 4:
                    pygame.draw.rect(self.screen, RED, (TOP_LEFT_X + i*TILE_SIZE, TOP_LEFT_Y + j*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def draw_targets(self):
        for g in self.ghosts:
            pygame.draw.line(self.screen, g.col, (ORIGIN.x + (g.target.x) * TILE_SIZE, ORIGIN.y + (g.target.y) * TILE_SIZE), (ORIGIN.x + (g.target.x + 1) * TILE_SIZE, ORIGIN.y + (g.target.y + 1) * TILE_SIZE), 3)
            pygame.draw.line(self.screen, g.col, (ORIGIN.x + (g.target.x) * TILE_SIZE, ORIGIN.y + (g.target.y + 1) * TILE_SIZE), (ORIGIN.x + (g.target.x + 1) * TILE_SIZE, ORIGIN.y + (g.target.y) * TILE_SIZE), 3)
            pygame.draw.rect(self.screen, g.col, (ORIGIN.x + (g.target.x) * TILE_SIZE, ORIGIN.y + (g.target.y) * TILE_SIZE+1, TILE_SIZE+1, TILE_SIZE), 3)