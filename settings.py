from enum import Enum

# settings

#WIN_RES = WIDTH, HEIGHT = 1280, 720
WIN_RES = WIDTH, HEIGHT = 1600, 900
# WIN_RES = WIDTH, HEIGHT = 1920, 1080
HALF_WIDTH, HALF_HEIGHT = WIDTH // 2, HEIGHT // 2
FOCAL_LEN = 250
SCALE = 100
SPEED = 0.05
MENU = 'menu' # *States
GAME = 'game'
GAME_OVER = 'game_over'


class WeaponType(str, Enum):
    REVOLVER = "revolver"
    SHOTGUN = "shotgun"
    MINIGUN = "minigun"
