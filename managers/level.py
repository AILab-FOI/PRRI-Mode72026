# TODO: replace infinite wave system with 4 defined levels (see GDD)
import random

from entities.enemies import Enemy, FastEnemy, TankEnemy


class LevelManager:
    def __init__(self, mode7, enemies):
        self.mode7 = mode7
        self.enemies = enemies

    def spawn_wave(self, wave_num):
        self.enemies.clear()
        for _ in range(5 + wave_num * 2):
            x, y = random.uniform(-10, 10), random.uniform(-10, 10)
            if wave_num < 5:
                enemy = Enemy((x, y))
            elif wave_num < 10:
                enemy = random.choice([Enemy((x, y)), FastEnemy((x, y))])
            elif wave_num < 15:
                enemy = random.choice([FastEnemy((x, y)), TankEnemy((x, y))])
            else:
                enemy = random.choice([Enemy((x, y)), FastEnemy((x, y)), TankEnemy((x, y))])
            self.enemies.append(enemy)

        match wave_num:
            case 3:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_cloudyday_lowres.png",
                    "assets/textures/environment/ground_sand_lowres.png",
                )
            case 6:
                self.mode7.set_textures(
                    "assets/textures/environment/polluted_sky_lowres.png",
                    "assets/textures/environment/groubd_volcan_lowres.png",
                )
            case 9:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_cloudynight_lowres.png",
                    "assets/textures/environment/ground_snow_lowres.png",
                )
            case 12:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_lowres.png",
                    "assets/textures/environment/ground_grass_lowres.png",
                )
            case 15:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_cloudyday_lowres.png",
                    "assets/textures/environment/ground_frozenice_lowres.png",
                )
            case 18:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_cloudyday_lowres.png",
                    "assets/textures/environment/ground_swamp_lowres.png",
                )
            case 21:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_night_lowres.png",
                    "assets/textures/environment/ground_factoryfloor_lowres.png",
                )
            case 24:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_cloudynight_lowres.png",
                    "assets/textures/environment/ground_town_lowres.png",
                )
            case 27:
                self.mode7.set_textures(
                    "assets/textures/environment/polluted_sky_lowres.png",
                    "assets/textures/environment/ground_gravel_lowres.png",
                )
            case 30:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_lowres.png",
                    "assets/textures/environment/ground_rail_lowres.png",
                )
            case 33:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_cloudyday_lowres.png",
                    "assets/textures/environment/ground_graveldirt_lowres.png",
                )
            case 36:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_night_lowres.png",
                    "assets/textures/environment/ground_halfsnow_lowres.png",
                )
            case 39:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_lowres.png",
                    "assets/textures/environment/ground_sea_lowres.png",
                )
            case 42:
                self.mode7.set_textures(
                    "assets/textures/environment/sky_cloudyday_lowres.png",
                    "assets/textures/environment/ground_dirt_lowres.png",
                )
            case _:
                pass
