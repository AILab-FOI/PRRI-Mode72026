import pygame as pg
import sys
import time
import numpy as np

from core.mode7 import Mode7
from entities.player import Player
from managers.audio import AudioManager
from managers.game import Game
from managers.ui import UIManager
from screens.menu import Menu
from screens.results import ResultsScreen
from settings import GAME, GAME_OVER, MENU, WIN_RES, WeaponType

class App:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.audio = AudioManager()
        self.mode7 = Mode7(self)
        self.player = Player()
        self.game = Game(self.mode7, self.player, self)
        self.menu = Menu(self)
        self.ui_manager = UIManager(self)
        self.state = MENU
        self.speed_multiplier = 1.0
        self.speed_timer = 0
        self.minigun_last_shot = 0
        self.weapon = WeaponType.REVOLVER
        self.weapon_timer = 0

        self.start_time = time.time()
        self.enemies_killed = 0
        self.results_screen = None
        self.shooting = False
        self.audio.play_menu_music()
        
    def apply_speed_boost(self, multiplier, duration=5):
        self.speed_multiplier = multiplier
        self.speed_timer = time.time() + duration
        print(f"[SPEED] Boost applied: x{multiplier} fo r {duration}s")

    def update(self):
        if self.state == MENU:
            self.menu.update()
        # Reset weapon after timer
        if self.weapon != WeaponType.REVOLVER and time.time() > self.weapon_timer:
            self.weapon = WeaponType.REVOLVER
            print("[TIMER] Power-up expired")
        elif self.state == GAME:
            if self.player.is_dead():
                self.audio.stop_powerup()
                self.state = GAME_OVER
                self.results_screen = ResultsScreen(
                    self.screen,
                    int(time.time() - self.start_time),
                    self.enemies_killed,
                    self.game.wave
                )
                return
            player_pos = self.mode7.pos
            self.mode7.update()
            self.game.update(player_pos)
            if hasattr(self, 'weapon_timer') and time.time() > self.weapon_timer:
                self.weapon = WeaponType.REVOLVER
                del self.weapon_timer
            if self.weapon == WeaponType.MINIGUN and self.shooting:
                now = time.time()
                if now - self.minigun_last_shot > 0.1:
                    self.audio.play_shotgun()
                    self.game.shoot_minigun(self.mode7.pos, self.mode7.angle)
                    self.minigun_last_shot = now
            self.clock.tick()
            pg.display.set_caption(f'{self.clock.get_fps():.1f}')
            if self.speed_multiplier != 1.0 and time.time() > self.speed_timer:
                self.speed_multiplier = 1.0
                print("[SPEED] Boost expired")


        elif self.state == GAME_OVER:
            pass



    def draw(self):
        if self.state == MENU:
            self.menu.draw()
        elif self.state == GAME:
            self.mode7.draw()
            self.game.draw(self.screen)
            self.ui_manager.draw_ui()
            self.ui_manager.draw_weapon_ui()
            pg.display.flip()
        elif self.state == GAME_OVER:
            if self.results_screen:
                self.results_screen.update()
                self.results_screen.draw()

    def check_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            if self.state == MENU and event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self.__init__()
                self.state = GAME
                self.switch_to_game()
            elif self.state == GAME_OVER:
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.__init__()
                    self.state = MENU
                    self.results_screen = None
            elif self.state == GAME and self.player.is_dead() and event.type == pg.KEYDOWN and event.key == pg.K_r:
                self.__init__()
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.shooting = True
                direction = np.array([np.cos(self.mode7.angle), np.sin(self.mode7.angle)])
                if self.weapon == WeaponType.REVOLVER:
                    self.audio.play_shotgun()
                    self.game.shoot_revolver(self.mode7.pos, self.mode7.angle)
                elif self.weapon == WeaponType.SHOTGUN:
                    self.audio.play_shotgun()
                    self.game.shoot_shotgun(self.mode7.pos, self.mode7.angle)
                elif self.weapon == WeaponType.MINIGUN:
                    self.audio.play_shotgun()
                    self.game.shoot_minigun(self.mode7.pos, self.mode7.angle)
            elif event.type == pg.KEYUP and event.key == pg.K_SPACE:
                self.shooting = False

    def switch_to_game(self):
        self.audio.play_game_music()

    def apply_powerup(self, weapon_type):
        print(f"[POWERUP] Weapon set to {weapon_type.value}")
        self.weapon = weapon_type
        self.weapon_timer = time.time() + 10
        self.audio.play_powerup()

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()
            pg.display.flip()

if __name__ == "__main__":
    app = App()
    app.run()
