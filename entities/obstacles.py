import pygame as pg
import numpy as np

class Obstacle:
    def __init__(self,pos,damage=5,collision_radius=0.8,texture_path=None):
        self.pos=np.array(pos,dtype=np.float32)
        self.damage = damage
        self.collision_radius=collision_radius
        self.alive=True

        if texture_path:
            self.texture = pg.image.load(texture_path).convert_alpha()
        else:
            self.texture = self._make_placeholder()

    def _make_placeholder(self):
        surf = pg.Surface((64, 64), pg.SRCALPHA)
      
        pg.draw.rect(surf, (120, 80, 50), (8, 16, 48, 48))
      
        pg.draw.polygon(surf, (80, 50, 30), [(4, 16), (32, 0), (60, 16)])
       
        pg.draw.rect(surf, (200, 220, 255), (22, 28, 20, 16))
      
        pg.draw.rect(surf, (60, 40, 20), (24, 46, 16, 18))
        return surf

    def update(self, player):
       
        if not self.alive:
            return

        distance = np.linalg.norm(self.pos - player.world_pos)
        if distance < self.collision_radius:
            player.take_damage(self.damage)
            self.alive = False
            print(f"[OBSTACLE] Igrač se zabio u zgradu! -{self.damage} HP")

    def draw(self, screen, mode7):
        if not self.alive:
            return

        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
           
            building_scale = int(scale * 1.5)
            if building_scale < 4:
                return
            scaled_texture = pg.transform.scale(self.texture, (building_scale, building_scale))
            screen.blit(
                scaled_texture,
                (int(screen_x) - building_scale // 2, int(screen_y) - building_scale),
            )


class SmallBuilding(Obstacle):


    def __init__(self, pos, texture_path=None):
        super().__init__(pos, damage=3, collision_radius=0.7, texture_path=texture_path)
        if not texture_path:
            self.texture = self._make_small_placeholder()

    def _make_small_placeholder(self):
        surf = pg.Surface((48, 48), pg.SRCALPHA)
        pg.draw.rect(surf, (100, 100, 110), (6, 12, 36, 36))
        pg.draw.polygon(surf, (70, 70, 80), [(2, 12), (24, 0), (46, 12)])
        pg.draw.rect(surf, (200, 220, 255), (14, 20, 10, 10))
        pg.draw.rect(surf, (200, 220, 255), (28, 20, 10, 10))
        return surf


class LargeBuilding(Obstacle):
    

    def __init__(self, pos, texture_path=None):
        super().__init__(pos, damage=8, collision_radius=1.2, texture_path=texture_path)
        if not texture_path:
            self.texture = self._make_large_placeholder()

    def _make_large_placeholder(self):
        surf = pg.Surface((80, 96), pg.SRCALPHA)
        
        pg.draw.rect(surf, (90, 60, 40), (8, 20, 64, 76))
       
        pg.draw.polygon(surf, (60, 40, 25), [(0, 20), (40, 0), (80, 20)])
       
        for row in range(2):
            for col in range(3):
                pg.draw.rect(surf, (200, 220, 255), (16 + col * 20, 30 + row * 24, 12, 14))
        
        pg.draw.rect(surf, (50, 30, 15), (30, 70, 20, 26))
        return surf
