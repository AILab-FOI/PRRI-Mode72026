import pygame as pg
import numpy as np
import time 
from settings import WeaponType

class Drop:
    def __init__(self, pos):
        self.pos = np.array(pos, dtype=np.float32)
        self.collected = False
        self.texture = pg.Surface((20, 20))  # Placeholder, can replace with textures

    def update(self, player_pos):
        if np.linalg.norm(self.pos - player_pos) < 0.6:
            self.on_pickup()
            self.collected = True

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale // 2, int(screen_y) - scale // 2))

    def on_pickup(self):
        pass


class HealthDrop(Drop):
    def __init__(self, pos, player, app):
        super().__init__(pos)
        self.texture = pg.image.load("assets/textures/powerups/Heal_powerup.png").convert_alpha()
        self.player = player
        self.app = app  # dodano za zvuk

    def on_pickup(self):
        print("[DROP] Picked up health drop!")
        if self.player.health < self.player.max_health:
            self.player.health += 5
            self.player.health = max(0, min(self.player.health, self.player.max_health))
            self.app.audio.play_health()  # sviraj zvuk


class ShotgunDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("assets/textures/powerups/shotgun_steampunk.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("[DROP] Picked up shotgun drop!")
        self.app.apply_powerup(WeaponType.SHOTGUN)
        self.app.weapon_timer = time.time() + 10




class MinigunDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("assets/textures/powerups/minigun_steampunk.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("[DROP] Picked up minigun drop!")
        self.app.apply_powerup(WeaponType.MINIGUN)
        self.app.weapon_timer = time.time() + 10

class SpeedUpDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("assets/textures/powerups/Speed_powerup.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("[DROP] Picked up speed power-up!")
        self.app.apply_speed_boost(1.6, duration=5.4)
