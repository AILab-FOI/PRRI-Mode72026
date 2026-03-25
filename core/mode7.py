import pygame as pg
import numpy as np
from settings import *
from numba import njit, prange

class Mode7:
    def __init__(self, app):
        self.app = app
#        self.floor_tex = pg.image.load('assets/textures/environment/ground_town_lowres.png').convert()
        self.set_textures('assets/textures/environment/sky_lowres.png', 'assets/textures/environment/ground_grass_lowres.png')
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)

#        self.ceil_tex = pg.image.load('assets/textures/environment/ceil_3.png').convert()
        self.tex_size = self.ceil_tex.get_size()
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)

        self.screen_array = pg.surfarray.array3d(pg.Surface(WIN_RES))

        self.alt = 1.0

    def set_textures(self, sky_path, ground_path):
        self.floor_tex = pg.image.load(ground_path).convert()
        self.ceil_tex = pg.image.load(sky_path).convert()
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)


    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_q]:
            self.alt += SPEED
        if keys[pg.K_e]:
            self.alt -= SPEED
        self.alt = min(max(self.alt, 0.3), 4.0)

        player = self.app.player
        self.screen_array = self.render_frame(self.floor_array, self.ceil_array, self.screen_array,
                                              self.tex_size, player.angle, player.pos, self.alt)

    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    def project(self, world_pos):
        """Convert world coordinates (x, y) to screen coordinates (screen_x, screen_y) with size scaling"""
        player = self.app.player
        relative_pos = world_pos - player.pos
        rotated_x = relative_pos[0] * np.cos(player.angle) - relative_pos[1] * np.sin(player.angle)
        rotated_y = relative_pos[0] * np.sin(player.angle) + relative_pos[1] * np.cos(player.angle)

        if rotated_y <= 0.1:  # Prevent division by zero and objects disappearing completely
            return -1000, -1000, 0  # Return an off-screen position

        screen_x = int(WIDTH / 2 + rotated_x / rotated_y * WIDTH / 4)
        screen_y = int(HEIGHT / 2 - self.alt * 50 / rotated_y)

        # Scale size based on distance (closer = bigger)
        scale = max(5, int(100 / rotated_y))  # Prevent scale from going too small

        return screen_x, screen_y, scale

    @staticmethod
    @njit(fastmath=True, parallel=True)
    def render_frame(floor_array, ceil_array, screen_array, tex_size, angle, player_pos, alt):

        sin, cos = np.sin(angle), np.cos(angle)

        # iterating over the screen array
        for i in prange(WIDTH):
            new_alt = alt
            for j in range(HALF_HEIGHT, HEIGHT):
                x = HALF_WIDTH - i
                y = j + FOCAL_LEN
                z = j - HALF_HEIGHT + new_alt

                # rotation
                px = (x * cos - y * sin)
                py = (x * sin + y * cos)

                # floor projection and transformation
                floor_x = px / z - player_pos[0]
                floor_y = py / z + player_pos[1]

                # floor pos and color
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
                # depth = 4 * abs(z) / HALF_HEIGHT
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
