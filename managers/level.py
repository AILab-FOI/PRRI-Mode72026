import random

from entities.enemies import Enemy, FastEnemy, TankEnemy
from entities.obstacles import Obstacle, SmallBuilding, LargeBuilding, Cloud, Dune, Volcano


LEVEL_TEXTURES = [
    ('assets/textures/environment/map1.png', 'assets/textures/environment/sky_cloudyday_lowres.png'),
    ('assets/textures/environment/map2.png', 'assets/textures/environment/sky_cloudynight_lowres.png'),
    ('assets/textures/environment/map3.png', 'assets/textures/environment/sky_night_lowres.png'),
]

# Enemy pools per map (index 0-2)
_ENEMY_POOL = [
    [Enemy],                    # map 1: only standard
    [Enemy, FastEnemy],         # map 2: standard + fast
    [FastEnemy, TankEnemy],     # map 3: fast + tank
]

# Obstacle per map: clouds in the sky on map 1, dunes on the ground on map 2, volcanoes on map 3.
_OBSTACLE_PER_MAP = [Cloud, Dune, Volcano]


class LevelManager:
    def __init__(self, mode7, enemies, obstacles, on_level_change=None):
        self.mode7 = mode7
        self.enemies = enemies
        self.obstacles = obstacles
        self._current_level_idx = -1
        self._preloaded = self.mode7.preload_levels(LEVEL_TEXTURES)
        self.on_level_change = on_level_change

    def spawn_wave(self, wave_num):
        self.enemies.clear()
        self.obstacles.clear()

        map_idx = min((wave_num - 1) // 3, 2)   # 0, 1, 2
        wave_in_map = (wave_num - 1) % 3         # 0, 1, 2  →  7, 8, 9 enemies

        if map_idx != self._current_level_idx:
            self._current_level_idx = map_idx
            self.mode7.apply_preloaded(self._preloaded[map_idx])
            if self.on_level_change:
                self.on_level_change(map_idx)

        enemy_count = 7 + wave_in_map
        spawn_height = float(getattr(self.mode7, "alt", Enemy.DEFAULT_MIN_HEIGHT))
        pool = _ENEMY_POOL[map_idx]

        for _ in range(enemy_count):
            x, y = random.uniform(-10, 10), random.uniform(-10, 10)
            self.enemies.append(random.choice(pool)((x, y), height=spawn_height))

        num_obstacles = min(3 + wave_num, 15)
        obstacle_cls = _OBSTACLE_PER_MAP[map_idx]

        for _ in range(num_obstacles):
            ox = random.uniform(-10, 10)
            oy = random.uniform(-10, 10)
            while abs(ox) < 2.0 and abs(oy) < 2.0:
                ox = random.uniform(-10, 10)
                oy = random.uniform(-10, 10)
            self.obstacles.append(obstacle_cls((ox, oy)))

    def apply_boss_map(self):
        if self._current_level_idx != 2:
            self._current_level_idx = 2
            self.mode7.apply_preloaded(self._preloaded[2])
