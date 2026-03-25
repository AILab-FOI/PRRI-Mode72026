import pygame as pg
import numpy as np

class Player:
    def __init__(self):
        self.health = 30
        self.max_health = 30
        self.hit_sound = pg.mixer.Sound('assets/music/HP loss.mp3')

    def take_damage(self, amount):
        print(f"[DMG] Taking {amount} damage")
        self.health = max(0, self.health - amount)
        self.hit_sound.play()

    def is_dead(self):
        return self.health <= 0
        
    def update(self):
        pass
