import pygame as pg
import numpy as np
from settings import AIR_LANE_REFERENCE_HEIGHT, PROJECTILE_HEIGHT_HIT_RADIUS


class Projectile:
    def __init__(
        self,
        player_pos,
        player_angle,
        speed=0.5,
        max_distance=20,
        offset_distance=2.0,
        hit_radius=0.18,
        height=AIR_LANE_REFERENCE_HEIGHT,
        vertical_hit_radius=PROJECTILE_HEIGHT_HIT_RADIUS,
    ):
        if np.isscalar(player_angle):
            player_angle = np.radians(player_angle) if player_angle > np.pi * 2 else player_angle

            direction_x = np.cos(player_angle - np.pi / 2)
            direction_y = -np.sin(player_angle - np.pi / 2)
            self.direction = np.array([direction_x, direction_y], dtype=np.float32)

            rotated_offset_x = offset_distance * direction_x
            rotated_offset_y = offset_distance * direction_y

            self.pos = np.array(player_pos, dtype=np.float32) + np.array([rotated_offset_x, rotated_offset_y])
            self.speed = speed
            self.max_distance = max_distance
            self.start_pos = np.array(self.pos, dtype=np.float32)
            self.active = True
            self.color = (0, 0, 0)
            self.radius_divisor = 15
            self.hit_radius = hit_radius
        else:
            self.pos = np.array(player_pos, dtype=np.float32)
            self.direction = np.array(player_angle, dtype=np.float32)
            self.speed = speed
            self.start_pos = np.array(player_pos, dtype=np.float32)
            self.max_distance = 15 if max_distance == 20 and offset_distance == 2.0 else max_distance
            self.active = True
            self.color = (255, 0, 0)
            self.radius_divisor = 20
            self.hit_radius = hit_radius
        self.height = float(height)
        self.vertical_hit_radius = vertical_hit_radius

    def update(self):
        self.pos += self.direction * self.speed
        if np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos, world_height=self.height)
        if scale > 0:
            radius = max(2, scale // self.radius_divisor)
            pg.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), radius)


class RocketProjectile(Projectile):
    def __init__(self, player_pos, player_angle, height=AIR_LANE_REFERENCE_HEIGHT):
        super().__init__(
            player_pos,
            player_angle,
            speed=0.22,
            max_distance=18,
            offset_distance=0.0,
            hit_radius=0.28,
            height=height,
        )
        self.color = (255, 120, 20)
        self.radius_divisor = 7

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos, world_height=self.height)
        if scale > 0:
            radius = max(4, scale // self.radius_divisor)
            pg.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), radius)
            pg.draw.circle(screen, (255, 220, 60), (int(screen_x), int(screen_y)), max(2, radius // 2))


class AoEProjectile(Projectile):
    """Boss AoE shot — deals area damage (checked by radius) on impact."""
    AOE_RADIUS = 1.8

    def __init__(self, pos, direction, speed, hit_radius, height, vertical_hit_radius):
        super().__init__(
            pos,
            direction,
            speed=speed,
            hit_radius=hit_radius,
            height=height,
            vertical_hit_radius=vertical_hit_radius,
        )
        self.color = (255, 60, 200)
        self.radius_divisor = 8
        self.aoe_radius = self.AOE_RADIUS

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos, world_height=self.height)
        if scale > 0:
            radius = max(5, scale // self.radius_divisor)
            pg.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), radius)
            pg.draw.circle(screen, (255, 200, 240), (int(screen_x), int(screen_y)), max(2, radius // 2))
