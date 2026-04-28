# TODO: replace infinite wave system with 4 defined levels (see GDD)
import random

from entities.enemies import Enemy, FastEnemy, TankEnemy
from entities.obstacles import Obstacle, SmallBuilding, LargeBuilding
from settings import PLAYER_MAX_ALTITUDE


LEVEL_TEXTURES = [
    ('assets/textures/environment/map1.png', 'assets/textures/environment/sky_cloudyday_lowres.png'),
    ('assets/textures/environment/map2.png', 'assets/textures/environment/sky_cloudynight_lowres.png'),
    ('assets/textures/environment/map3.png', 'assets/textures/environment/sky_night_lowres.png'),
]


class LevelManager:
    def __init__(self, mode7, enemies, obstacles):
        self.mode7 = mode7
        self.enemies = enemies
        self.obstacles = obstacles
        self._current_level_idx = -1
        self._preloaded = self.mode7.preload_levels(LEVEL_TEXTURES)

    def spawn_wave(self, wave_num):
        self.enemies.clear()
        self.obstacles.clear()

        if wave_num <= 3:
            level_idx = 0
        elif wave_num <= 6:
            level_idx = 1
        else:
            level_idx = 2

        if level_idx != self._current_level_idx:
            self._current_level_idx = level_idx
            self.mode7.apply_preloaded(self._preloaded[level_idx])

        for _ in range(5 + wave_num * 2):
            x, y = random.uniform(-10, 10), random.uniform(-10, 10)
            spawn_height = float(getattr(self.mode7, "alt", Enemy.DEFAULT_MIN_HEIGHT))
            if wave_num < 5:
                enemy_cls = Enemy
            elif wave_num < 10:
                enemy_cls = random.choice([Enemy, FastEnemy])
            elif wave_num < 15:
                enemy_cls = random.choice([FastEnemy, TankEnemy])
            else:
                enemy_cls = random.choice([Enemy, FastEnemy, TankEnemy])
            enemy = enemy_cls((x, y), height=spawn_height)
            self.enemies.append(enemy)

        num_obstacles = min(3 + wave_num, 15) 
        for _ in range(num_obstacles):
          
            ox = random.uniform(-12, 12)
            oy = random.uniform(-12, 12)
            
            while abs(ox) < 2.0 and abs(oy) < 2.0:
                ox = random.uniform(-12, 12)
                oy = random.uniform(-12, 12)

           
            building_type = random.choices(
                [SmallBuilding, Obstacle, LargeBuilding],
                weights=[3, 2, 1] if wave_num < 10 else [1, 2, 3],
                k=1,
            )[0]
            self.obstacles.append(building_type((ox, oy),texture_path="assets/textures/environment/ground_halfsnow_lowres.png"))
