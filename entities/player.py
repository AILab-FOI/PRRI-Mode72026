import pygame as pg
import numpy as np
import time

from settings import SPEED

class Player:
    def __init__(self):
        self.pos = np.array([0.0, 0.0])
        self.angle = 0.0
        self.speed_multiplier = 1.0
        self.speed_timer = 0
        self.health = 30
        self.max_health = 30
        self.hit_sound = pg.mixer.Sound('assets/music/HP loss.mp3')

    def take_damage(self, amount):
        print(f"[DMG] Taking {amount} damage")
        self.health = max(0, self.health - amount)
        self.hit_sound.play()

    def is_dead(self):
        return self.health <= 0

    def movement(self, keys):
        sin_a = np.sin(self.angle)
        cos_a = np.cos(self.angle)
        dx, dy = 0, 0
        player_speed = SPEED * 0.7 * self.speed_multiplier
        speed_sin = player_speed * sin_a
        speed_cos = player_speed * cos_a

        self.angle %= 2 * np.pi

        if keys[pg.K_w]:
            dy += speed_cos
            dx += speed_sin
        if keys[pg.K_s]:
            dy += -speed_cos
            dx += -speed_sin
        if keys[pg.K_a]:
            dy += speed_sin
            dx += -speed_cos
        if keys[pg.K_d]:
            dy += -speed_sin
            dx += speed_cos
        self.pos[0] += dx
        self.pos[1] += dy

        if keys[pg.K_LEFT]:
            self.angle -= SPEED
        if keys[pg.K_RIGHT]:
            self.angle += SPEED

    def update(self, keys):
        self.movement(keys)
        if self.speed_multiplier != 1.0 and time.time() > self.speed_timer:
            self.speed_multiplier = 1.0
            print("[SPEED] Boost expired")

    def apply_speed_boost(self, multiplier, duration):
        self.speed_multiplier = multiplier
        self.speed_timer = time.time() + duration
        print(f"[SPEED] Boost applied: x{multiplier} fo r {duration}s")
