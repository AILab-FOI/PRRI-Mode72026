import pygame as pg
import numpy as np
import time

from settings import SPEED

class Player:
    def __init__(self):
        self.pos = np.array([0.0, 0.0])
        self.velocity = np.zeros(2, dtype=np.float32)
        self.angle = 0.0
        self.base_speed = SPEED * 0.7
        self.acceleration = 0.22
        self.drag = 0.82
        self.turn_speed = SPEED * 0.9
        self.speed_multiplier = 1.0
        self.speed_timer = 0
        self.health = 30
        self.max_health = 30
        self.hit_radius = 0.32
        self.graze_radius = 0.72
        self.invulnerability_duration = 0.75
        self.invulnerable_until = 0
        self.hit_sound = pg.mixer.Sound('assets/music/HP loss.mp3')

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
        sin_a = np.sin(self.angle)
        cos_a = np.cos(self.angle)
        move_input = np.zeros(2, dtype=np.float32)

        self.angle %= 2 * np.pi

        if keys[pg.K_w]:
            move_input[1] += 1
        if keys[pg.K_s]:
            move_input[1] -= 1
        if keys[pg.K_a]:
            move_input[0] -= 1
        if keys[pg.K_d]:
            move_input[0] += 1

        input_length = np.linalg.norm(move_input)
        if input_length > 0:
            move_input /= input_length
            forward = np.array([sin_a, cos_a], dtype=np.float32)
            right = np.array([cos_a, -sin_a], dtype=np.float32)
            desired_velocity = (
                forward * move_input[1] + right * move_input[0]
            ) * self.base_speed * self.speed_multiplier
            self.velocity += (desired_velocity - self.velocity) * self.acceleration
        else:
            self.velocity *= self.drag

        self.pos += self.velocity

        if keys[pg.K_LEFT]:
            self.angle -= self.turn_speed
        if keys[pg.K_RIGHT]:
            self.angle += self.turn_speed

    def update(self, keys):
        self.movement(keys)
        if self.speed_multiplier != 1.0 and time.time() > self.speed_timer:
            self.speed_multiplier = 1.0
            print("[SPEED] Boost expired")

    def apply_speed_boost(self, multiplier, duration):
        self.speed_multiplier = multiplier
        self.speed_timer = time.time() + duration
        print(f"[SPEED] Boost applied: x{multiplier} fo r {duration}s")
