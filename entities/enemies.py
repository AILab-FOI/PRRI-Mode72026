import pygame as pg
import numpy as np
import random
from core.projectile import Projectile

class Enemy:
    def __init__(self, pos, speed=0.03, min_distance=2.0, damage=1):
        self.pos = np.array(pos, dtype=np.float32)
        self.speed = speed
        self.alive = True
        self.min_distance = min_distance
        self.texture = pg.image.load('assets/textures/enemies/zeppelin_obican.png').convert_alpha()
        self.bullets = []
        self.hit_timer = 0
        self.hp = 100
        self.max_hp = 100
        self.shoot_delay = 200
        self.shoot_timer = random.randint(0, self.shoot_delay)
        self.damage = damage
        self.circle_direction = random.choice([-1, 1])
        self.hit_radius = 0.55
        self.contact_radius = 0.42
        self.bullet_hit_radius = 0.18

    def update(self, player_pos):
        direction = player_pos - self.pos
        distance = np.linalg.norm(direction)

        if distance > 0:
            if distance < self.min_distance:
                direction /= distance
                perp_direction = np.array([-direction[1], direction[0]]) * self.circle_direction
                self.pos += perp_direction * self.speed
            else:
                direction /= distance
                self.pos += direction * self.speed

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot(player_pos)
            self.shoot_timer = self.shoot_delay

        self.hit_timer = max(0, self.hit_timer - 1)

        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.active]

    def shoot(self, player_pos):
        direction = player_pos - self.pos
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction = direction / norm
        bullet = Projectile(self.pos.copy(), direction, speed=0.08, hit_radius=self.bullet_hit_radius)
        self.bullets.append(bullet)

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)

        if scale > 0:
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale // 2, int(screen_y) - scale // 2))

            hp_bar_width = scale
            hp_bar_rect = pg.Rect(
                int(screen_x - hp_bar_width / 2),
                int(screen_y - scale // 2 - 10),
                int(hp_bar_width),
                5,
            )
            pg.draw.rect(screen, (100, 0, 0), hp_bar_rect)
            hp_ratio = self.hp / self.max_hp
            green_bar_width = int(hp_bar_rect.width * hp_ratio)
            green_rect = pg.Rect(hp_bar_rect.x, hp_bar_rect.y, green_bar_width, hp_bar_rect.height)
            pg.draw.rect(screen, (0, 255, 0), green_rect)

        for bullet in self.bullets:
            bullet.draw(screen, mode7)

    def check_collision(self, projectile):
        if np.linalg.norm(self.pos - projectile.pos) < self.hit_radius + projectile.hit_radius:
            self.hit_timer = 10
            self.hp -= 50
            if self.hp <= 0:
                self.alive = False
            return True
        return False

class TankEnemy(Enemy):
    def __init__(self, pos):
        super().__init__(pos, speed=0.02, min_distance=1.5, damage=2)
        self.texture = pg.image.load('assets/textures/enemies/zeppelin_tank.png').convert_alpha()
        self.hp = 400
        self.max_hp = 400
        self.shoot_delay = 300
        self.hit_radius = 0.72
        self.contact_radius = 0.5
        self.bullet_hit_radius = 0.22

    def shoot(self, player_pos):
        direction = player_pos - self.pos
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction = direction / norm
        bullet = Projectile(self.pos.copy(), direction, speed=0.16, hit_radius=self.bullet_hit_radius)
        self.bullets.append(bullet)

class FastEnemy(Enemy):
    def __init__(self, pos):
        super().__init__(pos, speed=0.04, min_distance=0.5, damage=4)
        self.texture = pg.image.load('assets/textures/enemies/zeppelin_tnt.png').convert_alpha()
        self.hp = 1  # Dies on contact
        self.max_hp = 1
        self.shoot_delay = None  # Not used
        self.bullets = []  # No bullets
        self.hit_radius = 0.4
        self.contact_radius = 0.34

    def update(self, player_pos):
        direction = player_pos - self.pos
        distance = np.linalg.norm(direction)

        if distance > 0:
            direction /= distance
            self.pos += direction * self.speed

    def shoot(self, player_pos):
        pass  # Disable shooting
