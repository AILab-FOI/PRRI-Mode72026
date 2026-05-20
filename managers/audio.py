import pygame as pg


class AudioManager:
    def __init__(self):
        self.powerup_sound = pg.mixer.Sound("assets/music/Novi sound/PowerUp.wav")
        self.revolver_sound = pg.mixer.Sound("assets/music/Novi sound/PucanjeObicno.wav")
        self.shotgun_sound = pg.mixer.Sound("assets/music/Novi sound/HeavyPucanje.wav")
        self.minigun_sound = pg.mixer.Sound("assets/music/Novi sound/MiniGunPucanje.wav")
        self.health_sound = pg.mixer.Sound("assets/music/HP UP.mp3")
        self.enemy_dead_sound = pg.mixer.Sound("assets/music/Novi sound/EnemyDead.wav")
        self.revolver_reload_sound = pg.mixer.Sound("assets/music/Novi sound/NormalReload.wav")
        self.shotgun_reload_sound = pg.mixer.Sound("assets/music/Novi sound/HeavyReload.wav")
        self.minigun_reload_sound = pg.mixer.Sound("assets/music/Novi sound/MiniGunReload.wav")
        self.move_sound = pg.mixer.Sound("assets/music/Novi sound/KreatanjeZeppelina.wav")
        self._move_channel = None

    def play_menu_music(self):
        pg.mixer.music.load("assets/music/IzmeduLevelaFinal.wav")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)

    def play_game_music(self):
        pg.mixer.music.stop()
        pg.mixer.music.load("assets/music/LEVELIFINAL.wav")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)

    def play_level_music(self, level_idx: int):
        tracks = [
            "assets/music/LEVELIFINAL.wav",
            "assets/music/DrugiLevel.wav",   
            "assets/music/LAVALEVEL.wav",
            "assets/music/BossBattle.wav", 
        ]
        pg.mixer.music.stop()
        pg.mixer.music.load(tracks[level_idx])
        pg.mixer.music.set_volume(1)
        pg.mixer.music.play(-1, 0.0)

    def play_between_levels_music(self, level_idx: int = 0):
        tracks = [
            "assets/music/IzmeduLevelaFINAL.wav",   
            "assets/music/PrijeDrugogLevela.wav",   
            "assets/music/PrijeLava.wav",
            "assets/music/PocetakBossFinal.wav",
            "assets/music/Heaven.wav",
        ]
        pg.mixer.music.stop()
        pg.mixer.music.load(tracks[level_idx])
        pg.mixer.music.set_volume(1)
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

    def play_enemy_dead(self):
        self.enemy_dead_sound.play()

    def play_revolver_reload(self):
        self.revolver_reload_sound.play()

    def play_shotgun_reload(self):
        self.shotgun_reload_sound.play()

    def play_minigun_reload(self):
        self.minigun_reload_sound.play()

    def start_move_sound(self):
        if self._move_channel is None or not self._move_channel.get_busy():
            self._move_channel = self.move_sound.play(-1)

    def stop_move_sound(self):
        if self._move_channel and self._move_channel.get_busy():
            self._move_channel.stop()
            self._move_channel = None
