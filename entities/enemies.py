import pygame as pg
import numpy as np
import random
from pathlib import Path
from core.projectile import Projectile
from settings import (
    ENEMY_HEIGHT_ADJUST_SPEED,
    ENEMY_HEIGHT_HIT_RADIUS,
    ENEMY_HEIGHT_MATCH_RADIUS,
    ENEMY_MIN_HEIGHT,
    ENEMY_MATCH_MAX_HEIGHT,
    ENEMY_SPAWN_MAX_HEIGHT,
    PROJECTILE_HEIGHT_HIT_RADIUS,
)

class Enemy:
    DEFAULT_MIN_HEIGHT = ENEMY_MIN_HEIGHT
    DEFAULT_SPAWN_MAX_HEIGHT = ENEMY_SPAWN_MAX_HEIGHT

    def __init__(
        self,
        pos,
        speed=0.03,
        min_distance=2.0,
        damage=1,
        height=None,
        min_height=ENEMY_MIN_HEIGHT,
        spawn_max_height=ENEMY_SPAWN_MAX_HEIGHT,
        match_max_height=ENEMY_MATCH_MAX_HEIGHT,
        height_match_radius=ENEMY_HEIGHT_MATCH_RADIUS,
        height_adjust_speed=ENEMY_HEIGHT_ADJUST_SPEED,
    ):
        self.pos = np.array(pos, dtype=np.float32)
        self.speed = speed
        self.alive = True
        self.min_distance = min_distance
        self.texture = pg.image.load('assets/textures/enemies/zeppelin_puske_new.png').convert_alpha()
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
        self.min_height = min_height
        self.spawn_max_height = max(self.min_height, min(spawn_max_height, match_max_height))
        self.match_max_height = max(self.spawn_max_height, match_max_height)
        if height is None:
            raw = random.uniform(self.min_height, self.spawn_max_height)
            self.cruise_height = self._clamp_height(raw, upper_bound=self.spawn_max_height)
        else:
            self.cruise_height = self._clamp_height(float(height))
        self.height = self.cruise_height
        self.height_match_radius = max(height_match_radius, self.min_distance + 0.8)
        self.height_adjust_speed = height_adjust_speed
        self.height_hit_radius = ENEMY_HEIGHT_HIT_RADIUS
        self.bullet_height_hit_radius = PROJECTILE_HEIGHT_HIT_RADIUS

    def _clamp_height(self, height, upper_bound=None):
        if upper_bound is None:
            upper_bound = self.match_max_height
        return float(np.clip(height, self.min_height, upper_bound))

    def _update_height(self, player_height, distance):
        target_height = self.cruise_height
        in_match_radius = player_height is not None and distance <= self.height_match_radius
        if in_match_radius:
            target_height = self._clamp_height(player_height)

        height_delta = target_height - self.height
        if abs(height_delta) < 1e-4:
            self.height = target_height
            return

        if abs(height_delta) <= self.height_adjust_speed:
            self.height = target_height
            return

        self.height += float(np.clip(height_delta, -self.height_adjust_speed, self.height_adjust_speed))

    def update(self, player_pos, player_height=None):
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

        self._update_height(player_height, distance)

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
        bullet = Projectile(
            self.pos.copy(),
            direction,
            speed=0.08,
            hit_radius=self.bullet_hit_radius,
            height=self.height,
            vertical_hit_radius=self.bullet_height_hit_radius,
        )
        self.bullets.append(bullet)

    def _draw_height_indicator(self, screen, screen_x, screen_y, scale, player_height):
        threshold = self.height_hit_radius + PROJECTILE_HEIGHT_HIT_RADIUS
        diff = self.height - player_height
        cx = int(screen_x)
        cy = int(screen_y - scale // 2 - 22)
        r = max(5, scale // 10)

        if abs(diff) < threshold:
            pg.draw.circle(screen, (0, 210, 0), (cx, cy), r)
        elif diff > 0:
            pts = [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
            pg.draw.polygon(screen, (220, 40, 40), pts)
        else:
            pts = [(cx, cy + r), (cx - r, cy - r), (cx + r, cy - r)]
            pg.draw.polygon(screen, (60, 140, 255), pts)

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos, world_height=self.height)

        if scale > 0:
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale // 2, int(screen_y) - scale // 2))

            if self.hit_timer > 0:
                flash_width = max(2, scale // 12)
                pg.draw.circle(
                    screen,
                    (255, 226, 128),
                    (int(screen_x), int(screen_y)),
                    max(6, scale // 2 + 6),
                    flash_width,
                )

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

            self._draw_height_indicator(screen, screen_x, screen_y, scale, mode7.alt)

        for bullet in self.bullets:
            bullet.draw(screen, mode7)

    def check_collision(self, projectile):
        planar_hit = np.linalg.norm(self.pos - projectile.pos) < self.hit_radius + projectile.hit_radius
        proj_height = getattr(projectile, "height", self.match_max_height)
        vertical_hit = abs(self.height - proj_height) < (
            self.height_hit_radius + getattr(projectile, "vertical_hit_radius", projectile.hit_radius)
        )
        if planar_hit and vertical_hit:
            self.hit_timer = 10
            self.hp -= 50
            if self.hp <= 0:
                self.alive = False
            return True
        return False

class TankEnemy(Enemy):
    def __init__(self, pos, height=None):
        super().__init__(pos, speed=0.02, min_distance=1.5, damage=2, height=height)
        self.texture = pg.image.load('assets/textures/enemies/zeppelin_tank_new.png').convert_alpha()
        self.hp = 400
        self.max_hp = 400
        self.shoot_delay = 300
        self.hit_radius = 0.72
        self.contact_radius = 0.5
        self.bullet_hit_radius = 0.22
        self.height_adjust_speed *= 0.8
        self.height_hit_radius = 0.18

    def shoot(self, player_pos):
        direction = player_pos - self.pos
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction = direction / norm
        bullet = Projectile(
            self.pos.copy(),
            direction,
            speed=0.16,
            hit_radius=self.bullet_hit_radius,
            height=self.height,
            vertical_hit_radius=self.bullet_height_hit_radius,
        )
        self.bullets.append(bullet)

class FastEnemy(Enemy):
    def __init__(self, pos, height=None):
        super().__init__(pos, speed=0.04, min_distance=0.5, damage=4, height=height)
        self.texture = pg.image.load('assets/textures/enemies/zeppelin_new.png').convert_alpha()
        self.hp = 1  # Dies on contact
        self.max_hp = 1
        self.shoot_delay = None  # Not used
        self.bullets = []  # No bullets
        self.hit_radius = 0.4
        self.contact_radius = 0.34
        self.height_adjust_speed *= 1.5
        self.height_match_radius += 0.5
        self.height_hit_radius = 0.12

    def update(self, player_pos, player_height=None):
        direction = player_pos - self.pos
        distance = np.linalg.norm(direction)

        if distance > 0:
            direction /= distance
            self.pos += direction * self.speed

        self._update_height(player_height, distance)

    def shoot(self, _player_pos):
        pass  # Disable shooting


class BossEnemy(Enemy):
    def __init__(self, pos, height=None):
        super().__init__(pos, speed=0.015, min_distance=4.0, damage=3, height=height)
        boss_path = 'assets/textures/enemies/Final_boss.png'
        if Path(boss_path).exists():
            self.texture = pg.image.load(boss_path).convert_alpha()
        else:
            self.texture = pg.image.load('assets/textures/enemies/zeppelin_tank_new.png').convert_alpha()
        self.hp = 2000
        self.max_hp = 2000
        self.shoot_delay = 60
        self.hit_radius = 1.2
        self.contact_radius = 0.8
        self.bullet_hit_radius = 0.25
        self.height_adjust_speed *= 0.5
        self.height_hit_radius = 0.28

    def shoot(self, player_pos):
        direction = player_pos - self.pos
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction = direction / norm
        # Triple spread shot
        for spread_angle in (-0.3, 0.0, 0.3):
            c, s = np.cos(spread_angle), np.sin(spread_angle)
            d = np.array([
                direction[0] * c - direction[1] * s,
                direction[0] * s + direction[1] * c,
            ], dtype=np.float32)
            self.bullets.append(Projectile(
                self.pos.copy(), d,
                speed=0.12,
                hit_radius=self.bullet_hit_radius,
                height=self.height,
                vertical_hit_radius=self.bullet_height_hit_radius,
            ))
