import pygame as pg
from pathlib import Path
from settings import WIN_RES

# Place your cutscene images here — same resolution as the main menu background.
# Empty space should be in the upper-center area where stats are rendered.
_CUTSCENE_IMAGES = [
    'assets/textures/ui/cutscene1.png',
    'assets/textures/ui/cutscene2.png',
    'assets/textures/ui/cutscene3.png',
]
_FALLBACK_BG = (20, 14, 10)


class CutsceneScreen:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.title_font = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 68)
        self.stat_font  = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 46)
        self.hint_font  = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 34)
        self._bg_cache = {}
        self._map_num = 1
        self._stats = {}
        self._on_continue = None

    def _load_bg(self, map_num):
        if map_num not in self._bg_cache:
            path = _CUTSCENE_IMAGES[map_num - 1]
            if Path(path).exists():
                img = pg.image.load(path).convert()
                self._bg_cache[map_num] = pg.transform.smoothscale(img, WIN_RES)
            else:
                self._bg_cache[map_num] = None
        return self._bg_cache[map_num]

    def setup(self, map_num, stats, on_continue, boss_victory=False):
        self._map_num = map_num
        self._stats = stats
        self._on_continue = on_continue
        self._boss_victory = boss_victory
        self.app.audio.play_between_levels_music(map_num)

    def continue_game(self):
        if self._on_continue:
            self._on_continue()

    def draw(self):
        bg = self._load_bg(self._map_num)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(_FALLBACK_BG)

        w, h = self.screen.get_size()
        cx = w // 2
        y = h // 8

        if self._boss_victory:
            cy = h // 2
            self._blit_text(self.title_font, "Boss Defeated!", cx, cy - 60, (220, 210, 180))
            if (pg.time.get_ticks() // 550) % 2 == 0:
                self._blit_text(self.hint_font, "Press ENTER for Main Menu", cx, cy + 60, (180, 160, 120))
        else:
            self._blit_text(self.title_font, f"Map {self._map_num} Complete", cx, y, (220, 210, 180))
            y += 96

            self._blit_text(self.stat_font, f"Enemies destroyed:  {self._stats['enemies_killed']}", cx, y, (255, 255, 255))
            y += 62
            self._blit_text(self.stat_font, f"Damage received:    {self._stats['damage_taken']}", cx, y, (255, 200, 150))
            y += 62
            self._blit_text(self.stat_font, f"Waves survived:     {self._stats['waves']}", cx, y, (150, 220, 255))
            y += 96

            if (pg.time.get_ticks() // 550) % 2 == 0:
                self._blit_text(self.hint_font, "Press ENTER to continue", cx, y, (180, 160, 120))

    def _blit_text(self, font, text, cx, y, color):
        shadow = font.render(text, True, (30, 18, 8))
        surf   = font.render(text, True, color)
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 3, y + 3)))
        self.screen.blit(surf,   surf.get_rect(center=(cx, y)))
