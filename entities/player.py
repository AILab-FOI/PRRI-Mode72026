import pygame as pg
import numpy as np
import time

from settings import SPEED, MAP_BOUND

class Player:
    def __init__(self):
        self.world_pos = np.array([0.0, 0.0], dtype=np.float32)
        self.velocity = np.zeros(2, dtype=np.float32)
        self.angle = 0.0
        self.base_speed = SPEED * 0.7
        self.acceleration = 0.22
        self.drag = 0.82
        self.turn_speed = SPEED * 0.6
        self.speed_multiplier = 1.0
        self.speed_timer = 0
        self.health = 30
        self.max_health = 30
        self.hit_radius = 0.32
        self.graze_radius = 0.72
        self.invulnerability_duration = 0.75
        self.invulnerable_until = 0
        self.hit_sound = pg.mixer.Sound('assets/music/HP loss.mp3')

    @property
    def pos(self):
        return self.world_pos

    @pos.setter
    def pos(self, value):
        self.world_pos = np.array(value, dtype=np.float32)

    def take_damage(self, amount):
        now = time.time()
        if now < self.invulnerable_until or self.health <= 0:
            return False

        print(f"[DMG] Taking {amount} damage")
        self.health = max(0, self.health - amount)
        self.invulnerable_until = now + self.invulnerability_duration
        self.hit_sound.play()
        return True

    def is_dead(self):
        return self.health <= 0

    def is_invulnerable(self):
        return time.time() < self.invulnerable_until

    def movement(self, keys):
        turn_input = 0
        if keys[pg.K_a]:
            turn_input -= 1
        if keys[pg.K_d]:
            turn_input += 1
        self.angle = (self.angle + turn_input * self.turn_speed) % (2 * np.pi)

        move_input = 0.0
        if keys[pg.K_w]:
            move_input += 1.0
        if keys[pg.K_s]:
            move_input -= 1.0

        if move_input != 0.0:
            forward = np.array([np.sin(self.angle), np.cos(self.angle)], dtype=np.float32)
            desired_velocity = forward * move_input * self.base_speed * self.speed_multiplier
            self.velocity += (desired_velocity - self.velocity) * self.acceleration
        else:
            self.velocity *= self.drag

        self.world_pos += self.velocity
        self.world_pos = np.clip(self.world_pos, -MAP_BOUND, MAP_BOUND)

    def update(self, keys):
        self.movement(keys)
        if self.speed_multiplier != 1.0 and time.time() > self.speed_timer:
            self.speed_multiplier = 1.0
            print("[SPEED] Boost expired")

    def apply_speed_boost(self, multiplier, duration):
        self.speed_multiplier = multiplier
        self.speed_timer = time.time() + duration
        print(f"[SPEED] Boost applied: x{multiplier} fo r {duration}s")
