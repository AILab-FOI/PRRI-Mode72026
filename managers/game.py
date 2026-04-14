import pygame as pg
import numpy as np
import random
from core.projectile import Projectile
from entities.drops import HealthDrop, ShotgunDrop, MinigunDrop, SpeedUpDrop
from entities.enemies import FastEnemy
from managers.level import LevelManager
from entities.obstacles import Obstacle


class Game:
    def __init__(self, mode7, player, app):
        self.mode7 = mode7
        self.player = player
        self.app = app
        self.projectiles = []
        self.enemies = []
        self.drops = []
        self.obstacles = []
        self.wave = 1
        self.level_manager = LevelManager(self.mode7, self.enemies, self.obstacles)
        self.wave_sound = pg.mixer.Sound("assets/music/Level up.mp3")
        self.explosion_sound = pg.mixer.Sound("assets/music/eksplozija.mp3")
        self.level_manager.spawn_wave(self.wave)

    def spawn_wave(self, wave_num):
        # TODO: replace LevelManager.spawn_wave() with 4 defined levels per GDD when level design is finalized
        self.level_manager.spawn_wave(wave_num)

    def update(self, player_pos):
        for proj in self.projectiles:
            proj.update()

        for proj in self.projectiles:
            for enemy in self.enemies:
                if enemy.check_collision(proj):
                    proj.active = False
                    if not enemy.alive:
                        self.app.audio.play_enemy_dead()
                        self.app.enemies_killed += 1
                        if random.random() < 0.3:
                            drop_type = random.choice([HealthDrop, ShotgunDrop, MinigunDrop, SpeedUpDrop])
                            pos = enemy.pos.copy()
                            if drop_type == HealthDrop:
                                self.drops.append(HealthDrop(pos, self.player, self.app))
                            else:
                                self.drops.append(drop_type(pos, self.app))

        self.projectiles = [p for p in self.projectiles if p.active]

        for enemy in self.enemies:
            enemy.update(player_pos)
            for bullet in enemy.bullets:
                if np.linalg.norm(np.array(player_pos) - bullet.pos) < self.player.hit_radius + bullet.hit_radius:
                    self.player.take_damage(enemy.damage)
                    bullet.active = False
            if isinstance(enemy, FastEnemy):
                if np.linalg.norm(np.array(player_pos) - enemy.pos) < self.player.hit_radius + enemy.contact_radius:
                    self.player.take_damage(enemy.damage)
                    self.explosion_sound.play()
                    enemy.alive = False

        self.enemies[:] = [e for e in self.enemies if e.alive]

        for drop in self.drops:
            drop.update(player_pos)

        self.drops = [d for d in self.drops if not d.collected]

        for obstacle in self.obstacles:
            obstacle.update(self.player)
        self.obstacles[:] = [o for o in self.obstacles if o.alive]

        if len(self.enemies) == 0:
            self.wave += 1
            self.level_manager.spawn_wave(self.wave)

    def draw(self, screen):
        for proj in self.projectiles:
            proj.draw(screen, self.mode7)
        for enemy in self.enemies:
            enemy.draw(screen, self.mode7)
        for drop in self.drops:
            drop.draw(screen, self.mode7)
        for obj in self.obstacles:
            obj.draw(screen,self.mode7)


    def shoot_revolver(self, angle):
        pos = self.get_player_projectile_spawn_pos()
        spread = random.uniform(-0.025, 0.025)
        self.projectiles.append(Projectile(pos, angle + spread, speed=0.62, offset_distance=0.0))

    def shoot_shotgun(self, angle):
        pos = self.get_player_projectile_spawn_pos()
        for spread in [-0.24, 0.0, 0.24]:
            pellet_spread = spread + random.uniform(-0.03, 0.03)
            pellet_speed = 0.48 + random.uniform(-0.03, 0.04)
            self.projectiles.append(Projectile(pos, angle + pellet_spread, speed=pellet_speed, offset_distance=0.0))

    def shoot_minigun(self, angle):
        pos = self.get_player_projectile_spawn_pos()
        spread = random.uniform(-0.06, 0.06)
        self.projectiles.append(Projectile(pos, angle + spread, speed=0.54, offset_distance=0.0))

    def get_player_projectile_spawn_pos(self):
        # The zeppelin sprite is a fixed HUD overlay, so gameplay projectiles
        # must spawn from a stable world-space muzzle instead of camera altitude.
        forward_offset = self.get_projectile_offset(self.player.world_pos)
        forward = np.array([np.sin(self.player.angle), np.cos(self.player.angle)], dtype=np.float32)
        return self.player.world_pos + forward * forward_offset

    def get_projectile_offset(self, pos):
        return 0.5 if any(np.linalg.norm(enemy.pos - pos) < 2.0 for enemy in self.enemies) else 2.0
