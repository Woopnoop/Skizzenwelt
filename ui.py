# ui.py - Hauptmenü, Levelauswahl, HUD, Pause, GameOver
import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PENCIL_COLOR, PAPER_COLOR,
    PENCIL_LIGHT, PENCIL_VERY_LIGHT, HEART_COLOR,
    HIGHLIGHT_COLOR, FART_COOLDOWN
)
import sketch


def _get_font(size):
    """Gibt einen Font zurück."""
    try:
        return pygame.font.SysFont('Segoe UI', size)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_text(surface, text, x, y, size=24, color=None, center=False):
    """Zeichnet Text."""
    color = color or PENCIL_COLOR
    font = _get_font(size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)
    return rect


def _wobbly_button(surface, text, x, y, w, h, mouse_pos, seed_offset=0):
    """Zeichnet einen wackeligen Button, gibt True zurück wenn Maus drüber."""
    rect = pygame.Rect(x, y, w, h)
    hover = rect.collidepoint(mouse_pos)

    if hover:
        # Leicht gefüllter Hintergrund
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, rect)

    sketch.wobbly_rect(surface, PENCIL_COLOR, (x, y, w, h), 2, seed_offset)
    _draw_text(surface, text, x + w // 2, y + h // 2, 22, PENCIL_COLOR, center=True)
    return hover, rect


def draw_main_menu(surface, mouse_pos, frame):
    """Zeichnet das Hauptmenü."""
    sketch.draw_paper_background(surface)

    # Titel "Skizzenwelt"
    title_y = 150
    _draw_text(surface, "Skizzenwelt", SCREEN_WIDTH // 2, title_y, 64, PENCIL_COLOR, center=True)

    # Untertitel
    _draw_text(surface, "Ein Bleistift-Abenteuer", SCREEN_WIDTH // 2, title_y + 60, 20,
               PENCIL_LIGHT, center=True)

    # Kleine Figur als Deko
    sketch.draw_player(surface, SCREEN_WIDTH // 2 - 12, title_y + 90, True, frame)

    # Bodenlinie unter der Figur
    sketch.wobbly_line(surface, PENCIL_COLOR,
                       (SCREEN_WIDTH // 2 - 80, title_y + 138),
                       (SCREEN_WIDTH // 2 + 80, title_y + 138), 2, frame)

    # Buttons
    btn_w, btn_h = 240, 50
    btn_x = SCREEN_WIDTH // 2 - btn_w // 2

    start_hover, start_rect = _wobbly_button(
        surface, "Neues Spiel", btn_x, 400, btn_w, btn_h, mouse_pos, 1000)

    select_hover, select_rect = _wobbly_button(
        surface, "Levelauswahl", btn_x, 470, btn_w, btn_h, mouse_pos, 2000)

    quit_hover, quit_rect = _wobbly_button(
        surface, "Beenden", btn_x, 540, btn_w, btn_h, mouse_pos, 3000)

    return {
        'start': (start_hover, start_rect),
        'select': (select_hover, select_rect),
        'quit': (quit_hover, quit_rect),
    }


def draw_level_select(surface, mouse_pos, level_manager):
    """Zeichnet die Levelauswahl."""
    sketch.draw_paper_background(surface)

    _draw_text(surface, "Levelauswahl", SCREEN_WIDTH // 2, 60, 40, PENCIL_COLOR, center=True)

    buttons = {}
    cols = 5
    box_size = 80
    gap = 20
    start_x = SCREEN_WIDTH // 2 - (cols * (box_size + gap) - gap) // 2
    start_y = 140

    for i in range(level_manager.total_levels):
        row = i // cols
        col = i % cols
        x = start_x + col * (box_size + gap)
        y = start_y + row * (box_size + gap + 20)

        unlocked = level_manager.is_unlocked(i)
        color = PENCIL_COLOR if unlocked else PENCIL_VERY_LIGHT
        rect = pygame.Rect(x, y, box_size, box_size)
        hover = rect.collidepoint(mouse_pos) and unlocked

        if hover:
            pygame.draw.rect(surface, HIGHLIGHT_COLOR, rect)

        sketch.wobbly_rect(surface, color, (x, y, box_size, box_size), 2, i * 500)
        _draw_text(surface, str(i + 1), x + box_size // 2, y + 25, 28, color, center=True)

        name = level_manager.get_level_name(i)
        if len(name) > 12:
            name = name[:11] + "."
        _draw_text(surface, name, x + box_size // 2, y + 55, 12, color, center=True)

        if not unlocked:
            # Schloss-Symbol
            _draw_text(surface, "~", x + box_size // 2, y + box_size // 2 + 5, 20,
                       PENCIL_VERY_LIGHT, center=True)

        buttons[i] = (hover and unlocked, rect)

    # Zurück-Button
    back_hover, back_rect = _wobbly_button(
        surface, "Zurueck", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 45, mouse_pos, 9000)
    buttons['back'] = (back_hover, back_rect)

    return buttons


def draw_hud(surface, player, level_index, fart_cooldown):
    """Zeichnet das HUD (immer sichtbar oben)."""
    # Hintergrund-Streifen
    pygame.draw.rect(surface, (*PAPER_COLOR, 200), (0, 0, SCREEN_WIDTH, 36))
    pygame.draw.line(surface, PENCIL_VERY_LIGHT, (0, 36), (SCREEN_WIDTH, 36), 1)

    # Herzen links
    for i in range(player.max_hp):
        hx = 10 + i * 28
        if i < player.hp:
            sketch.draw_heart(surface, hx, 8, 14, i * 100 + 5000)
        else:
            # Leeres Herz (nur Umriss, heller)
            sketch.draw_heart(surface, hx, 8, 14, i * 100 + 5000)
            pygame.draw.rect(surface, PAPER_COLOR, (hx + 2, 10, 10, 10))
            sketch.wobbly_circle(surface, PENCIL_VERY_LIGHT, (hx + 7, 16), 6, 1, 8, i * 100 + 5100)

    # Steuerung Mitte
    controls = "<- -> Bewegen | Leertaste Springen | F Schub | ESC Pause"
    _draw_text(surface, controls, SCREEN_WIDTH // 2, 18, 13, PENCIL_LIGHT, center=True)

    # Levelnummer rechts
    level_text = f"Level {level_index + 1}"
    _draw_text(surface, level_text, SCREEN_WIDTH - 80, 10, 18, PENCIL_COLOR)

    # Furz-Cooldown Anzeige
    if fart_cooldown > 0:
        bar_x = SCREEN_WIDTH - 160
        bar_w = 60
        bar_h = 6
        remaining = fart_cooldown / FART_COOLDOWN
        pygame.draw.rect(surface, PENCIL_VERY_LIGHT, (bar_x, 26, bar_w, bar_h))
        pygame.draw.rect(surface, PENCIL_LIGHT, (bar_x, 26, int(bar_w * (1 - remaining)), bar_h))


def draw_pause(surface):
    """Zeichnet den Pause-Bildschirm."""
    # Halbtransparenter Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((245, 235, 220, 180))
    surface.blit(overlay, (0, 0))

    _draw_text(surface, "PAUSE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, 48,
               PENCIL_COLOR, center=True)

    _draw_text(surface, "ESC zum Fortfahren", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, 22,
               PENCIL_LIGHT, center=True)
    _draw_text(surface, "Q zum Hauptmenue", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, 22,
               PENCIL_LIGHT, center=True)


def draw_game_over(surface, mouse_pos):
    """Zeichnet den GameOver-Bildschirm."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((245, 235, 220, 200))
    surface.blit(overlay, (0, 0))

    _draw_text(surface, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, 48,
               PENCIL_COLOR, center=True)

    btn_w, btn_h = 200, 45
    btn_x = SCREEN_WIDTH // 2 - btn_w // 2

    retry_hover, retry_rect = _wobbly_button(
        surface, "Nochmal", btn_x, SCREEN_HEIGHT // 2, btn_w, btn_h, mouse_pos, 6000)
    menu_hover, menu_rect = _wobbly_button(
        surface, "Hauptmenue", btn_x, SCREEN_HEIGHT // 2 + 60, btn_w, btn_h, mouse_pos, 7000)

    return {
        'retry': (retry_hover, retry_rect),
        'menu': (menu_hover, menu_rect),
    }


def draw_level_complete(surface, mouse_pos, level_index, total_levels):
    """Zeichnet den Level-Geschafft-Bildschirm."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((245, 235, 220, 200))
    surface.blit(overlay, (0, 0))

    _draw_text(surface, "Level geschafft!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, 42,
               PENCIL_COLOR, center=True)

    btn_w, btn_h = 200, 45
    btn_x = SCREEN_WIDTH // 2 - btn_w // 2

    buttons = {}

    if level_index + 1 < total_levels:
        next_hover, next_rect = _wobbly_button(
            surface, "Naechstes Level", btn_x, SCREEN_HEIGHT // 2, btn_w, btn_h, mouse_pos, 8000)
        buttons['next'] = (next_hover, next_rect)

    menu_hover, menu_rect = _wobbly_button(
        surface, "Hauptmenue", btn_x, SCREEN_HEIGHT // 2 + 60, btn_w, btn_h, mouse_pos, 8500)
    buttons['menu'] = (menu_hover, menu_rect)

    if level_index + 1 >= total_levels:
        _draw_text(surface, "Du hast alle Level geschafft!", SCREEN_WIDTH // 2,
                   SCREEN_HEIGHT // 2 + 130, 24, PENCIL_COLOR, center=True)

    return buttons
