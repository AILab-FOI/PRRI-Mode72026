import pygame as pg
import sys
import time
from pathlib import Path
from settings import WIN_RES, MENU, LOADING, GAME

_BTN_COLOR_NORMAL  = (255, 255, 255)
_BTN_COLOR_HOVER   = (255, 220, 100)
_BTN_COLOR_CLICKED = (255, 130, 50)
_BTN_CLICK_DELAY   = 0.18


class Menu:
    def __init__(self, app):
        self.app = app
        self.screen = self.app.screen
        self.grey = (220, 210, 180)
        self.font = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 74)
        self.title_font = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 100)
        self.background = pg.image.load('assets/textures/ui/main_menu_no_text.png').convert()
        self.background = pg.transform.smoothscale(self.background, WIN_RES)

        button_width, button_height = 300, 60
        screen_width, screen_height = WIN_RES
        button_x = (screen_width - button_width) // 2
        button_y_start = self.app.screen.get_height() // 2 - 190

        self.buttons = [
            {'text': 'Play', 'rect': pg.Rect(button_x, button_y_start, button_width, button_height), 'action': self.start_game},
            {'text': 'Quit', 'rect': pg.Rect(button_x, button_y_start + (button_height + 30), button_width, button_height), 'action': self.exit_game}
        ]

        self.hovered_button = None
        self.clicked_button = None
        self.click_time = 0.0
        self.prev_mouse_pressed = False

    def start_game(self):
        self.app.state = LOADING
        self.app.loading_screen.start()

    def exit_game(self):
        pg.quit()
        sys.exit()

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        just_clicked = mouse_pressed and not self.prev_mouse_pressed
        self.prev_mouse_pressed = mouse_pressed

        self.hovered_button = None
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos):
                self.hovered_button = button
                if just_clicked and self.clicked_button is None:
                    self.clicked_button = button
                    self.click_time = time.time()

        if self.clicked_button is not None and time.time() - self.click_time >= _BTN_CLICK_DELAY:
            action = self.clicked_button['action']
            self.clicked_button = None
            action()

    def draw(self):
        self.app.screen.blit(self.background, (0, 0))
        title_shadow = self.title_font.render("The Last Zeppelin", True, (45, 24, 28))
        title = self.title_font.render("The Last Zeppelin", True, self.grey)

        x_center = self.screen.get_width() // 2
        start_y = max(20, self.screen.get_height() // 12 - 45)

        self.screen.blit(title_shadow, (x_center - title_shadow.get_width() // 2 + 4, start_y + 4))
        self.screen.blit(title, (x_center - title.get_width() // 2, start_y))

        for button in self.buttons:
            if button is self.clicked_button:
                color = _BTN_COLOR_CLICKED
            elif button is self.hovered_button:
                color = _BTN_COLOR_HOVER
            else:
                color = _BTN_COLOR_NORMAL
            shadow = self.font.render(button['text'], True, (45, 24, 28))
            text = self.font.render(button['text'], True, color)
            text_rect = text.get_rect(center=button['rect'].center)
            shadow_rect = shadow.get_rect(center=(button['rect'].centerx + 3, button['rect'].centery + 3))
            self.app.screen.blit(shadow, shadow_rect)
            self.app.screen.blit(text, text_rect)


_LOADING_SPRITE_SIZE = 220
_LOADING_DURATION = 2.5
_LOADING_FRAME_MS = 110
_LOADING_BG = (18, 12, 8)
_LOADING_DOTS_INTERVAL = 0.45


class LoadingScreen:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 52)
        self.frames = self._load_frames()
        self.start_time = 0.0
        self.frame_index = 0
        self.last_frame_time = 0

    def _load_frames(self):
        frame_dir = Path('assets/textures/novi-zeppelin/neutral')
        frames = []
        for path in sorted(frame_dir.glob('*.png')):
            img = pg.image.load(str(path)).convert_alpha()
            img = pg.transform.smoothscale(img, (_LOADING_SPRITE_SIZE, _LOADING_SPRITE_SIZE))
            frames.append(img)
        return frames or [pg.Surface((_LOADING_SPRITE_SIZE, _LOADING_SPRITE_SIZE), pg.SRCALPHA)]

    def start(self):
        now = time.time()
        self.start_time = now
        self.frame_index = 0
        self.last_frame_time = now
        self.app.audio.play_game_music()

    def update(self):
        now = time.time()
        if now - self.last_frame_time >= _LOADING_FRAME_MS / 1000:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_frame_time = now
        if now - self.start_time >= _LOADING_DURATION:
            self.app.state = GAME

    def draw(self):
        self.screen.fill(_LOADING_BG)
        w, h = self.screen.get_size()
        cx, cy = w // 2, h // 2

        frame = self.frames[self.frame_index]
        bob = int(6 * pg.math.Vector2(0, 1).rotate(
            (time.time() * 200) % 360
        ).y)
        sprite_rect = frame.get_rect(center=(cx, cy - 40 + bob))
        self.screen.blit(frame, sprite_rect)

        dots = '.' * (int((time.time() - self.start_time) / _LOADING_DOTS_INTERVAL) % 4)
        label = f'Loading{dots}'
        shadow = self.font.render(label, True, (45, 24, 28))
        text = self.font.render(label, True, (220, 210, 180))
        ty = cy + _LOADING_SPRITE_SIZE // 2
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 3, ty + 3)))
        self.screen.blit(text, text.get_rect(center=(cx, ty)))
