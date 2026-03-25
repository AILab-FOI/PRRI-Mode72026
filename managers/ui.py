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
        }
        health_bar_sprite = pg.image.load("assets/textures/ui/Steampunk_healthbar_anim.png").convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.scaled_width = int(self.frame_width * 3)
        self.scaled_height = int(self.frame_height * 3)
        self.total_frames = 7
        self.health_bar_frames = []
        for i in range(self.total_frames):
            x = i * self.frame_width
            y = 0
            frame = health_bar_sprite.subsurface(pg.Rect(x, y, self.frame_width, self.frame_height))
            scaled_frame = pg.transform.scale(frame, (self.scaled_width, self.scaled_height))
            self.health_bar_frames.append(scaled_frame)

        self.progression_box = pg.image.load("assets/textures/ui/progression_blank.png").convert_alpha()
        self.progression_box = pg.transform.scale(self.progression_box, (200, 200))

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
        box_x, box_y = 20, 20
        self.screen.blit(self.progression_box, (box_x, box_y))

        font = pg.font.Font("assets/fonts/steampunk-mainmenu.ttf", 20)
        color = (255, 220, 180)

        wave_text = font.render(f"Wave: {self.app.game.wave}", True, color)
        enemy_label = font.render("Enemies:", True, color)
        enemy_number = font.render(str(len(self.app.game.enemies)), True, color)

        text_x = box_x + 70
        wave_y = box_y + 65
        enemy_y = box_y + 100
        enemy_number_y = enemy_y + 25

        self.screen.blit(wave_text, (text_x, wave_y))
        self.screen.blit(enemy_label, (text_x, enemy_y))
        self.screen.blit(enemy_number, (text_x + 25, enemy_number_y))

        self.draw_health()
        self.draw_status_message()

        if self.app.weapon != WeaponType.REVOLVER and time.time() < self.app.weapon_timer:
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
        health_index = 6 - (self.app.player.health // 5)
        if health_index >= 30 or health_index <= 0:
            health_index = 0
        if self.app.player.health <= 4 and self.app.player.health >= 1:
            health_index = 5
        x = self.screen.get_width() - self.scaled_width - 10
        y = 10
        self.screen.blit(self.health_bar_frames[health_index], (x, y))
        if self.app.player.is_invulnerable() and (pg.time.get_ticks() // 90) % 2 == 0:
            pg.draw.rect(
                self.screen,
                (255, 231, 163),
                (x + 22, y + 28, self.scaled_width - 44, self.scaled_height - 60),
                3,
                border_radius=10,
            )

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
