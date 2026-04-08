import types
import unittest
from unittest.mock import patch

import numpy as np
import pygame as pg

from core.mode7 import Mode7
from core.projectile import Projectile
from entities.enemies import Enemy
from entities.player import Player
from managers.game import Game


class DummySound:
    def play(self):
        return None

    def stop(self):
        return None


class ImageStub:
    def __init__(self, size=(16, 16)):
        self.surface = pg.Surface(size, pg.SRCALPHA)

    def convert_alpha(self):
        return self.surface

    def convert(self):
        return self.surface


class FakeKeys(dict):
    def __getitem__(self, key):
        return self.get(key, False)


class DamageTracker:
    def __init__(self):
        self.calls = []

    def take_damage(self, amount):
        self.calls.append(amount)
        return True


class PlayerMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.init()

    @classmethod
    def tearDownClass(cls):
        pg.quit()

    def make_player(self):
        player = Player.__new__(Player)
        player.world_pos = np.array([0.0, 0.0], dtype=np.float32)
        player.velocity = np.zeros(2, dtype=np.float32)
        player.angle = 0.0
        player.base_speed = 0.035
        player.acceleration = 0.22
        player.drag = 0.82
        player.turn_speed = 0.03
        player.speed_multiplier = 1.0
        player.speed_timer = 0
        player.health = 30
        player.max_health = 30
        player.hit_radius = 0.32
        player.graze_radius = 0.72
        player.invulnerability_duration = 0.75
        player.invulnerable_until = 0
        player.hit_sound = DummySound()
        return player

    def make_mode7(self, angle=0.0, alt=1.0, world_pos=(2.0, -1.0)):
        player = types.SimpleNamespace(
            world_pos=np.array(world_pos, dtype=np.float32),
            angle=angle,
            is_invulnerable=lambda: False,
        )
        app = types.SimpleNamespace(player=player)
        mode7 = Mode7.__new__(Mode7)
        mode7.app = app
        mode7.alt = alt
        mode7.camera_pos = player.world_pos.copy()
        mode7.camera_angle = angle
        return mode7, player

    def make_game(self, player_angle=0.0):
        player = types.SimpleNamespace(
            world_pos=np.array([1.0, -2.0], dtype=np.float32),
            angle=player_angle,
            hit_radius=0.32,
            take_damage=lambda amount: True,
        )
        game = types.SimpleNamespace(
            player=player,
            enemies=[],
        )
        game.get_projectile_offset = lambda pos: Game.get_projectile_offset(game, pos)
        return game, player

    def test_rotation_input_does_not_move_player_world_position(self):
        player = self.make_player()
        start_pos = player.world_pos.copy()

        player.movement(FakeKeys({pg.K_a: True}))

        self.assertTrue(np.allclose(player.world_pos, start_pos))
        self.assertNotEqual(player.angle, 0.0)

    def test_player_projectile_spawn_is_stable_across_camera_altitudes(self):
        game, player = self.make_game(player_angle=np.pi / 6)
        low_alt_mode7 = types.SimpleNamespace(alt=0.3)
        high_alt_mode7 = types.SimpleNamespace(alt=4.0)
        game.mode7 = low_alt_mode7

        low_alt_spawn = Game.get_player_projectile_spawn_pos(game)

        game.mode7 = high_alt_mode7
        high_alt_spawn = Game.get_player_projectile_spawn_pos(game)

        self.assertTrue(np.allclose(low_alt_spawn, high_alt_spawn))
        self.assertGreater(np.linalg.norm(low_alt_spawn - player.world_pos), 0.0)

    def test_enemy_collision_is_independent_of_camera_altitude(self):
        player = DamageTracker()
        enemy_bullet = Projectile(
            player_pos=np.array([0.12, 0.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
        )
        enemy = types.SimpleNamespace(
            update=lambda player_pos: None,
            bullets=[enemy_bullet],
            damage=2,
            alive=True,
            pos=np.array([5.0, 5.0], dtype=np.float32),
            contact_radius=0.42,
        )
        game = types.SimpleNamespace(
            projectiles=[],
            enemies=[enemy],
            player=types.SimpleNamespace(
                hit_radius=0.32,
                take_damage=player.take_damage,
                world_pos=np.array([0.0, 0.0], dtype=np.float32),
            ),
            mode7=types.SimpleNamespace(alt=4.0),
            drops=[],
            obstacles=[],
            wave=1,
            app=types.SimpleNamespace(enemies_killed=0),
            explosion_sound=DummySound(),
            level_manager=types.SimpleNamespace(spawn_wave=lambda wave_num: None),
        )

        Game.update(game, np.array([0.0, 0.0], dtype=np.float32))

        self.assertEqual(player.calls, [2])
        self.assertFalse(enemy_bullet.active)

    def test_enemy_hit_detection_no_longer_depends_on_camera_altitude(self):
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 1.0))

        projectile = Projectile(
            player_pos=np.array([0.0, 1.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
        )

        self.assertTrue(enemy.check_collision(projectile))


if __name__ == "__main__":
    unittest.main()
