# camera.py - Scrollende Kamera mit Lerp
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CAMERA_LERP


class Camera:
    def __init__(self, level_width, level_height):
        self.x = 0.0
        self.y = 0.0
        self.level_width = level_width
        self.level_height = level_height

    def update(self, target_x, target_y):
        """Folgt dem Ziel sanft mit Lerp."""
        goal_x = target_x - SCREEN_WIDTH // 2
        goal_y = target_y - SCREEN_HEIGHT // 2

        self.x += (goal_x - self.x) * CAMERA_LERP
        self.y += (goal_y - self.y) * CAMERA_LERP

        # Grenzen
        self.x = max(0, min(self.x, self.level_width - SCREEN_WIDTH))
        self.y = max(0, min(self.y, self.level_height - SCREEN_HEIGHT))

    def apply(self, x, y):
        """Gibt die Bildschirm-Koordinaten zurück."""
        return x - int(self.x), y - int(self.y)

    def apply_rect(self, rect):
        """Verschiebt ein pygame.Rect in Bildschirm-Koordinaten."""
        import pygame
        return pygame.Rect(rect.x - int(self.x), rect.y - int(self.y), rect.width, rect.height)
