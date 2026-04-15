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
from settings import AIR_LANE_REFERENCE_HEIGHT


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
        player.height_hit_radius = 0.12
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
        mode7.reference_flight_height = 1.0
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

    def test_player_altitude_is_capped_at_spawn_height(self):
        player = types.SimpleNamespace(
            world_pos=np.array([0.0, 0.0], dtype=np.float32),
            angle=0.0,
            is_invulnerable=lambda: False,
        )
        app = types.SimpleNamespace(player=player)
        mode7 = Mode7.__new__(Mode7)
        mode7.app = app
        mode7.alt = AIR_LANE_REFERENCE_HEIGHT
        mode7.camera_pos = player.world_pos.copy()
        mode7.camera_angle = 0.0
        mode7.floor_array = np.zeros((2, 2, 3), dtype=np.uint8)
        mode7.ceil_array = np.zeros((2, 2, 3), dtype=np.uint8)
        mode7.screen_array = np.zeros((10, 10, 3), dtype=np.uint8)
        mode7.tex_size = (2, 2)
        mode7.map_mode = 1
        mode7.map_world_size = 24.0
        mode7.render_frame = lambda *args, **kwargs: mode7.screen_array

        with patch("pygame.key.get_pressed", return_value=FakeKeys({pg.K_e: True})):
            Mode7.update(mode7)

        self.assertEqual(mode7.alt, AIR_LANE_REFERENCE_HEIGHT)

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
            height=0.45,
        )
        enemy = types.SimpleNamespace(
            update=lambda player_pos, player_height: None,
            bullets=[enemy_bullet],
            damage=2,
            alive=True,
            pos=np.array([5.0, 5.0], dtype=np.float32),
            contact_radius=0.42,
            height=0.45,
            height_hit_radius=0.14,
        )
        game = types.SimpleNamespace(
            projectiles=[],
            enemies=[enemy],
            player=types.SimpleNamespace(
                hit_radius=0.32,
                height_hit_radius=0.12,
                take_damage=player.take_damage,
                world_pos=np.array([0.0, 0.0], dtype=np.float32),
            ),
            mode7=types.SimpleNamespace(alt=0.45),
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

    def test_enemy_bullet_misses_when_height_band_is_different(self):
        player = DamageTracker()
        enemy_bullet = Projectile(
            player_pos=np.array([0.12, 0.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
            height=1.0,
        )
        enemy = types.SimpleNamespace(
            update=lambda player_pos, player_height: None,
            bullets=[enemy_bullet],
            damage=2,
            alive=True,
            pos=np.array([5.0, 5.0], dtype=np.float32),
            contact_radius=0.42,
            height=1.0,
            height_hit_radius=0.14,
        )
        game = types.SimpleNamespace(
            projectiles=[],
            enemies=[enemy],
            player=types.SimpleNamespace(
                hit_radius=0.32,
                height_hit_radius=0.12,
                take_damage=player.take_damage,
                world_pos=np.array([0.0, 0.0], dtype=np.float32),
            ),
            mode7=types.SimpleNamespace(alt=0.35),
            drops=[],
            obstacles=[],
            wave=1,
            app=types.SimpleNamespace(enemies_killed=0),
            explosion_sound=DummySound(),
            level_manager=types.SimpleNamespace(spawn_wave=lambda wave_num: None),
        )

        Game.update(game, np.array([0.0, 0.0], dtype=np.float32))

        self.assertEqual(player.calls, [])
        self.assertTrue(enemy_bullet.active)

    def test_enemy_hit_detection_no_longer_depends_on_camera_altitude(self):
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 1.0), height=1.0)

        projectile = Projectile(
            player_pos=np.array([0.0, 1.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
            height=1.0,
        )

        self.assertTrue(enemy.check_collision(projectile))

    def test_enemy_hit_detection_respects_height_band(self):
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 1.0), height=1.0)

        projectile = Projectile(
            player_pos=np.array([0.0, 1.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
            height=0.35,
        )

        self.assertFalse(enemy.check_collision(projectile))

    def test_enemy_can_climb_above_cruise_height_to_match_player(self):
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 0.0), height=1.0)

        for _ in range(10):
            enemy.update(np.array([0.0, 2.0], dtype=np.float32), player_height=6.0)

        self.assertGreater(enemy.height, 1.0)
        self.assertLess(enemy.height, 2.0)

        for _ in range(100):
            enemy.update(np.array([0.0, 2.0], dtype=np.float32), player_height=6.0)

        self.assertGreater(enemy.height, 5.5)

    def test_enemy_descends_toward_player_until_min_height_floor(self):
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 0.0), height=1.0)

        for _ in range(9):
            enemy.update(np.array([0.0, 2.0], dtype=np.float32), player_height=0.1)

        # After partial descent: moved but hasn't clamped to floor yet
        self.assertLess(enemy.height, 1.0)
        self.assertGreater(enemy.height, enemy.min_height)

        for _ in range(100):
            enemy.update(np.array([0.0, 2.0], dtype=np.float32), player_height=0.1)

        self.assertLess(enemy.height, 0.5)
        self.assertGreaterEqual(enemy.height, enemy.min_height)

    def test_projection_uses_current_player_altitude_for_height_offset(self):
        mode7, _player = self.make_mode7(angle=0.0, alt=6.0, world_pos=(0.0, 0.0))

        _x_low, y_low, _scale_low = mode7.project(np.array([0.0, 5.0], dtype=np.float32), world_height=1.0)
        _x_high, y_high, _scale_high = mode7.project(np.array([0.0, 5.0], dtype=np.float32), world_height=6.0)

        # Higher world_height → above player → smaller screen_y (higher on screen)
        self.assertLess(y_high, y_low)

    def test_projection_absolute_position_shifts_with_player_altitude(self):
        """Enemy at fixed world_height must appear at different screen_y as player altitude changes."""
        from settings import HALF_HEIGHT as SCREEN_HALF_H
        world_pos = np.array([0.0, 5.0], dtype=np.float32)

        mode7_low, _ = self.make_mode7(angle=0.0, alt=1.0, world_pos=(0.0, 0.0))
        mode7_high, _ = self.make_mode7(angle=0.0, alt=6.0, world_pos=(0.0, 0.0))

        _, y_from_low, _ = mode7_low.project(world_pos, world_height=3.0)
        _, y_from_high, _ = mode7_high.project(world_pos, world_height=3.0)

        # Player at 1.0, enemy at 3.0 → enemy is above player → above horizon
        self.assertLess(y_from_low, SCREEN_HALF_H)
        # Player at 6.0, enemy at 3.0 → enemy is below player → below horizon
        self.assertGreater(y_from_high, SCREEN_HALF_H)
        # The two positions must differ
        self.assertNotEqual(y_from_low, y_from_high)

    def test_enemy_explicit_spawn_height_not_clamped_to_reference(self):
        """Enemy created with height=5.0 must actually start near that height, not clamped to 1.0."""
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 1.0), height=5.0)

        self.assertGreater(enemy.height, 4.0)
        self.assertGreater(enemy.cruise_height, 4.0)

    def test_player_at_min_altitude_can_hit_enemy_at_min_height(self):
        """Gap between PLAYER_MIN_ALTITUDE (0.05) and ENEMY_MIN_HEIGHT (0.18) must be within hit threshold."""
        from settings import PLAYER_MIN_ALTITUDE, ENEMY_MIN_HEIGHT
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 0.0), height=ENEMY_MIN_HEIGHT)

        projectile = Projectile(
            player_pos=np.array([0.0, 0.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
            height=PLAYER_MIN_ALTITUDE,
        )

        self.assertTrue(enemy.check_collision(projectile),
                        f"Player at min altitude ({PLAYER_MIN_ALTITUDE}) must be able to hit "
                        f"enemy at min height ({ENEMY_MIN_HEIGHT})")

    def test_player_at_max_altitude_can_hit_enemy_converging_from_below(self):
        """At max altitude a shot must land on an enemy that is close but not yet fully ascended."""
        from settings import PLAYER_MAX_ALTITUDE, ENEMY_HEIGHT_HIT_RADIUS, PROJECTILE_HEIGHT_HIT_RADIUS
        # Worst-case: enemy is exactly one threshold away from player max
        threshold = ENEMY_HEIGHT_HIT_RADIUS + PROJECTILE_HEIGHT_HIT_RADIUS
        enemy_height = PLAYER_MAX_ALTITUDE - threshold + 0.01  # just inside the band

        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 0.0), height=enemy_height)

        projectile = Projectile(
            player_pos=np.array([0.0, 0.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
            height=PLAYER_MAX_ALTITUDE,
        )

        self.assertTrue(enemy.check_collision(projectile),
                        f"Player at max altitude ({PLAYER_MAX_ALTITUDE}) must hit enemy "
                        f"converging from {enemy_height:.3f}")

    def test_enemy_spawned_at_player_altitude_is_immediately_hittable(self):
        """Enemy created at player altitude must be hittable with zero delay."""
        player_alt = 0.6
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((0.0, 0.0), height=player_alt)

        projectile = Projectile(
            player_pos=np.array([0.0, 0.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
            height=player_alt,
        )

        self.assertTrue(enemy.check_collision(projectile))

    def test_enemy_from_far_spawn_still_matches_initial_player_height(self):
        with patch("pygame.image.load", return_value=ImageStub()):
            enemy = Enemy((10.0, 10.0), height=0.35)

        for _ in range(20):
            enemy.update(np.array([0.0, 0.0], dtype=np.float32), player_height=AIR_LANE_REFERENCE_HEIGHT)

        self.assertGreater(enemy.height, 0.35)

    def test_player_projectile_height_is_fixed_at_fire_time(self):
        game, _player = self.make_game(player_angle=0.0)
        game.projectiles = []
        game.mode7 = types.SimpleNamespace(alt=0.35)

        Game.shoot_revolver(game, 0.0)
        projectile = game.projectiles[0]
        game.mode7.alt = 6.0

        self.assertAlmostEqual(projectile.height, 0.35)

    def test_game_updates_enemy_before_player_projectile_collision(self):
        projectile = Projectile(
            player_pos=np.array([0.0, 0.0], dtype=np.float32),
            player_angle=np.array([0.0, 0.0], dtype=np.float32),
            speed=0.0,
            hit_radius=0.18,
            height=6.0,
        )

        enemy = types.SimpleNamespace(
            pos=np.array([0.0, 0.0], dtype=np.float32),
            bullets=[],
            damage=1,
            alive=True,
            contact_radius=0.42,
            height=1.0,
            height_hit_radius=0.14,
        )

        def update_enemy(player_pos, player_height):
            enemy.height = player_height

        def check_collision(proj):
            return abs(enemy.height - proj.height) < 0.3

        enemy.update = update_enemy
        enemy.check_collision = check_collision

        game = types.SimpleNamespace(
            projectiles=[projectile],
            enemies=[enemy],
            player=types.SimpleNamespace(
                hit_radius=0.32,
                height_hit_radius=0.12,
                take_damage=lambda amount: True,
                world_pos=np.array([0.0, 0.0], dtype=np.float32),
            ),
            mode7=types.SimpleNamespace(alt=6.0),
            drops=[],
            obstacles=[],
            wave=1,
            app=types.SimpleNamespace(
                enemies_killed=0,
                audio=types.SimpleNamespace(play_enemy_dead=lambda: None),
            ),
            explosion_sound=DummySound(),
            level_manager=types.SimpleNamespace(spawn_wave=lambda wave_num: None),
        )

        Game.update(game, np.array([0.0, 0.0], dtype=np.float32))

        self.assertFalse(projectile.active)


if __name__ == "__main__":
    unittest.main()
