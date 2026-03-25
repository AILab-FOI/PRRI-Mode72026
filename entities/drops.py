import pygame as pg
import numpy as np
import random
from settings import WeaponType

class Drop:
    def __init__(self, pos):
        self.pos = np.array(pos, dtype=np.float32)
        self.collected = False
        self.texture = pg.Surface((20, 20))  # Placeholder, can replace with textures
        self.pickup_radius = 0.42
        self.magnet_radius = 1.8
        self.magnet_speed = 0.12
        self.bob_phase = random.uniform(0, np.pi * 2)

    def update(self, player_pos):
        distance = np.linalg.norm(self.pos - player_pos)

        if distance <= self.pickup_radius:
            self.collected = self.on_pickup()
            return

        if 0 < distance < self.magnet_radius:
            direction = (player_pos - self.pos) / distance
            self.pos += direction * min(self.magnet_speed, distance)

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            bob_offset = np.sin(pg.time.get_ticks() * 0.006 + self.bob_phase) * max(3, scale * 0.08)
            pulse = 1 + 0.06 * np.sin(pg.time.get_ticks() * 0.008 + self.bob_phase)
            display_scale = max(8, int(scale * pulse))
            scaled_texture = pg.transform.scale(self.texture, (display_scale, display_scale))
            screen.blit(
                scaled_texture,
                (int(screen_x) - display_scale // 2, int(screen_y - bob_offset) - display_scale // 2),
            )

    def on_pickup(self):
        return False


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
            self.app.show_status_message("Hull repaired +5", duration=1.6)
            return True
        return False


class ShotgunDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("assets/textures/powerups/shotgun_steampunk.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("[DROP] Picked up shotgun drop!")
        self.app.apply_powerup(WeaponType.SHOTGUN)
        return True




class MinigunDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("assets/textures/powerups/minigun_steampunk.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("[DROP] Picked up minigun drop!")
        self.app.apply_powerup(WeaponType.MINIGUN)
        return True

class SpeedUpDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("assets/textures/powerups/Speed_powerup.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("[DROP] Picked up speed power-up!")
        self.app.apply_speed_boost(1.6, duration=5.4)
        return True
