# particles.py - Partikeleffekte (Furz-Wolken, Staub, etc.)
import pygame
import random
import math
from settings import (
    PENCIL_COLOR, PENCIL_LIGHT, PENCIL_VERY_LIGHT,
    DUST_PARTICLE_COUNT, FART_PARTICLE_COUNT, STOMP_PARTICLE_COUNT,
    PARTICLE_LIFETIME
)
import sketch


class Particle:
    def __init__(self, x, y, vx, vy, lifetime, size=3, color=None):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.color = color or PENCIL_LIGHT
        self.alive = True

    def update(self):
        if not self.alive:
            return
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # Leichte Gravitation
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, cam):
        if not self.alive:
            return
        sx, sy = cam.apply(int(self.x), int(self.y))
        alpha = self.lifetime / self.max_lifetime
        size = max(1, int(self.size * alpha))
        sketch.wobbly_circle(surface, self.color, (sx, sy), size, 1, 6, int(self.x + self.y))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_dust(self, x, y):
        """Staub beim Landen."""
        for _ in range(DUST_PARTICLE_COUNT):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-1, 0)
            lifetime = random.randint(10, PARTICLE_LIFETIME)
            self.particles.append(Particle(x, y, vx, vy, lifetime, 2, PENCIL_VERY_LIGHT))

    def emit_fart(self, x, y):
        """Furz-Wolke."""
        for _ in range(FART_PARTICLE_COUNT):
            vx = random.uniform(-2, 2)
            vy = random.uniform(1, 3)
            lifetime = random.randint(15, PARTICLE_LIFETIME + 10)
            size = random.randint(3, 6)
            self.particles.append(Particle(x, y, vx, vy, lifetime, size, PENCIL_LIGHT))

    def emit_stomp(self, x, y):
        """Gegner besiegt."""
        for _ in range(STOMP_PARTICLE_COUNT):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(10, 25)
            self.particles.append(Particle(x, y, vx, vy, lifetime, 3, PENCIL_COLOR))

    def emit_damage(self, x, y):
        """Spieler nimmt Schaden."""
        for _ in range(6):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(15, 30)
            self.particles.append(Particle(x, y, vx, vy, lifetime, 2, (180, 60, 60)))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface, cam):
        for p in self.particles:
            p.draw(surface, cam)
