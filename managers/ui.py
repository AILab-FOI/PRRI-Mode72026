import time

import pygame as pg

from settings import WeaponType


class UIManager:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.powerup_icon = pg.image.load("assets/textures/ui/Steampunk_valve_and_pipe.png").convert_alpha()
        self.powerup_icon = pg.transform.scale(self.powerup_icon, (128, 128))
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
        original_empty = pg.image.load("assets/textures/ui/bez bara.png").convert_alpha()
        self.health_bar_empty = pg.transform.scale(original_empty, (bar_width, bar_height))
        # x offset i širina crvenog dijela bara unutar skalirane slike
        scale = bar_height / orig_h
        self.bar_fill_x = int(248 * scale)
        self.bar_fill_w = int((968 - 248) * scale)

        self.progression_box = pg.image.load("assets/textures/ui/wave_bg.png").convert_alpha()
        self.progression_box = pg.transform.scale(self.progression_box, (500, 110))

        original_full = pg.image.load("assets/textures/ui/steampunk_bar_full.png").convert_alpha()
        scale_factor = 0.2
        self.bar_full = pg.transform.scale(
            original_full,
            (int(original_full.get_width() * scale_factor), int(original_full.get_height() * scale_factor)),
        )

        original_speed = pg.image.load("assets/textures/ui/powerup_bar.png").convert_alpha()
        scale_factor = 0.1
        scaled_speed = pg.transform.scale(
            original_speed,
            (int(original_speed.get_width() * scale_factor), int(original_speed.get_height() * scale_factor)),
        )

        self.bar_speed = pg.transform.rotate(scaled_speed, 90)

        for key in self.weapon_icons:
            self.weapon_icons[key] = pg.transform.scale(self.weapon_icons[key], (80, 80))
        self.weapon_frame = pg.image.load("assets/textures/ui/UI_frame_static.png").convert_alpha()
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

        if self.app.rocket_shots_remaining > 0:
            shots = self.app.rocket_shots_remaining
            font = pg.font.Font("assets/fonts/steampunk-mainmenu.ttf", 24)
            label = font.render("Rockets", True, (255, 160, 30))
            count = font.render(f"x{shots}", True, (255, 200, 60))
            right_margin = 20
            label_x = self.screen.get_width() - label.get_width() - right_margin
            count_x = self.screen.get_width() - count.get_width() - right_margin
            self.screen.blit(label, (label_x, 215))
            self.screen.blit(count, (count_x, 245))

        if self.app.weapon != WeaponType.REVOLVER and self.app.weapon != WeaponType.ROCKET_LAUNCHER and time.time() < self.app.weapon_timer:
            x, y = 85, 600
            total = 10
            remaining = self.app.weapon_timer - time.time()
            percent = max(0, min(1, remaining / total))

            full_width = int(self.bar_full.get_width() * percent)
            if full_width > 0:
                bar_clip = self.bar_full.subsurface((0, 0, full_width, self.bar_full.get_height()))
                self.screen.blit(bar_clip, (x, y))

        if self.app.player.speed_multiplier > 1.0 and time.time() < self.app.player.speed_timer:
            x2, y2 = 1440, 180
            total = 5.4
            remaining = self.app.player.speed_timer - time.time()
            percent = max(0, min(1, remaining / total))

            full_height = int(self.bar_speed.get_height() * percent)
            if full_height > 0:
                bar_clip = self.bar_speed.subsurface(
                    (0, self.bar_speed.get_height() - full_height, self.bar_speed.get_width(), full_height)
                )
                rotated_clip = pg.transform.rotate(bar_clip, 0)
                self.screen.blit(rotated_clip, (x2, y2 + (self.bar_speed.get_height() - full_height)))

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
        padding = 20
        frame_width, frame_height = self.weapon_frame.get_size()
        x = padding
        y = self.screen.get_height() - frame_height - padding
        if x + frame_width > self.screen.get_width():
            x = self.screen.get_width() - frame_width
        if y + frame_height > self.screen.get_height():
            y = self.screen.get_height() - frame_height
        frame_rect = self.weapon_frame.get_rect()
        frame_rect.topleft = (x, y)
        self.screen.blit(self.weapon_frame, frame_rect)
        icon = self.weapon_icons[self.app.weapon]
        icon = pg.transform.scale(icon, (128, 128))
        icon_x = frame_rect.x + (frame_rect.width - icon.get_width()) // 2
        icon_y = frame_rect.y + (frame_rect.height - icon.get_height()) // 2
        self.screen.blit(icon, (icon_x, icon_y))

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
