import pygame

class Spritesheet():
    def __init__(self, file):
        try:
            self.sheet = pygame.image.load(file).convert()
        except:
            pygame.error
            print('Unable to load file ', file)
            raise SystemExit

    def image_at(self, rectangle, colorkey=None):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def image_list(self, rects, colorkey=None):
        return [self.image_at(rect, colorkey) for rect in rects]