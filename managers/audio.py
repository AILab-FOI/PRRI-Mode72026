import pygame as pg


class AudioManager:
    def __init__(self):
        self.powerup_sound = pg.mixer.Sound("assets/music/Timer.mp3")
        self.revolver_sound = pg.mixer.Sound("assets/music/Revolver.mp3")
        self.shotgun_sound = pg.mixer.Sound("assets/music/shotgun sound effect.mp3")
        self.minigun_sound = pg.mixer.Sound("assets/music/Minigun zvucni efekt.mp3")
        self.health_sound = pg.mixer.Sound("assets/music/HP UP.mp3")

    def play_menu_music(self):
        pg.mixer.music.load("assets/music/Pixel Pulse.mp3")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)

    def play_game_music(self):
        pg.mixer.music.stop()
        pg.mixer.music.load("assets/music/Pixel Forge.mp3")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)

    def play_powerup(self):
        self.powerup_sound.stop()
        self.powerup_sound.play()

    def stop_powerup(self):
        self.powerup_sound.stop()

    def play_shotgun(self):
        self.shotgun_sound.play()

    def play_revolver(self):
        self.revolver_sound.play()

    def play_minigun(self):
        self.minigun_sound.play()

    def play_health(self):
        self.health_sound.play()
