import pygame as pg
import numpy as np

class Player:
    def __init__(self):
        self.health = 30
        self.max_health = 30
        self.hit_sound = pg.mixer.Sound('assets/music/HP loss.mp3')
        self.health_bar_sprite = pg.image.load('assets/textures/ui/Steampunk_healthbar_anim.png').convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.scaled_width = int(self.frame_width * 3)
        self.scaled_height = int(self.frame_height * 3)
        self.total_frames = 7
        self.health_bar_frames = []
        for i in range(self.total_frames):
            x = i * self.frame_width
            y = 0
            frame = self.health_bar_sprite.subsurface(pg.Rect(x, y, self.frame_width, self.frame_height))
            scaled_frame = pg.transform.scale(frame, (self.scaled_width, self.scaled_height))
            self.health_bar_frames.append(scaled_frame)

    def take_damage(self, amount):
        print(f"[DMG] Taking {amount} damage")
        self.health = max(0, self.health - amount)
        self.hit_sound.play()

    def is_dead(self):
        return self.health <= 0

    def draw_health(self, screen):
        health_index = 6 - (self.health // 5)
        if health_index >= 30 or health_index <= 0:
            health_index = 0
        if self.health <= 4 and self.health >= 1:
            health_index = 5
        x = screen.get_width() - self.scaled_width - 10
        y = 10
        screen.blit(self.health_bar_frames[health_index], (x, y))
        
    def update(self):
        pass
