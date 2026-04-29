import pygame as pg
import numpy as np
from pathlib import Path
from settings import *
from numba import njit, prange

SPRITE_SCREEN_X = WIDTH // 2
SPRITE_SCREEN_Y = HALF_HEIGHT + 80
SPRITE_DISPLAY_SIZE = 128
PROJECTION_Y_SCALE = 50.0
PLAYER_ANIMATION_FRAME_MS = 110
PLAYER_ANIMATION_ROOT = Path("assets/textures/novi-zeppelin")
PLAYER_GLOW_PADDING = 10
PLAYER_GLOW_COLOR = (255, 196, 92, 80)


class Mode7:
    def __init__(self, app):
        self.app = app
#        self.floor_tex = pg.image.load('assets/textures/environment/ground_town_lowres.png').convert()
        self.set_map('assets/textures/environment/map1.png', 'assets/textures/environment/sky_cloudyday_lowres.png')
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)

#        self.ceil_tex = pg.image.load('assets/textures/environment/ceil_3.png').convert()
        self.tex_size = self.ceil_tex.get_size()
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)

        self.screen_array = pg.surfarray.array3d(pg.Surface(WIN_RES))

        self.map_mode = 0
        self.map_world_size = 24.0
        self.alt = AIR_LANE_REFERENCE_HEIGHT
        self.reference_flight_height = AIR_LANE_REFERENCE_HEIGHT
        self.camera_pos = np.zeros(2, dtype=np.float32)
        self.camera_angle = 0.0

        self.player_animations = self._load_player_animations()

    def _load_player_animations(self):
        animations = {}
        for state_dir in PLAYER_ANIMATION_ROOT.iterdir():
            if not state_dir.is_dir():
                continue

            frames = []
            for frame_path in sorted(state_dir.glob("*.png")):
                raw_frame = pg.image.load(str(frame_path)).convert_alpha()
                frames.append(self._prepare_player_sprite(raw_frame))

            if frames:
                animations[state_dir.name] = frames

        if not animations:
            raw_sprite = pg.image.load('assets/textures/environment/airship_1.png').convert_alpha()
            fallback = self._prepare_player_sprite(raw_sprite)
            animations["neutral"] = [fallback]

        return animations

    def _prepare_player_sprite(self, raw_sprite):
        sprite = pg.transform.scale(raw_sprite, (SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE))
        surface_size = SPRITE_DISPLAY_SIZE + PLAYER_GLOW_PADDING * 2
        composed = pg.Surface((surface_size, surface_size), pg.SRCALPHA)
        glow = self._make_player_glow(sprite)
        composed.blit(glow, (0, 0))
        composed.blit(sprite, (PLAYER_GLOW_PADDING, PLAYER_GLOW_PADDING))
        return composed

    def _make_player_glow(self, sprite):
        surface_size = SPRITE_DISPLAY_SIZE + PLAYER_GLOW_PADDING * 2
        glow = pg.Surface((surface_size, surface_size), pg.SRCALPHA)
        mask_surface = pg.mask.from_surface(sprite).to_surface(
            setcolor=PLAYER_GLOW_COLOR,
            unsetcolor=(0, 0, 0, 0),
        ).convert_alpha()
        glow.blit(mask_surface, (PLAYER_GLOW_PADDING, PLAYER_GLOW_PADDING))

        small_size = max(1, surface_size // 4)
        softened = pg.transform.smoothscale(glow, (small_size, small_size))
        softened = pg.transform.smoothscale(softened, (surface_size, surface_size))
        glow.blit(softened, (0, 0), special_flags=pg.BLEND_RGBA_ADD)
        return glow

    def set_textures(self, sky_path, ground_path):
        self.floor_tex = pg.image.load(ground_path).convert()
        self.ceil_tex = pg.image.load(sky_path).convert()
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)
        self.map_mode = 0

    def set_map(self, map_path, sky_path='assets/textures/environment/sky_lowres.png'):
        self.floor_tex = pg.image.load(map_path).convert()
        self.ceil_tex = pg.image.load(sky_path).convert()
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)
        self.map_mode = 1

    def preload_levels(self, level_textures):
        preloaded = []
        for map_path, sky_path in level_textures:
            floor_tex = pg.image.load(map_path).convert()
            ceil_tex = pg.image.load(sky_path).convert()
            tex_size = floor_tex.get_size()
            floor_array = pg.surfarray.array3d(floor_tex)
            ceil_tex = pg.transform.scale(ceil_tex, tex_size)
            ceil_array = pg.surfarray.array3d(ceil_tex)
            preloaded.append((floor_array, ceil_array, tex_size))
        return preloaded

    def apply_preloaded(self, preloaded_entry):
        self.floor_array, self.ceil_array, self.tex_size = preloaded_entry
        self.map_mode = 1

    def sync_camera_to_player(self):
        player = self.app.player
        k = SPRITE_SCREEN_Y - HALF_HEIGHT  # 80 px — sprite offset from horizon
        pivot_dist = FOCAL_LEN / (k + (k + 1) * self.alt)
        forward = np.array([np.sin(player.angle), np.cos(player.angle)], dtype=np.float32)
        self.camera_pos = player.world_pos - forward * pivot_dist
        self.camera_angle = player.angle


    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_q]:
            self.alt -= PLAYER_ALTITUDE_SPEED
        if keys[pg.K_e]:
            self.alt += PLAYER_ALTITUDE_SPEED
        self.alt = min(max(self.alt, PLAYER_MIN_ALTITUDE), PLAYER_MAX_ALTITUDE)

        self.sync_camera_to_player()

        self.screen_array = self.render_frame(self.floor_array, self.ceil_array, self.screen_array,
                                              self.tex_size, self.camera_angle, self.camera_pos, self.alt,
                                              self.map_mode, self.map_world_size)

    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)
    
    def draw_player_sprite(self):
        player = self.app.player
        state = getattr(player, "animation_state", "neutral")
        frames = self.player_animations.get(state) or self.player_animations.get("neutral")
        frame_index = (pg.time.get_ticks() // PLAYER_ANIMATION_FRAME_MS) % len(frames)
        sprite = frames[frame_index]

        if player.is_invulnerable() and (pg.time.get_ticks() // 90) % 2 == 0:
            sprite = sprite.copy()
            sprite.fill((255, 240, 80, 90), special_flags=pg.BLEND_RGBA_ADD)

        blit_x = SPRITE_SCREEN_X - sprite.get_width() // 2
        blit_y = SPRITE_SCREEN_Y - sprite.get_height() // 2
        self.app.screen.blit(sprite, (blit_x, blit_y))

    def project(self, world_pos, world_height=None):
        """Convert world coordinates (x, y) to screen coordinates with optional air-lane height."""
        relative_pos = world_pos - self.camera_pos
        rotated_x = relative_pos[0] * np.cos(self.camera_angle) - relative_pos[1] * np.sin(self.camera_angle)
        rotated_y = relative_pos[0] * np.sin(self.camera_angle) + relative_pos[1] * np.cos(self.camera_angle)

        if rotated_y <= 0.1:  # Prevent division by zero and objects disappearing completely
            return -1000, -1000, 0  # Return an off-screen position

        screen_x = int(HALF_WIDTH + rotated_x / rotated_y * WIDTH / 4)
        h = world_height if world_height is not None else 0.0
        screen_y = int(HALF_HEIGHT + (self.alt - h) * PROJECTION_Y_SCALE / rotated_y)

        # Scale size based on distance (closer = bigger)
        scale = max(5, int(100 / rotated_y))  # Prevent scale from going too small

        return screen_x, screen_y, scale

    @staticmethod
    @njit(fastmath=True, parallel=True)
    def render_frame(floor_array, ceil_array, screen_array, tex_size, angle, player_pos, alt,
                     map_mode, map_world_size):

        sin, cos = np.sin(angle), np.cos(angle)

        # iterating over the screen array
        for i in prange(WIDTH):
            new_alt = alt
            for j in range(HALF_HEIGHT, HEIGHT):
                x = HALF_WIDTH - i
                y = FOCAL_LEN
                z = j - HALF_HEIGHT + new_alt

                # rotation
                px = (x * cos - y * sin)
                py = (x * sin + y * cos)

                # floor projection and transformation
                floor_x = px / z - player_pos[0]
                floor_y = py / z + player_pos[1]

                # floor pos and color
                floor_col = floor_array[0, 0]
                if map_mode == 1:
                    # single map image — linear mapping, no tiling
                    u = int((floor_x / map_world_size + 0.5) * tex_size[0])
                    v = int((floor_y / map_world_size + 0.5) * tex_size[1])
                    if 0 <= u < tex_size[0] and 0 <= v < tex_size[1]:
                        floor_col = floor_array[u, v]
                    else:
                        floor_col = floor_array[0, 0] - floor_array[0, 0]
                else:
                    floor_pos = int(floor_x * SCALE % tex_size[0]), int(floor_y * SCALE % tex_size[1])
                    floor_col = floor_array[floor_pos]

                # ceil projection and transformation
                ceil_x = alt * px / z - player_pos[0] * 0.3
                ceil_y = alt * py / z + player_pos[1] * 0.3

                # ceil pos and color
                ceil_u = int(np.abs(ceil_x * SCALE) % tex_size[0])
                ceil_v = int(np.abs(ceil_y * SCALE) % tex_size[1])
                ceil_pos = (ceil_u, ceil_v)
                ceil_col = ceil_array[ceil_pos]

                # shading
                depth = min(max(2.5 * (abs(z) / HALF_HEIGHT), 0), 1)
                fog = (1 - depth) * 230

                floor_col = (floor_col[0] * depth + fog,
                             floor_col[1] * depth + fog,
                             floor_col[2] * depth + fog)

                ceil_col = (ceil_col[0] * depth + fog,
                            ceil_col[1] * depth + fog,
                            ceil_col[2] * depth + fog)

                # fill screen array
                screen_array[i, j] = floor_col
                screen_array[i, -j] = ceil_col

                # next depth
                new_alt += alt

        return screen_array
