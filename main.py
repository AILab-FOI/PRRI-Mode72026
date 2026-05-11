import pygame as pg
import sys
import time

from core.mode7 import Mode7
from entities.player import Player
from managers.audio import AudioManager
from managers.game import Game
from managers.ui import UIManager
from screens.cutscene import CutsceneScreen
from screens.menu import Menu, LoadingScreen
from screens.results import ResultsScreen
from settings import CUTSCENE, GAME, GAME_OVER, LOADING, MENU, WIN_RES, WeaponType

class App:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.audio = AudioManager()
        self.mode7 = Mode7(self)
        self.player = Player()
        self.mode7.update()  # warm up numba JIT at startup so loading screen animates freely
        self.game = Game(self.mode7, self.player, self)
        self.menu = Menu(self)
        self.loading_screen = LoadingScreen(self)
        self.cutscene_screen = CutsceneScreen(self)
        self.ui_manager = UIManager(self)
        self.state = MENU
        self.last_shot_time = 0
        self.weapon = WeaponType.REVOLVER
        self.weapon_timer = 0
        self.weapon_cooldowns = {
            WeaponType.REVOLVER: 0.34,
            WeaponType.SHOTGUN: 0.58,
            WeaponType.MINIGUN: 0.09,
            WeaponType.ROCKET_LAUNCHER: 1.5,
        }

        self.start_time = time.time()
        self.enemies_killed = 0
        self.map_kills_start = 0
        self.map_damage_start = 0
        self.results_screen = None
        self.shooting = False
        self.rocket_shots_remaining = 0
        self.status_message = ""
        self.status_message_until = 0
        self.audio.play_menu_music()
        self._pending_action = None
        
    def _restart_game(self):
        self._pending_action = 'restart'

    def _go_to_menu(self):
        self._pending_action = 'menu'

    def apply_speed_boost(self, multiplier, duration=5):
        self.player.apply_speed_boost(multiplier, duration)
        self.show_status_message(f"Speed boost x{multiplier:.1f}", duration=1.6)

    def update(self):
        if self.state == MENU:
            self.menu.update()
        elif self.state == LOADING:
            self.loading_screen.update()
        # Reset weapon after timer
        if self.weapon != WeaponType.REVOLVER and self.weapon_timer > 0 and time.time() > self.weapon_timer:
            if self.weapon == WeaponType.MINIGUN:
                self.audio.play_minigun_reload()
            self.weapon = WeaponType.REVOLVER
            self.weapon_timer = 0
            print("[TIMER] Power-up expired")
        elif self.state == GAME:
            if self.player.is_dead():
                self.audio.stop_powerup()
                self.audio.stop_move_sound()
                self.state = GAME_OVER
                self.results_screen = ResultsScreen(
                    self.screen,
                    int(time.time() - self.start_time),
                    self.enemies_killed,
                    self.game.wave,
                    on_retry=self._restart_game,
                    on_menu=self._go_to_menu,
                )
                return
            keys = pg.key.get_pressed()
            self.player.update(keys)
            if keys[pg.K_w] or keys[pg.K_s]:
                self.audio.start_move_sound()
            else:
                self.audio.stop_move_sound()
            player_pos = self.player.world_pos
            self.mode7.update()
            self.game.update(player_pos)
            if self.weapon == WeaponType.MINIGUN and self.shooting:
                self.try_fire_weapon()
            self.clock.tick(60)
            pg.display.set_caption(f'{self.clock.get_fps():.1f}')


        elif self.state == CUTSCENE:
            pass  # game is paused; input handled in check_event
        elif self.state == GAME_OVER:
            pass



    def draw(self):
        if self.state == MENU:
            self.menu.draw()
        elif self.state == LOADING:
            self.loading_screen.draw()
            pg.display.flip()
        elif self.state == GAME:
            self.mode7.draw()
            self.game.draw(self.screen)
            self.mode7.draw_player_sprite()
            self.ui_manager.draw_ui()
            self.ui_manager.draw_weapon_ui()
            pg.display.flip()
        elif self.state == CUTSCENE:
            self.cutscene_screen.draw()
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
                self.menu.start_game()
            elif self.state == CUTSCENE and event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self.cutscene_screen.continue_game()
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

    def trigger_cutscene(self):
        completed_wave = self.game.wave
        map_num = completed_wave // 3  # wave 3 → 1, wave 6 → 2, wave 9 → 3
        stats = {
            'enemies_killed': self.enemies_killed - self.map_kills_start,
            'damage_taken':   self.player.damage_taken - self.map_damage_start,
            'waves': 3,
        }
        self.map_kills_start = self.enemies_killed
        self.map_damage_start = self.player.damage_taken

        if completed_wave < 9:
            def on_continue():
                self.game.wave += 1
                self.game.level_manager.spawn_wave(self.game.wave)
                self.state = GAME
        else:
            on_continue = self.start_boss

        self.cutscene_screen.setup(map_num, stats, on_continue)
        self.state = CUTSCENE

    def start_boss(self):
        self.game.wave += 1
        self.game.spawn_boss()
        self.state = GAME

    def on_boss_defeated(self):
        self.audio.stop_powerup()
        self.audio.stop_move_sound()
        self.state = GAME_OVER
        self.results_screen = ResultsScreen(
            self.screen,
            int(time.time() - self.start_time),
            self.enemies_killed,
            self.game.wave,
            on_retry=self._restart_game,
            on_menu=self._go_to_menu,
        )

    def apply_powerup(self, weapon_type):
        print(f"[POWERUP] Weapon set to {weapon_type.value}")
        self.weapon = weapon_type
        if weapon_type == WeaponType.ROCKET_LAUNCHER:
            if self.weapon == WeaponType.ROCKET_LAUNCHER:
                self.rocket_shots_remaining += 5
            else:
                self.rocket_shots_remaining = 5
            self.weapon_timer = 0
            self.show_status_message(f"{self.rocket_shots_remaining} Rockets loaded!", duration=1.8)
        else:
            self.weapon_timer = time.time() + 10
            self.show_status_message(f"{weapon_type.value.title()} online", duration=1.8)
        self.audio.play_powerup()

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
            self.game.shoot_revolver(self.player.angle)
            self.audio.play_revolver_reload()
        elif self.weapon == WeaponType.SHOTGUN:
            self.audio.play_shotgun()
            self.game.shoot_shotgun(self.player.angle)
            self.audio.play_shotgun_reload()
        elif self.weapon == WeaponType.MINIGUN:
            self.audio.play_minigun()
            self.game.shoot_minigun(self.player.angle)
        elif self.weapon == WeaponType.ROCKET_LAUNCHER:
            self.audio.play_shotgun()
            self.game.shoot_rocket_launcher(self.player.angle)
            self.audio.play_shotgun_reload()
            self.rocket_shots_remaining -= 1
            if self.rocket_shots_remaining <= 0:
                self.weapon = WeaponType.REVOLVER
                self.weapon_timer = 0
                self.show_status_message("Rockets depleted", duration=1.8)

        now = time.time()
        self.last_shot_time = now
        return True

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()
            pg.display.flip()
            if self._pending_action == 'restart':
                self.__init__()
                self.state = LOADING
                self.loading_screen.start()
            elif self._pending_action == 'menu':
                self.__init__()
                self.state = MENU

if __name__ == "__main__":
    app = App()
    app.run()
