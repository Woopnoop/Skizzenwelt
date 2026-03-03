# enemies.py - Gegner-Klassen (Walker, Jumper, Flyer)
import pygame
import math
from settings import (
    WALKER_SPEED, JUMPER_SPEED, JUMPER_JUMP_INTERVAL, JUMPER_JUMP_FORCE,
    FLYER_SPEED, FLYER_AMPLITUDE, FLYER_FREQUENCY, GRAVITY, MAX_FALL_SPEED
)
import sketch


class Enemy:
    """Basis-Klasse für Gegner."""
    def __init__(self, x, y, w=30, h=30):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.facing_right = True
        self.frame = 0
        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
        self.seed = int(x * 13 + y * 7)

    def stomp(self):
        """Gegner wird besiegt durch Draufspringen."""
        self.alive = False

    def update(self, platforms):
        pass

    def draw(self, surface, cam):
        pass

    def _apply_gravity(self):
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

    def _collide_platforms(self, platforms):
        """Einfache Plattform-Kollision für Gegner."""
        # Horizontal
        self.rect.x = int(self.x)
        for p in platforms:
            r = p.rect if hasattr(p, 'rect') else p
            if self.rect.colliderect(r):
                if self.vx > 0:
                    self.rect.right = r.left
                    self.x = float(self.rect.x)
                    self.facing_right = False
                    self.vx = -abs(self.vx)
                elif self.vx < 0:
                    self.rect.left = r.right
                    self.x = float(self.rect.x)
                    self.facing_right = True
                    self.vx = abs(self.vx)

        # Vertikal
        self.rect.y = int(self.y)
        on_ground = False
        for p in platforms:
            r = p.rect if hasattr(p, 'rect') else p
            if self.rect.colliderect(r):
                if self.vy > 0:
                    self.rect.bottom = r.top
                    self.y = float(self.rect.y)
                    self.vy = 0
                    on_ground = True
                elif self.vy < 0:
                    self.rect.top = r.bottom
                    self.y = float(self.rect.y)
                    self.vy = 0
        return on_ground

    def _check_edge(self, platforms):
        """Dreht um wenn am Plattformrand."""
        check_x = self.rect.right + 2 if self.vx > 0 else self.rect.left - 2
        check_rect = pygame.Rect(check_x, self.rect.bottom + 2, 4, 4)
        for p in platforms:
            r = p.rect if hasattr(p, 'rect') else p
            if check_rect.colliderect(r):
                return  # Boden vorhanden
        # Kein Boden → umdrehen
        self.vx = -self.vx
        self.facing_right = self.vx > 0


class Walker(Enemy):
    """Patroulliert auf Plattformen hin und her."""
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30)
        self.vx = WALKER_SPEED
        self.facing_right = True

    def update(self, platforms):
        if not self.alive:
            return
        self.frame += 1
        self._apply_gravity()
        self.x += self.vx
        self.y += self.vy
        on_ground = self._collide_platforms(platforms)
        if on_ground:
            self._check_edge(platforms)

    def draw(self, surface, cam):
        if not self.alive:
            return
        sx, sy = cam.apply(int(self.x), int(self.y))
        sketch.draw_walker(surface, sx, sy, self.facing_right, self.frame, self.seed)


class Jumper(Enemy):
    """Wie Walker, springt alle 2 Sekunden."""
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30)
        self.vx = JUMPER_SPEED
        self.facing_right = True
        self.jump_timer = JUMPER_JUMP_INTERVAL

    def update(self, platforms):
        if not self.alive:
            return
        self.frame += 1
        self._apply_gravity()

        self.x += self.vx
        self.y += self.vy

        on_ground = self._collide_platforms(platforms)

        if on_ground:
            self._check_edge(platforms)
            self.jump_timer -= 1
            if self.jump_timer <= 0:
                self.vy = JUMPER_JUMP_FORCE
                self.jump_timer = JUMPER_JUMP_INTERVAL

    def draw(self, surface, cam):
        if not self.alive:
            return
        sx, sy = cam.apply(int(self.x), int(self.y))
        sketch.draw_jumper(surface, sx, sy, self.facing_right, self.frame, self.seed)


class Flyer(Enemy):
    """Fliegt in Sinuswelle, Fledermaus-artig."""
    def __init__(self, x, y, direction=1):
        super().__init__(x, y, 30, 24)
        self.start_y = y
        self.speed = FLYER_SPEED * direction
        self.phase = 0

    def update(self, platforms=None):
        if not self.alive:
            return
        self.frame += 1
        self.phase += FLYER_FREQUENCY
        self.x += self.speed
        self.y = self.start_y + math.sin(self.phase) * FLYER_AMPLITUDE
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.facing_right = self.speed > 0

    def draw(self, surface, cam):
        if not self.alive:
            return
        sx, sy = cam.apply(int(self.x), int(self.y))
        sketch.draw_flyer(surface, sx, sy, self.frame, self.seed)
