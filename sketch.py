# sketch.py - Bleistift-Rendering-System
import pygame
import random
import math
from settings import (
    SKETCH_SEGMENTS, SKETCH_WOBBLE, SKETCH_REDRAW_INTERVAL, LINE_WIDTH,
    PAPER_COLOR, PAPER_LINE_COLOR, PENCIL_COLOR, PENCIL_LIGHT,
    PENCIL_VERY_LIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, HEART_COLOR
)

# Globaler Frame-Zähler für Neuzeichnung
_frame_counter = 0
_wobble_seed = 0


def tick():
    """Muss jeden Frame aufgerufen werden."""
    global _frame_counter, _wobble_seed
    _frame_counter += 1
    if _frame_counter % SKETCH_REDRAW_INTERVAL == 0:
        _wobble_seed = random.randint(0, 100000)


def _wobble_offset(index, seed=None):
    """Berechnet eine pseudo-zufällige Verschiebung für einen Punkt."""
    s = seed if seed is not None else _wobble_seed
    random.seed(s + index * 7)
    ox = random.uniform(-SKETCH_WOBBLE, SKETCH_WOBBLE)
    oy = random.uniform(-SKETCH_WOBBLE, SKETCH_WOBBLE)
    random.seed()  # Reset
    return ox, oy


def wobbly_line(surface, color, start, end, width=LINE_WIDTH, seed_offset=0):
    """Zeichnet eine wackelige Bleistift-Linie."""
    points = []
    for i in range(SKETCH_SEGMENTS + 1):
        t = i / SKETCH_SEGMENTS
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        if 0 < i < SKETCH_SEGMENTS:
            ox, oy = _wobble_offset(i + seed_offset)
            x += ox
            y += oy
        points.append((x, y))
    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, width)


def wobbly_rect(surface, color, rect, width=LINE_WIDTH, seed_offset=0):
    """Zeichnet ein wackeliges Rechteck."""
    x, y, w, h = rect
    wobbly_line(surface, color, (x, y), (x + w, y), width, seed_offset)
    wobbly_line(surface, color, (x + w, y), (x + w, y + h), width, seed_offset + 100)
    wobbly_line(surface, color, (x + w, y + h), (x, y + h), width, seed_offset + 200)
    wobbly_line(surface, color, (x, y + h), (x, y), width, seed_offset + 300)


def wobbly_circle(surface, color, center, radius, width=LINE_WIDTH, segments=16, seed_offset=0):
    """Zeichnet einen wackeligen Kreis."""
    points = []
    for i in range(segments + 1):
        angle = (i / segments) * math.pi * 2
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius
        ox, oy = _wobble_offset(i + seed_offset)
        x += ox * 0.7
        y += oy * 0.7
        points.append((x, y))
    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, width)


def wobbly_polygon(surface, color, points, width=LINE_WIDTH, seed_offset=0):
    """Zeichnet ein wackeliges Polygon (geschlossen)."""
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        wobbly_line(surface, color, start, end, width, seed_offset + i * 100)


def wobbly_triangle(surface, color, p1, p2, p3, width=LINE_WIDTH, seed_offset=0):
    """Zeichnet ein wackeliges Dreieck."""
    wobbly_polygon(surface, color, [p1, p2, p3], width, seed_offset)


def draw_paper_background(surface):
    """Zeichnet den Papier-Hintergrund mit Linien und Textur."""
    surface.fill(PAPER_COLOR)

    # Horizontale Linien (wie Schreibpapier)
    for y in range(40, SCREEN_HEIGHT, 32):
        pygame.draw.line(surface, PAPER_LINE_COLOR, (0, y), (SCREEN_WIDTH, y), 1)

    # Rand links (roter Rand wie Schulheft)
    pygame.draw.line(surface, (200, 160, 160), (60, 0), (60, SCREEN_HEIGHT), 1)

    # Leichte Körnung
    random.seed(_wobble_seed // 6)
    for _ in range(80):
        gx = random.randint(0, SCREEN_WIDTH)
        gy = random.randint(0, SCREEN_HEIGHT)
        gc = random.randint(200, 235)
        pygame.draw.circle(surface, (gc, gc - 5, gc - 15), (gx, gy), 1)
    random.seed()


def draw_player(surface, x, y, facing_right=True, frame=0):
    """Zeichnet die Spielerfigur prozedural im Bleistift-Stil.
    Spitzhut, Kopf, Mantel, Beine - wie in der Referenzskizze.
    """
    cx = x + 12  # Mittelpunkt
    flip = 1 if facing_right else -1
    seed = _wobble_seed + int(x) + int(y)

    # Animation: leichtes Wippen
    bob = math.sin(frame * 0.15) * 1.5

    # Spitzhut (Dreieck)
    hat_top = (cx + flip * 2, y - 4 + bob)
    hat_left = (cx - 7, y + 8 + bob)
    hat_right = (cx + 7, y + 8 + bob)
    wobbly_triangle(surface, PENCIL_COLOR, hat_top, hat_left, hat_right, 2, seed)

    # Kopf (kleiner Kreis)
    head_center = (cx, y + 14 + bob)
    wobbly_circle(surface, PENCIL_COLOR, head_center, 6, 2, 12, seed + 50)

    # Augen
    eye_x = cx + flip * 2
    pygame.draw.circle(surface, PENCIL_COLOR, (int(eye_x), int(y + 13 + bob)), 1)

    # Mantel / Körper (Trapez)
    body_top_l = (cx - 6, y + 20 + bob)
    body_top_r = (cx + 6, y + 20 + bob)
    body_bot_l = (cx - 9, y + 34 + bob)
    body_bot_r = (cx + 9, y + 34 + bob)
    wobbly_polygon(surface, PENCIL_COLOR, [body_top_l, body_top_r, body_bot_r, body_bot_l], 2, seed + 100)

    # Beine
    walk_cycle = math.sin(frame * 0.3) * 4
    leg_y = y + 34 + bob
    # Linkes Bein
    wobbly_line(surface, PENCIL_COLOR,
                (cx - 4, leg_y),
                (cx - 6 - walk_cycle, y + 44 + bob), 2, seed + 200)
    # Rechtes Bein
    wobbly_line(surface, PENCIL_COLOR,
                (cx + 4, leg_y),
                (cx + 6 + walk_cycle, y + 44 + bob), 2, seed + 250)


def draw_player_hanging(surface, x, y, facing_right=True):
    """Zeichnet den Spieler beim Kanten-Festhalten."""
    cx = x + 12
    flip = 1 if facing_right else -1
    seed = _wobble_seed + int(x)

    # Hut
    hat_top = (cx + flip * 2, y - 2)
    hat_left = (cx - 6, y + 8)
    hat_right = (cx + 6, y + 8)
    wobbly_triangle(surface, PENCIL_COLOR, hat_top, hat_left, hat_right, 2, seed)

    # Kopf
    wobbly_circle(surface, PENCIL_COLOR, (cx, y + 14), 6, 2, 12, seed + 50)

    # Arm hoch (greift Kante)
    arm_x = cx + flip * 10
    wobbly_line(surface, PENCIL_COLOR, (cx + flip * 6, y + 20), (arm_x, y + 4), 2, seed + 80)

    # Körper
    body_top_l = (cx - 5, y + 20)
    body_top_r = (cx + 5, y + 20)
    body_bot_l = (cx - 7, y + 34)
    body_bot_r = (cx + 7, y + 34)
    wobbly_polygon(surface, PENCIL_COLOR, [body_top_l, body_top_r, body_bot_r, body_bot_l], 2, seed + 100)

    # Beine hängen
    wobbly_line(surface, PENCIL_COLOR, (cx - 3, y + 34), (cx - 5, y + 44), 2, seed + 200)
    wobbly_line(surface, PENCIL_COLOR, (cx + 3, y + 34), (cx + 5, y + 44), 2, seed + 250)


def draw_box(surface, x, y, w, h, seed_offset=0):
    """Zeichnet eine Kiste im Bleistift-Stil."""
    wobbly_rect(surface, PENCIL_COLOR, (x, y, w, h), 2, seed_offset)
    # Kreuz-Linien in der Kiste
    wobbly_line(surface, PENCIL_LIGHT, (x + 4, y + 4), (x + w - 4, y + h - 4), 1, seed_offset + 400)
    wobbly_line(surface, PENCIL_LIGHT, (x + w - 4, y + 4), (x + 4, y + h - 4), 1, seed_offset + 500)


def draw_platform(surface, x, y, w, h, seed_offset=0):
    """Zeichnet eine Standard-Plattform."""
    wobbly_rect(surface, PENCIL_COLOR, (x, y, w, h), 2, seed_offset)
    # Horizontale Linien für Textur
    for ly in range(y + 8, y + h, 8):
        wobbly_line(surface, PENCIL_VERY_LIGHT, (x + 3, ly), (x + w - 3, ly), 1, seed_offset + ly)


def draw_spike(surface, x, y, w, h, seed_offset=0):
    """Zeichnet Stacheln."""
    num_spikes = max(1, w // 10)
    spike_w = w / num_spikes
    for i in range(num_spikes):
        sx = x + i * spike_w
        p1 = (sx, y + h)
        p2 = (sx + spike_w, y + h)
        p3 = (sx + spike_w / 2, y)
        wobbly_triangle(surface, PENCIL_COLOR, p1, p2, p3, 2, seed_offset + i * 50)


def draw_heart(surface, x, y, size=12, seed_offset=0):
    """Zeichnet ein Herz-Symbol."""
    cx, cy = x + size // 2, y + size // 2
    # Zwei obere Kreise
    r = size // 3
    wobbly_circle(surface, HEART_COLOR, (cx - r + 1, cy - 2), r, 2, 10, seed_offset)
    wobbly_circle(surface, HEART_COLOR, (cx + r - 1, cy - 2), r, 2, 10, seed_offset + 30)
    # Untere Spitze
    wobbly_line(surface, HEART_COLOR, (cx - size // 2, cy), (cx, cy + size // 2), 2, seed_offset + 60)
    wobbly_line(surface, HEART_COLOR, (cx + size // 2, cy), (cx, cy + size // 2), 2, seed_offset + 90)


def draw_flag(surface, x, y, h=60, seed_offset=0):
    """Zeichnet eine Level-Ende-Flagge."""
    # Mast
    wobbly_line(surface, PENCIL_COLOR, (x, y), (x, y + h), 2, seed_offset)
    # Flagge (Dreieck)
    flag_color = (180, 60, 60)
    wobbly_triangle(surface, flag_color,
                    (x, y), (x + 25, y + 10), (x, y + 20),
                    2, seed_offset + 100)
    # Basis
    wobbly_line(surface, PENCIL_COLOR, (x - 8, y + h), (x + 8, y + h), 2, seed_offset + 200)


def draw_walker(surface, x, y, facing_right=True, frame=0, seed_offset=0):
    """Zeichnet einen Walker-Gegner (kleines Wesen mit Beinen)."""
    cx = x + 15
    flip = 1 if facing_right else -1
    bob = math.sin(frame * 0.2) * 1

    # Körper (Oval)
    wobbly_circle(surface, PENCIL_COLOR, (cx, int(y + 14 + bob)), 10, 2, 12, seed_offset)
    # Augen (böse)
    eye_x = cx + flip * 3
    pygame.draw.circle(surface, PENCIL_COLOR, (int(eye_x - 2), int(y + 12 + bob)), 2)
    pygame.draw.circle(surface, PENCIL_COLOR, (int(eye_x + 4), int(y + 12 + bob)), 2)
    # Böse Augenbrauen
    wobbly_line(surface, PENCIL_COLOR,
                (eye_x - 4, y + 9 + bob), (eye_x, y + 11 + bob), 1, seed_offset + 50)
    wobbly_line(surface, PENCIL_COLOR,
                (eye_x + 6, y + 9 + bob), (eye_x + 2, y + 11 + bob), 1, seed_offset + 60)

    # Beine
    walk = math.sin(frame * 0.3) * 3
    wobbly_line(surface, PENCIL_COLOR,
                (cx - 5, y + 24 + bob), (cx - 7 - walk, y + 30 + bob), 2, seed_offset + 100)
    wobbly_line(surface, PENCIL_COLOR,
                (cx + 5, y + 24 + bob), (cx + 7 + walk, y + 30 + bob), 2, seed_offset + 150)


def draw_jumper(surface, x, y, facing_right=True, frame=0, seed_offset=0):
    """Zeichnet einen Jumper-Gegner (Frosch-artig)."""
    cx = x + 15
    flip = 1 if facing_right else -1
    bob = math.sin(frame * 0.2) * 1

    # Körper (breiter)
    body_points = [
        (cx - 12, y + 20 + bob),
        (cx - 8, y + 8 + bob),
        (cx, y + 4 + bob),
        (cx + 8, y + 8 + bob),
        (cx + 12, y + 20 + bob),
    ]
    wobbly_polygon(surface, PENCIL_COLOR, body_points, 2, seed_offset)

    # Große Augen
    wobbly_circle(surface, PENCIL_COLOR, (cx - 4, int(y + 10 + bob)), 3, 2, 8, seed_offset + 50)
    wobbly_circle(surface, PENCIL_COLOR, (cx + 4, int(y + 10 + bob)), 3, 2, 8, seed_offset + 70)
    pygame.draw.circle(surface, PENCIL_COLOR, (int(cx - 3 + flip), int(y + 10 + bob)), 1)
    pygame.draw.circle(surface, PENCIL_COLOR, (int(cx + 5 + flip), int(y + 10 + bob)), 1)

    # Beine (springbereit)
    wobbly_line(surface, PENCIL_COLOR,
                (cx - 10, y + 20 + bob), (cx - 14, y + 28 + bob), 2, seed_offset + 100)
    wobbly_line(surface, PENCIL_COLOR,
                (cx - 14, y + 28 + bob), (cx - 8, y + 30 + bob), 2, seed_offset + 120)
    wobbly_line(surface, PENCIL_COLOR,
                (cx + 10, y + 20 + bob), (cx + 14, y + 28 + bob), 2, seed_offset + 150)
    wobbly_line(surface, PENCIL_COLOR,
                (cx + 14, y + 28 + bob), (cx + 8, y + 30 + bob), 2, seed_offset + 170)


def draw_flyer(surface, x, y, frame=0, seed_offset=0):
    """Zeichnet einen Flyer-Gegner (Fledermaus-artig)."""
    cx = x + 15
    cy = y + 12

    # Flügel-Animation
    wing_angle = math.sin(frame * 0.25) * 0.5

    # Körper (klein, rund)
    wobbly_circle(surface, PENCIL_COLOR, (cx, cy), 6, 2, 10, seed_offset)

    # Augen
    pygame.draw.circle(surface, PENCIL_COLOR, (cx - 3, cy - 1), 1)
    pygame.draw.circle(surface, PENCIL_COLOR, (cx + 3, cy - 1), 1)

    # Ohren
    wobbly_triangle(surface, PENCIL_COLOR,
                    (cx - 5, cy - 5), (cx - 8, cy - 12), (cx - 2, cy - 7),
                    1, seed_offset + 30)
    wobbly_triangle(surface, PENCIL_COLOR,
                    (cx + 5, cy - 5), (cx + 8, cy - 12), (cx + 2, cy - 7),
                    1, seed_offset + 40)

    # Flügel
    wing_y_off = math.sin(frame * 0.25) * 8
    # Links
    wobbly_line(surface, PENCIL_COLOR,
                (cx - 6, cy), (cx - 22, cy - 6 - wing_y_off), 2, seed_offset + 100)
    wobbly_line(surface, PENCIL_COLOR,
                (cx - 22, cy - 6 - wing_y_off), (cx - 14, cy + 2), 2, seed_offset + 120)
    wobbly_line(surface, PENCIL_COLOR,
                (cx - 14, cy + 2), (cx - 6, cy), 1, seed_offset + 140)
    # Rechts
    wobbly_line(surface, PENCIL_COLOR,
                (cx + 6, cy), (cx + 22, cy - 6 - wing_y_off), 2, seed_offset + 200)
    wobbly_line(surface, PENCIL_COLOR,
                (cx + 22, cy - 6 - wing_y_off), (cx + 14, cy + 2), 2, seed_offset + 220)
    wobbly_line(surface, PENCIL_COLOR,
                (cx + 14, cy + 2), (cx + 6, cy), 1, seed_offset + 240)


def draw_moving_platform(surface, x, y, w, h, seed_offset=0):
    """Zeichnet eine bewegliche Plattform mit Pfeilen."""
    wobbly_rect(surface, PENCIL_COLOR, (x, y, w, h), 2, seed_offset)
    # Pfeile andeuten
    mid_y = y + h // 2
    wobbly_line(surface, PENCIL_LIGHT, (x + 5, mid_y), (x + w - 5, mid_y), 1, seed_offset + 400)
    # Pfeilspitzen
    wobbly_line(surface, PENCIL_LIGHT, (x + w - 10, mid_y - 3), (x + w - 5, mid_y), 1, seed_offset + 450)
    wobbly_line(surface, PENCIL_LIGHT, (x + w - 10, mid_y + 3), (x + w - 5, mid_y), 1, seed_offset + 460)


def draw_falling_platform(surface, x, y, w, h, shake=0, seed_offset=0):
    """Zeichnet eine fallende Plattform (mit optionalem Wackeln)."""
    sx = random.uniform(-shake, shake) if shake > 0 else 0
    sy = random.uniform(-shake, shake) if shake > 0 else 0
    wobbly_rect(surface, PENCIL_COLOR, (x + sx, y + sy, w, h), 2, seed_offset)
    # Risse andeuten
    wobbly_line(surface, PENCIL_LIGHT, (x + sx + w * 0.3, y + sy + 2),
                (x + sx + w * 0.5, y + sy + h - 2), 1, seed_offset + 500)
    wobbly_line(surface, PENCIL_LIGHT, (x + sx + w * 0.6, y + sy + 3),
                (x + sx + w * 0.7, y + sy + h - 1), 1, seed_offset + 550)
