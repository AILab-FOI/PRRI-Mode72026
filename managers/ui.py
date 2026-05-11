import time

import pygame as pg

from settings import WeaponType


class UIManager:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.weapon_icons = {
            WeaponType.REVOLVER: pg.image.load("assets/textures/powerups/revolver_steampunk.png").convert_alpha(),
            WeaponType.SHOTGUN: pg.image.load("assets/textures/powerups/shotgun_steampunk.png").convert_alpha(),
            WeaponType.MINIGUN: pg.image.load("assets/textures/powerups/minigun_steampunk.png").convert_alpha(),
            WeaponType.ROCKET_LAUNCHER: pg.image.load("assets/textures/powerups/Speed_powerup.png").convert_alpha(),
        }
        bar_height = 110
        original_full = pg.image.load("assets/textures/ui/hud_bez_pozadine.png").convert_alpha()
        orig_w, orig_h = original_full.get_size()
        aspect = orig_w / orig_h
        bar_width = int(bar_height * aspect)
        self.health_bar_full = pg.transform.scale(original_full, (bar_width, bar_height))
        original_empty = pg.image.load("assets/textures/ui/hud_bez.png").convert_alpha()
        self.health_bar_empty = pg.transform.scale(original_empty, (bar_width, bar_height))
        # x offset i širina crvenog dijela bara unutar skalirane slike
        scale = bar_height / orig_h
        self.bar_fill_x = int(248 * scale)
        self.bar_fill_w = int((968 - 248) * scale)

        self.progression_box = pg.image.load("assets/textures/ui/wave_bg.png").convert_alpha()
        self.progression_box = pg.transform.scale(self.progression_box, (500, 110))

        orig_weapon_full = pg.image.load("assets/textures/ui/weapon_bar_pun.png").convert_alpha()
        orig_weapon_empty = pg.image.load("assets/textures/ui/weapon_bar_prazan.png").convert_alpha()
        # originalna slika 666x375, vidljivi dio x=28 do x=644 (616px širok)
        # skaliramo tako da tih 616px bude točno 300px (širina weapon framea)
        scale_wb = 250 / 616
        weapon_bar_w = int(666 * scale_wb)
        weapon_bar_h = int(375 * scale_wb)
        self.bar_full = pg.transform.scale(orig_weapon_full, (weapon_bar_w, weapon_bar_h))
        self.bar_empty = pg.transform.scale(orig_weapon_empty, (weapon_bar_w, weapon_bar_h))
        self.bar_fill_x_wb = int(173 * scale_wb)
        self.bar_fill_w_wb = int((547 - 173) * scale_wb)
        self.weapon_bar_x_offset = int(28 * scale_wb)
        self.weapon_bar_w = weapon_bar_w
        self.weapon_bar_h = weapon_bar_h

        orig_speed_full = pg.image.load("assets/textures/ui/powerup_pun.png").convert_alpha()
        orig_speed_empty = pg.image.load("assets/textures/ui/powerup_prazan.png").convert_alpha()
        orig_speed_h = orig_speed_full.get_height()
        orig_speed_w = orig_speed_full.get_width()
        speed_h = 280
        speed_w = int(orig_speed_w * speed_h / orig_speed_h)
        self.bar_speed_full = pg.transform.scale(orig_speed_full, (speed_w, speed_h))
        self.bar_speed_empty = pg.transform.scale(orig_speed_empty, (speed_w, speed_h))
        scale = speed_h / orig_speed_h
        self.bar_speed_fill_y = int(132 * scale)
        self.bar_speed_fill_h = int((500 - 132) * scale)

        for key in self.weapon_icons:
            self.weapon_icons[key] = pg.transform.scale(self.weapon_icons[key], (80, 80))
        self.weapon_frame = pg.image.load("assets/textures/ui/frame.png").convert_alpha()
        self.weapon_frame = pg.transform.scale(self.weapon_frame, (300, 200))

    def draw_ui(self):
        box_x, box_y = 40, 40
        self.screen.blit(self.progression_box, (box_x, box_y))

        font = pg.font.Font("assets/fonts/steampunk-mainmenu.ttf", 22)
        color = (255, 220, 180)

        wave_text = font.render(f"Wave: {self.app.game.wave}", True, color)
        enemy_text = font.render(f"Enemies: {len(self.app.game.enemies)}", True, color)

        # tamni bar unutar slike: x od 113 do 424, sredina y 55
        bar_mid_x = box_x + (113 + 424) // 2
        bar_mid_y = box_y + 55

        gap = 20
        total_w = wave_text.get_width() + gap + enemy_text.get_width()

        wave_x = bar_mid_x - total_w // 2
        wave_y = bar_mid_y - wave_text.get_height() // 2

        enemy_x = wave_x + wave_text.get_width() + gap
        enemy_y = bar_mid_y - enemy_text.get_height() // 2

        self.screen.blit(wave_text, (wave_x, wave_y))
        self.screen.blit(enemy_text, (enemy_x, enemy_y))

        self.draw_health()
        self.draw_status_message()



        if self.app.player.speed_multiplier > 1.0 and time.time() < self.app.player.speed_timer:
            bw = self.bar_speed_full.get_width()
            bh = self.bar_speed_full.get_height()
            x2 = self.screen.get_width() - bw - 40
            y2 = 180
            total = 5.4
            remaining = self.app.player.speed_timer - time.time()
            percent = max(0, min(1, remaining / total))

            fill_h = int(self.bar_speed_fill_h * percent)
            if fill_h > 0:
                self.screen.blit(self.bar_speed_empty, (x2, y2))
                top = self.bar_speed_fill_y + (self.bar_speed_fill_h - fill_h)
                clip = self.bar_speed_full.subsurface((0, top, bw, fill_h))
                self.screen.blit(clip, (x2, y2 + top))

    def draw_health(self):
        bar_w = self.health_bar_full.get_width()
        bar_h = self.health_bar_full.get_height()
        padding = 40
        x = self.screen.get_width() - bar_w - padding
        y = padding

        # prazni okvir uvijek vidljiv
        self.screen.blit(self.health_bar_empty, (x, y))

        # reži samo crveni dio bara po 18 segmenata, max_health = 30
        segments = 18
        current_segments = round(self.app.player.health / self.app.player.max_health * segments)
        if self.app.player.health > 0:
            current_segments = max(1, current_segments)
        fill_w = int(self.bar_fill_w * current_segments / segments)
        if fill_w > 0:
            clip = self.health_bar_full.subsurface(pg.Rect(self.bar_fill_x, 0, fill_w, bar_h))
            self.screen.blit(clip, (x + self.bar_fill_x, y))

        if self.app.player.is_invulnerable() and (pg.time.get_ticks() // 90) % 2 == 0:
            pg.draw.rect(self.screen, (255, 231, 163), (x, y, bar_w, bar_h), 3, border_radius=6)

    def draw_weapon_ui(self):
        # pozicija weapon framea (300x200) u donjem lijevom kutu
        fw, fh = 300, 200
        padding = 20
        fx = padding
        fy = self.screen.get_height() - fh - padding

        # weapon cooldown bar — tik iznad weapon framea
        bar_active = (
            self.app.weapon != WeaponType.REVOLVER
            and self.app.weapon != WeaponType.ROCKET_LAUNCHER
            and time.time() < self.app.weapon_timer
        )
        bx = fx + (fw - 250) // 2 - self.weapon_bar_x_offset
        by = fy - self.weapon_bar_h + 50

        if bar_active:
            total = 10
            remaining = self.app.weapon_timer - time.time()
            percent = max(0, min(1, remaining / total))
            fill_w = int(self.bar_fill_w_wb * percent)
            if fill_w > 0:
                self.screen.blit(self.bar_empty, (bx, by))
                clip = self.bar_full.subsurface((self.bar_fill_x_wb, 0, fill_w, self.weapon_bar_h))
                self.screen.blit(clip, (bx + self.bar_fill_x_wb, by))

        # rockets counter — iznad bara ako je aktivan, inače iznad weapon framea
        if self.app.rocket_shots_remaining > 0:
            font = pg.font.Font("assets/fonts/steampunk-mainmenu.ttf", 24)
            text = f"Rockets  x{self.app.rocket_shots_remaining}"
            shadow = font.render(text, True, (30, 18, 8))
            label = font.render(text, True, (220, 210, 180))
            lx = fx + (fw - label.get_width()) // 2
            ly = (by - label.get_height() - 2) if bar_active else (fy - label.get_height() - 2)
            self.screen.blit(shadow, (lx + 2, ly + 2))
            self.screen.blit(label, (lx, ly))

        self.screen.blit(self.weapon_frame, (fx, fy))
        icon = self.weapon_icons[self.app.weapon]
        icon = pg.transform.scale(icon, (128, 128))
        self.screen.blit(icon, (fx + (fw - 128) // 2, fy + (fh - 128) // 2))

    def draw_status_message(self):
        if time.time() >= self.app.status_message_until or not self.app.status_message:
            return

        font = pg.font.Font("assets/fonts/steampunk-mainmenu.ttf", 24)
        text = font.render(self.app.status_message, True, (255, 230, 190))
        padding_x, padding_y = 30, 16
        box = pg.Rect(0, 0, text.get_width() + padding_x * 2, text.get_height() + padding_y * 2)
        box.center = (self.screen.get_width() // 2, self.screen.get_height() - 90)
        pg.draw.rect(self.screen, (36, 24, 14), box, border_radius=14)
        pg.draw.rect(self.screen, (173, 130, 78), box, 2, border_radius=14)
        self.screen.blit(text, (box.x + padding_x, box.y + padding_y))
