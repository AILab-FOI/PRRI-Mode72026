import pygame as pg
import sys
from settings import WIN_RES, MENU, GAME

class Menu:
    def __init__(self, app):
        self.app = app
        self.screen = self.app.screen
        self.white = (255, 255, 255)
        self.grey = (220, 210, 180)
        self.font = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 74)
        self.title_font = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 100)
        self.background = pg.image.load('assets/textures/ui/main_menu_no_text.png').convert()
        self.background = pg.transform.smoothscale(self.background, WIN_RES)
        print("Background loaded.")

        button_width, button_height = 300, 60
        screen_width, screen_height = WIN_RES
        button_x = (screen_width - button_width) // 2
        button_y_start = self.app.screen.get_height() // 2 - 190

        self.buttons = [
            {'text': 'Play', 'rect': pg.Rect(button_x, button_y_start, button_width, button_height), 'action': self.start_game},
            {'text': 'Quit', 'rect': pg.Rect(button_x, button_y_start + (button_height + 30), button_width, button_height), 'action': self.exit_game}
        ]

    def start_game(self):
        print("Starting game.")
        self.app.state = GAME
        self.app.switch_to_game()

    def exit_game(self):
        pg.quit()
        sys.exit()

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos):
                if pg.mouse.get_pressed()[0]:
                    button['action']()

    def draw(self):
        print("Drawing menu.")
        self.app.screen.blit(self.background, (0, 0))
        title_shadow = self.title_font.render("The Last Zeppelin", True, (45, 24, 28))
        title = self.title_font.render("The Last Zeppelin", True, self.grey)

        x_center = self.screen.get_width() // 2
        start_y = max(20, self.screen.get_height() // 12 - 45)

        self.screen.blit(title_shadow, (x_center - title_shadow.get_width() // 2 + 4, start_y + 4))
        self.screen.blit(title, (x_center - title.get_width() // 2, start_y))

        for button in self.buttons:
            shadow = self.font.render(button['text'], True, (45, 24, 28))
            text = self.font.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            shadow_rect = shadow.get_rect(center=(button['rect'].centerx + 3, button['rect'].centery + 3))
            self.app.screen.blit(shadow, shadow_rect)
            self.app.screen.blit(text, text_rect)
