import pygame as pg
import sys
import time

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
        self.last_shot_time = 0
        self.weapon = WeaponType.REVOLVER
        self.weapon_timer = 0
        self.weapon_cooldowns = {
            WeaponType.REVOLVER: 0.34,
            WeaponType.SHOTGUN: 0.58,
            WeaponType.MINIGUN: 0.09,
        }

        self.start_time = time.time()
        self.enemies_killed = 0
        self.results_screen = None
        self.shooting = False
        self.status_message = ""
        self.status_message_until = 0
        self.audio.play_menu_music()
        
    def apply_speed_boost(self, multiplier, duration=5):
        self.player.apply_speed_boost(multiplier, duration)
        self.show_status_message(f"Speed boost x{multiplier:.1f}", duration=1.6)

    def update(self):
        if self.state == MENU:
            self.menu.update()
        # Reset weapon after timer
        if self.weapon != WeaponType.REVOLVER and self.weapon_timer > 0 and time.time() > self.weapon_timer:
            self.weapon = WeaponType.REVOLVER
            self.weapon_timer = 0
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
            self.player.update(pg.key.get_pressed())
            player_pos = self.player.pos
            self.mode7.update()
            self.game.update(player_pos)
            if self.weapon == WeaponType.MINIGUN and self.shooting:
                self.try_fire_weapon()
            self.clock.tick()
            pg.display.set_caption(f'{self.clock.get_fps():.1f}')


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
            elif self.state == GAME and event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.shooting = True
                self.try_fire_weapon()
            elif self.state == GAME and event.type == pg.KEYUP and event.key == pg.K_SPACE:
                self.shooting = False

    def switch_to_game(self):
        self.audio.play_game_music()

    def apply_powerup(self, weapon_type):
        print(f"[POWERUP] Weapon set to {weapon_type.value}")
        self.weapon = weapon_type
        self.weapon_timer = time.time() + 10
        self.audio.play_powerup()
        self.show_status_message(f"{weapon_type.value.title()} online", duration=1.8)

    def show_status_message(self, message, duration=1.8):
        self.status_message = message
        self.status_message_until = time.time() + duration

    def can_fire_weapon(self):
        cooldown = self.weapon_cooldowns[self.weapon]
        return time.time() - self.last_shot_time >= cooldown

    def try_fire_weapon(self):
        if not self.can_fire_weapon():
            return False

        if self.weapon == WeaponType.REVOLVER:
            self.audio.play_revolver()
            self.game.shoot_revolver(self.player.pos, self.player.angle)
        elif self.weapon == WeaponType.SHOTGUN:
            self.audio.play_shotgun()
            self.game.shoot_shotgun(self.player.pos, self.player.angle)
        elif self.weapon == WeaponType.MINIGUN:
            self.audio.play_minigun()
            self.game.shoot_minigun(self.player.pos, self.player.angle)

        now = time.time()
        self.last_shot_time = now
        return True

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()
            pg.display.flip()

if __name__ == "__main__":
    app = App()
    app.run()
