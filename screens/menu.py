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
        self.title_font = pg.font.Font('assets/fonts/steampunk-mainmenu.ttf', 140)
        self.background = pg.image.load('assets/textures/ui/BG_notext.png').convert()
        print("Background loaded.")

        button_width, button_height = 300, 60
        screen_width, screen_height = WIN_RES
        button_x = (screen_width - button_width) // 2
        button_y_start = self.app.screen.get_height() // 2 + 100  # Pomiče Start game niže

        self.buttons = [
            {'text': 'Start game', 'rect': pg.Rect(button_x, button_y_start, button_width, button_height), 'action': self.start_game},
            {'text': 'Exit', 'rect': pg.Rect(button_x, button_y_start + (button_height + 50), button_width, button_height), 'action': self.exit_game}
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
        title_1 = self.title_font.render("Zeppelino", True, self.grey)
        title_2 = self.title_font.render("shooterino", True, self.grey)

        x_center = self.screen.get_width() // 2
        start_y = self.screen.get_height() // 10

        # nacrtaj prvi red
        self.screen.blit(title_1, (x_center - title_1.get_width() // 2, start_y))

        # nacrtaj drugi red ispod
        self.screen.blit(title_2, (x_center - title_2.get_width() // 2, start_y + title_1.get_height() + 10))
        for button in self.buttons:
            text = self.font.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            self.app.screen.blit(text, text_rect)
