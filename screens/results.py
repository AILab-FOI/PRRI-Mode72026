import pygame as pg
import time

_BTN_COLOR_NORMAL  = (255, 255, 255)
_BTN_COLOR_HOVER   = (255, 220, 100)
_BTN_COLOR_CLICKED = (255, 130, 50)
_BTN_CLICK_DELAY   = 0.18


class ResultsScreen:
    def __init__(self, screen, time_survived, enemies_killed, waves_survived, on_retry=None, on_menu=None):
        self.screen = screen
        self.bg_image = pg.image.load("assets/textures/ui/main_menu_no_text.png").convert()
        self.bg_image = pg.transform.scale(self.bg_image, self.screen.get_size())
        self.time_survived = time_survived
        self.enemies_killed = enemies_killed
        self.waves_survived = waves_survived
        self.font = pg.font.Font("assets/fonts/steampunk-mainmenu.ttf", 100)
        self.btn_font = pg.font.Font("assets/fonts/steampunk-mainmenu.ttf", 74)
        self.small_font = pg.font.SysFont("Comic Sans MS", 40)
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.fade_in_duration = 60
        self.elapsed_time = 0
        self.y_position = self.screen.get_height() // 2
        self.game_over_text = self.font.render("GAME OVER", True, self.white)
        self.results_fade_in_alpha = 0
        self.result_texts = [
            self.small_font.render(f"Time Survived: {self.format_time(self.time_survived)}", True, self.white),
            self.small_font.render(f"Enemies Killed: {self.enemies_killed}", True, self.white),
            self.small_font.render(f"Waves Survived: {self.waves_survived}", True, self.white)
        ]

        button_width, button_height = 300, 60
        cx = screen.get_width() // 2
        btn_y = screen.get_height() // 2 + 3 * 80 + 40
        self.buttons = [
            {'text': 'Retry', 'rect': pg.Rect(cx - button_width - 20, btn_y, button_width, button_height), 'action': on_retry},
            {'text': 'Menu',  'rect': pg.Rect(cx + 20,                 btn_y, button_width, button_height), 'action': on_menu},
        ]
        self.hovered_button = None
        self.clicked_button = None
        self.click_time = 0.0
        self.prev_mouse_pressed = False

    def format_time(self, time_in_seconds):
        minutes = time_in_seconds // 60
        seconds = time_in_seconds % 60
        return f"{int(minutes):02}:{int(seconds):02}"

    def update(self):
        self.elapsed_time += 1
        if self.elapsed_time < 60:
            self.y_position -= 1
        if self.elapsed_time > 60:
            if self.results_fade_in_alpha < 255:
                self.results_fade_in_alpha += 5

        if not self.is_done():
            return

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
            if action:
                action()

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.screen.blit(self.game_over_text, (self.screen.get_width() // 2 - self.game_over_text.get_width() // 2, self.screen.get_height() // 5))
        alpha_surface = pg.Surface((self.screen.get_width(), self.screen.get_height()), pg.SRCALPHA)
        alpha_surface.fill((0, 0, 0, 255 - self.results_fade_in_alpha))
        self.screen.blit(alpha_surface, (0, 0))
        if self.elapsed_time > 60:
            for i, result_text in enumerate(self.result_texts):
                self.screen.blit(result_text, (self.screen.get_width() // 2 - result_text.get_width() // 2, self.screen.get_height() // 2 + i * 80))
        if self.is_done():
            for button in self.buttons:
                if button is self.clicked_button:
                    color = _BTN_COLOR_CLICKED
                elif button is self.hovered_button:
                    color = _BTN_COLOR_HOVER
                else:
                    color = _BTN_COLOR_NORMAL
                shadow = self.btn_font.render(button['text'], True, (45, 24, 28))
                text = self.btn_font.render(button['text'], True, color)
                text_rect = text.get_rect(center=button['rect'].center)
                shadow_rect = shadow.get_rect(center=(button['rect'].centerx + 3, button['rect'].centery + 3))
                self.screen.blit(shadow, shadow_rect)
                self.screen.blit(text, text_rect)
        pg.display.flip()

    def is_done(self):
        return self.results_fade_in_alpha >= 255
