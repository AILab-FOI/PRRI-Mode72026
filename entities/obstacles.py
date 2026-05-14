import pygame as pg
import numpy as np

from settings import FOCAL_LEN, HALF_HEIGHT, HALF_WIDTH, HEIGHT, PROJECTILE_HEIGHT_HIT_RADIUS, WIDTH


class Obstacle:
    altitude = 0.0
    altitude_hit_radius = float('inf')  # old buildings always collide regardless of player altitude
    anchor_to_floor = False  # True → screen_y is derived from the mode7 floor projection so the sprite base sits on the ground
    anchor_to_ceiling = False  # True → screen_y is the ceiling row so the sprite top hugs the sky

    def __init__(self, pos, damage=5, collision_radius=0.8, texture_path=None, hp=50):
        self.pos = np.array(pos, dtype=np.float32)
        self.damage = damage
        self.collision_radius = collision_radius
        self.alive = True
        self.hp = hp
        self.max_hp = hp
        self.hit_timer = 0

        if texture_path:
            self.texture = pg.image.load(texture_path).convert_alpha()
        else:
            self.texture = self._make_placeholder()

    def _make_placeholder(self):
        surf = pg.Surface((64, 64), pg.SRCALPHA)
        pg.draw.rect(surf, (120, 80, 50), (8, 16, 48, 48))
        pg.draw.polygon(surf, (80, 50, 30), [(4, 16), (32, 0), (60, 16)])
        pg.draw.rect(surf, (200, 220, 255), (22, 28, 20, 16))
        pg.draw.rect(surf, (60, 40, 20), (24, 46, 16, 18))
        return surf

    def update(self, player, player_alt=None):
        if not self.alive:
            return

        self.hit_timer = max(0, self.hit_timer - 1)

        planar_distance = np.linalg.norm(self.pos - player.world_pos)
        if planar_distance < self.collision_radius:
            if player_alt is not None and abs(player_alt - self.altitude) >= self.altitude_hit_radius:
                return
            player.take_damage(self.damage)
            self.alive = False
            print(f"[OBSTACLE] Igrač se zabio u prepreku! -{self.damage} HP")

    def check_collision(self, projectile):
        planar_hit = np.linalg.norm(self.pos - projectile.pos) < self.collision_radius + projectile.hit_radius
        proj_height = getattr(projectile, "height", self.altitude)
        vertical_hit = abs(self.altitude - proj_height) < (
            self.altitude_hit_radius + getattr(projectile, "vertical_hit_radius", projectile.hit_radius)
        )
        if planar_hit and vertical_hit:
            self.hit_timer = 10
            self.hp -= 50
            if self.hp <= 0:
                self.alive = False
            return True
        return False

    def draw(self, screen, mode7):
        if not self.alive:
            return

        if self.anchor_to_floor:
            screen_x, screen_y, scale = self._project_to_floor(mode7)
        elif self.anchor_to_ceiling:
            screen_x, screen_y, scale = self._project_to_ceiling(mode7)
        else:
            screen_x, screen_y, scale = mode7.project(self.pos, world_height=self.altitude)
        if scale > 0:
            building_scale = int(scale * 1.5)
            if building_scale < 4:
                return
            scaled_texture = pg.transform.scale(self.texture, (building_scale, building_scale))
            if self.anchor_to_ceiling:
                blit_y = int(screen_y)  # screen_y is the ceiling row; top of sprite hugs the sky
                indicator_cy = int(screen_y) + building_scale + 22
            else:
                blit_y = int(screen_y) - building_scale
                indicator_cy = int(screen_y) - building_scale - 22
            screen.blit(
                scaled_texture,
                (int(screen_x) - building_scale // 2, blit_y),
            )

            if self.hit_timer > 0:
                flash_width = max(2, building_scale // 12)
                pg.draw.circle(
                    screen,
                    (255, 226, 128),
                    (int(screen_x), blit_y + building_scale // 2),
                    max(6, building_scale // 2 + 6),
                    flash_width,
                )

            self._draw_height_indicator(screen, int(screen_x), indicator_cy, building_scale, mode7.alt)

    def _draw_height_indicator(self, screen, cx, cy, sprite_size, player_alt):
        if self.altitude_hit_radius == float('inf'):
            return  # Always-hittable obstacles don't need an indicator
        threshold = self.altitude_hit_radius + PROJECTILE_HEIGHT_HIT_RADIUS
        diff = self.altitude - player_alt
        r = max(5, sprite_size // 10)

        if abs(diff) < threshold:
            pg.draw.circle(screen, (0, 210, 0), (cx, cy), r)
        elif diff > 0:
            # obstacle has higher altitude value → it's closer to the ground → player must descend
            pts = [(cx, cy + r), (cx - r, cy - r), (cx + r, cy - r)]
            pg.draw.polygon(screen, (220, 40, 40), pts)
        else:
            # obstacle has lower altitude value → it's higher in the sky → player must ascend
            pts = [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
            pg.draw.polygon(screen, (60, 140, 255), pts)

    def _project_to_floor(self, mode7):
        # Mirrors the mode7 floor renderer's inverse mapping so the sprite's bottom edge
        # lands on the floor row at this world distance, regardless of altitude.
        relative_pos = self.pos - mode7.camera_pos
        cos_a, sin_a = np.cos(mode7.camera_angle), np.sin(mode7.camera_angle)
        rotated_x = relative_pos[0] * cos_a - relative_pos[1] * sin_a
        rotated_y = relative_pos[0] * sin_a + relative_pos[1] * cos_a
        if rotated_y <= 0.1:
            return -1000, -1000, 0
        screen_x = int(HALF_WIDTH + rotated_x / rotated_y * WIDTH / 4)
        alt = mode7.alt
        screen_y = int(HALF_HEIGHT + (FOCAL_LEN / rotated_y - alt) / (1 + alt))
        scale = max(5, int(100 / rotated_y))
        return screen_x, screen_y, scale

    def _project_to_ceiling(self, mode7):
        # Mirror of _project_to_floor: the sky row is at HEIGHT - floor_row for the same world distance,
        # so the sprite's TOP edge can hug the ceiling regardless of altitude.
        relative_pos = self.pos - mode7.camera_pos
        cos_a, sin_a = np.cos(mode7.camera_angle), np.sin(mode7.camera_angle)
        rotated_x = relative_pos[0] * cos_a - relative_pos[1] * sin_a
        rotated_y = relative_pos[0] * sin_a + relative_pos[1] * cos_a
        if rotated_y <= 0.1:
            return -1000, -1000, 0
        screen_x = int(HALF_WIDTH + rotated_x / rotated_y * WIDTH / 4)
        alt = mode7.alt
        floor_y = HALF_HEIGHT + (FOCAL_LEN / rotated_y - alt) / (1 + alt)
        ceiling_y = HEIGHT - int(floor_y)
        scale = max(5, int(100 / rotated_y))
        return screen_x, ceiling_y, scale


class SmallBuilding(Obstacle):
    def __init__(self, pos, texture_path=None):
        super().__init__(pos, damage=3, collision_radius=0.7, texture_path=texture_path, hp=80)
        if not texture_path:
            self.texture = self._make_small_placeholder()

    def _make_small_placeholder(self):
        surf = pg.Surface((48, 48), pg.SRCALPHA)
        pg.draw.rect(surf, (100, 100, 110), (6, 12, 36, 36))
        pg.draw.polygon(surf, (70, 70, 80), [(2, 12), (24, 0), (46, 12)])
        pg.draw.rect(surf, (200, 220, 255), (14, 20, 10, 10))
        pg.draw.rect(surf, (200, 220, 255), (28, 20, 10, 10))
        return surf


class LargeBuilding(Obstacle):
    def __init__(self, pos, texture_path=None):
        super().__init__(pos, damage=8, collision_radius=1.2, texture_path=texture_path, hp=150)
        if not texture_path:
            self.texture = self._make_large_placeholder()

    def _make_large_placeholder(self):
        surf = pg.Surface((80, 96), pg.SRCALPHA)
        pg.draw.rect(surf, (90, 60, 40), (8, 20, 64, 76))
        pg.draw.polygon(surf, (60, 40, 25), [(0, 20), (40, 0), (80, 20)])
        for row in range(2):
            for col in range(3):
                pg.draw.rect(surf, (200, 220, 255), (16 + col * 20, 30 + row * 24, 12, 14))
        pg.draw.rect(surf, (50, 30, 15), (30, 70, 20, 26))
        return surf


class Dune(Obstacle):
    """Ground-level obstacle on map 2. Only hits when the player is flying low (alt ≳ 0.85)."""
    altitude = 1.0
    altitude_hit_radius = 0.15
    anchor_to_floor = True

    def __init__(self, pos):
        super().__init__(pos, damage=5, collision_radius=1.0, hp=120,
                         texture_path='assets/textures/sprjatovi-png/Dina.png')


class Cloud(Obstacle):
    """Sky-level obstacle on map 1. Only hits when the player is at the cloud's altitude
    (not when flying above or below where the sprite is rendered)."""
    altitude = 0.02
    altitude_hit_radius = 0.08
    anchor_to_ceiling = True

    def __init__(self, pos):
        super().__init__(pos, damage=4, collision_radius=1.2, hp=80,
                         texture_path='assets/textures/sprjatovi-png/Oblak.png')


class Volcano(Obstacle):
    """Ground-level obstacle on map 3. Only hits when the player is flying low (alt ≳ 0.85)."""
    altitude = 1.0
    altitude_hit_radius = 0.15
    anchor_to_floor = True

    def __init__(self, pos):
        # Vulkan.png is 192x256 but draw() force-scales to a square, so the on-screen
        # silhouette is wider than 1.1 felt in world space. Bumped to match the visual.
        super().__init__(pos, damage=8, collision_radius=1.6, hp=150,
                         texture_path='assets/textures/sprjatovi-png/Vulkan.png')
