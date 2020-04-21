import sys, pygame, glob, os

from pygame.locals import *
import pygame.mixer
import utils

pygame.mixer.init()

class Sounds(object):
    def __init__(self):
        self.talking = []
        self.player_damage = []
        self.boops = []

        for filename in glob.glob(utils.fix_path(os.path.join('resource','sounds','*.wav'))):
            f = open(filename, 'rb')
            sound = pygame.mixer.Sound(file=f)
            sound.set_volume(0.6)
            name = os.path.basename(filename)
            name = os.path.splitext(name)[0]
            setattr(self,name,sound)
            if 'boop' in name:
                self.boops.append(sound)
