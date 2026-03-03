# platforms.py - Plattformen, Boxen, Stacheln, bewegliche/fallende Plattformen, Pickups, Flagge
import pygame
from settings import (
    TILE_SIZE, MOVING_PLATFORM_SPEED,
    FALLING_PLATFORM_SHAKE_TIME, FALLING_PLATFORM_RESET_TIME
)
import sketch


class Platform:
    """Standard-Plattform / Boden."""
    def __init__(self, x, y, w=None, h=None):
        self.x = x
        self.y = y
        self.w = w or TILE_SIZE
        self.h = h or TILE_SIZE
        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.seed = x * 7 + y * 13

    def update(self):
        pass

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        sketch.draw_platform(surface, sx, sy, self.w, self.h, self.seed)


class Box(Platform):
    """Kiste / Box (wie in Referenzbild)."""
    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        sketch.draw_box(surface, sx, sy, self.w, self.h, self.seed)


class Spike:
    """Stacheln - verursachen Schaden."""
    def __init__(self, x, y, w=None, h=None):
        self.x = x
        self.y = y
        self.w = w or TILE_SIZE
        self.h = h or (TILE_SIZE // 2)
        self.rect = pygame.Rect(x, y + self.h // 2, self.w, self.h // 2)
        self.seed = x * 11 + y * 17

    def update(self):
        pass

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        sketch.draw_spike(surface, sx, sy, self.w, self.h, self.seed)


class MovingPlatform:
    """Bewegliche Plattform."""
    def __init__(self, x, y, w=None, h=None, move_x=0, move_y=0, distance=100):
        self.start_x = x
        self.start_y = y
        self.x = float(x)
        self.y = float(y)
        self.w = w or (TILE_SIZE * 3)
        self.h = h or (TILE_SIZE // 2)
        self.move_x = move_x
        self.move_y = move_y
        self.distance = distance
        self.direction = 1
        self.traveled = 0
        self.speed = MOVING_PLATFORM_SPEED
        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
        self.seed = x * 3 + y * 19
        self.dx = 0.0
        self.dy = 0.0

    def update(self):
        prev_x, prev_y = self.x, self.y

        if self.move_x != 0:
            self.x += self.speed * self.direction * self.move_x
        if self.move_y != 0:
            self.y += self.speed * self.direction * self.move_y

        self.traveled += self.speed
        if self.traveled >= self.distance:
            self.direction *= -1
            self.traveled = 0

        self.dx = self.x - prev_x
        self.dy = self.y - prev_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface, cam):
        sx, sy = cam.apply(int(self.x), int(self.y))
        sketch.draw_moving_platform(surface, sx, sy, self.w, self.h, self.seed)


class FallingPlatform:
    """Fallende Plattform - wackelt, dann fällt."""
    def __init__(self, x, y, w=None, h=None):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = float(y)
        self.w = w or (TILE_SIZE * 2)
        self.h = h or (TILE_SIZE // 2)
        self.rect = pygame.Rect(x, int(self.y), self.w, self.h)
        self.seed = x * 23 + y * 5
        self.triggered = False
        self.shake_timer = 0
        self.falling = False
        self.fall_speed = 0
        self.reset_timer = 0
        self.visible = True

    def trigger(self):
        if not self.triggered and not self.falling:
            self.triggered = True
            self.shake_timer = FALLING_PLATFORM_SHAKE_TIME

    def update(self):
        if self.triggered and not self.falling:
            self.shake_timer -= 1
            if self.shake_timer <= 0:
                self.falling = True
                self.triggered = False

        if self.falling:
            self.fall_speed += 0.5
            self.y += self.fall_speed
            self.rect.y = int(self.y)
            if self.y > self.start_y + 800:
                self.falling = False
                self.visible = False
                self.reset_timer = FALLING_PLATFORM_RESET_TIME

        if not self.visible:
            self.reset_timer -= 1
            if self.reset_timer <= 0:
                self.y = float(self.start_y)
                self.rect.y = self.start_y
                self.fall_speed = 0
                self.visible = True

    def draw(self, surface, cam):
        if not self.visible:
            return
        sx, sy = cam.apply(self.x, int(self.y))
        shake = 2 if self.triggered else 0
        sketch.draw_falling_platform(surface, sx, sy, self.w, self.h, shake, self.seed)


class HeartPickup:
    """Herz-Pickup zur Heilung."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False
        self.seed = x * 31 + y * 37

    def update(self):
        pass

    def draw(self, surface, cam):
        if self.collected:
            return
        sx, sy = cam.apply(self.x, self.y)
        sketch.draw_heart(surface, sx, sy, 16, self.seed)


class Flag:
    """Level-Ende-Flagge."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - 5, y, 30, 60)
        self.seed = x * 41 + y * 43

    def update(self):
        pass

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        sketch.draw_flag(surface, sx, sy, 60, self.seed)
