# player.py - Spielerfigur mit allen Mechaniken
import pygame
from settings import (
    GRAVITY, MAX_FALL_SPEED, PLAYER_SPEED, PLAYER_JUMP_FORCE,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_MAX_HP,
    COYOTE_TIME, JUMP_BUFFER, FART_BOOST, FART_COOLDOWN,
    INVULNERABILITY_FRAMES, TILE_SIZE
)
import sketch


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.vx = 0.0
        self.vy = 0.0
        self.facing_right = True
        self.on_ground = False
        self.frame = 0
        self.moving = False

        # Sprung-Mechanik
        self.coyote_timer = 0
        self.jump_buffer = 0
        self.jumped = False  # Flag für Sound

        # Kanten-Festhalten
        self.hanging = False
        self.hang_dir = 0  # 1 = rechts, -1 = links
        self.can_hang = True

        # Furz-Schub
        self.fart_cooldown = 0
        self.fart_active = False

        # Leben
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.invulnerable = 0
        self.alive = True

        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def reset(self, x, y):
        """Setzt den Spieler an eine neue Position zurück."""
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.hanging = False
        self.fart_cooldown = 0
        self.invulnerable = 0
        self.alive = True
        self.coyote_timer = 0
        self.jump_buffer = 0
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def take_damage(self, particles=None):
        """Spieler nimmt Schaden."""
        if self.invulnerable > 0:
            return False
        self.hp -= 1
        self.invulnerable = INVULNERABILITY_FRAMES
        self.vy = -6  # Rückstoß nach oben
        if self.hp <= 0:
            self.alive = False
        return True

    def heal(self):
        """Heilt ein Herz."""
        if self.hp < self.max_hp:
            self.hp += 1

    def handle_input(self, keys, key_down_events):
        """Verarbeitet Eingaben."""
        # Horizontale Bewegung
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
            self.moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing_right = True
            self.moving = True
        else:
            self.moving = False

        # Springen (mit Buffer)
        for event in key_down_events:
            if event == pygame.K_SPACE or event == pygame.K_UP or event == pygame.K_w:
                self.jump_buffer = JUMP_BUFFER
                if self.hanging:
                    self._climb_up()

            if event == pygame.K_f:
                self._try_fart()

        # Kanten-Festhalten: Hochklettern mit Hoch
        if self.hanging:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self._climb_up()

    def _try_jump(self):
        """Versucht zu springen."""
        if self.coyote_timer > 0:
            self.vy = PLAYER_JUMP_FORCE
            self.coyote_timer = 0
            self.jump_buffer = 0
            self.on_ground = False
            self.jumped = True
            return True
        return False

    def _climb_up(self):
        """Klettert von der Kante hoch."""
        self.hanging = False
        self.vy = PLAYER_JUMP_FORCE * 0.8
        self.vx = self.hang_dir * PLAYER_SPEED
        self.can_hang = False
        self.jumped = True

    def _try_fart(self):
        """Furz-Schub in der Luft."""
        if not self.on_ground and self.fart_cooldown <= 0 and not self.hanging:
            self.vy = FART_BOOST
            self.fart_cooldown = FART_COOLDOWN
            self.fart_active = True
            return True
        return False

    def update(self, platforms, moving_platforms, falling_platforms):
        """Aktualisiert Spieler-Physik und Kollision."""
        if not self.alive:
            return

        self.frame += 1

        # Timer
        if self.invulnerable > 0:
            self.invulnerable -= 1
        if self.fart_cooldown > 0:
            self.fart_cooldown -= 1

        # Sprung Buffer
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            if self._try_jump():
                pass

        # Gravitation (nicht wenn hangend)
        if not self.hanging:
            self.vy += GRAVITY
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED

        # Coyote Time
        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
            self.can_hang = True
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        if self.hanging:
            self.vy = 0
            self.vx = 0

        # Horizontale Bewegung + Kollision
        self.x += self.vx
        self.rect.x = int(self.x)
        all_platforms = list(platforms) + list(moving_platforms) + [fp for fp in falling_platforms if fp.visible and not fp.falling]
        self._collide_horizontal(all_platforms)

        # Auf beweglichen Plattformen mitfahren
        for mp in moving_platforms:
            if self.on_ground and self.rect.colliderect(mp.rect):
                if abs(self.rect.bottom - mp.rect.top) < 8:
                    self.x += mp.dx
                    self.rect.x = int(self.x)

        # Vertikale Bewegung + Kollision
        self.y += self.vy
        self.rect.y = int(self.y)
        was_on_ground = self.on_ground
        self.on_ground = False
        self._collide_vertical(all_platforms)

        # Boden-Sonde: prüft ob Spieler direkt auf einer Plattform steht
        # (verhindert Flackern durch Float→Int-Rundung)
        if not self.on_ground and self.vy >= 0:
            probe = pygame.Rect(self.rect.x, self.rect.y + 1, self.w, self.h)
            for p in all_platforms:
                r = p.rect if hasattr(p, 'rect') else p
                if probe.colliderect(r):
                    self.on_ground = True
                    break

        # Kanten-Erkennung
        if not self.on_ground and self.vy > 0 and self.can_hang and not self.hanging:
            self._check_ledge_grab(all_platforms)

        # Fallende Plattformen triggern
        for fp in falling_platforms:
            if fp.visible and not fp.falling and self.rect.colliderect(fp.rect):
                if abs(self.rect.bottom - fp.rect.top) < 8:
                    fp.trigger()

        # Fart reset
        self.fart_active = False

        # Tod durch Fallen
        if self.y > 2000:
            self.alive = False

    def _collide_horizontal(self, platforms):
        for p in platforms:
            r = p.rect if hasattr(p, 'rect') else p
            if self.rect.colliderect(r):
                if self.vx > 0:
                    self.rect.right = r.left
                    self.x = float(self.rect.x)
                elif self.vx < 0:
                    self.rect.left = r.right
                    self.x = float(self.rect.x)

    def _collide_vertical(self, platforms):
        for p in platforms:
            r = p.rect if hasattr(p, 'rect') else p
            if self.rect.colliderect(r):
                if self.vy > 0:
                    self.rect.bottom = r.top
                    self.y = float(self.rect.y)
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = r.bottom
                    self.y = float(self.rect.y)
                    self.vy = 0

    def _check_ledge_grab(self, platforms):
        """Prüft ob der Spieler eine Kante greifen kann."""
        check_dist = 6
        for p in platforms:
            r = p.rect if hasattr(p, 'rect') else p
            # Rechts neben einer Plattform
            probe_right = pygame.Rect(self.rect.right, self.rect.top, check_dist, self.h)
            if probe_right.colliderect(r):
                # Oberkante der Plattform ist nahe Spieler-Mitte
                if abs(r.top - self.rect.centery) < self.h // 2:
                    self.hanging = True
                    self.hang_dir = 1
                    self.vy = 0
                    self.y = float(r.top - self.h // 2)
                    self.rect.y = int(self.y)
                    self.facing_right = True
                    return

            # Links neben einer Plattform
            probe_left = pygame.Rect(self.rect.left - check_dist, self.rect.top, check_dist, self.h)
            if probe_left.colliderect(r):
                if abs(r.top - self.rect.centery) < self.h // 2:
                    self.hanging = True
                    self.hang_dir = -1
                    self.vy = 0
                    self.y = float(r.top - self.h // 2)
                    self.rect.y = int(self.y)
                    self.facing_right = False
                    return

    def draw(self, surface, cam):
        """Zeichnet den Spieler."""
        if not self.alive:
            return

        # Blink-Effekt bei Unverwundbarkeit
        if self.invulnerable > 0 and (self.invulnerable // 4) % 2 == 0:
            return

        sx, sy = cam.apply(int(self.x), int(self.y))

        if self.hanging:
            sketch.draw_player_hanging(surface, sx, sy, self.facing_right)
        else:
            f = self.frame if self.moving else 0
            sketch.draw_player(surface, sx, sy, self.facing_right, f)
