# game.py - Spielzustandsmaschine (Menü/Spielen/Pause/etc.)
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from player import Player
from level import LevelManager, parse_level
from particles import ParticleSystem
import sketch
import ui
import sound


# Spielzustände
STATE_MENU = 'menu'
STATE_LEVEL_SELECT = 'level_select'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_GAME_OVER = 'game_over'
STATE_LEVEL_COMPLETE = 'level_complete'


class Game:
    def __init__(self):
        self.state = STATE_MENU
        self.level_manager = LevelManager()
        self.player = None
        self.level_data = None
        self.particles = ParticleSystem()
        self.frame = 0
        self._key_down_events = []  # Gesammelte Key-Down Events pro Frame
        sound.init()

    def start_level(self, level_index):
        """Startet ein bestimmtes Level."""
        self.level_data = self.level_manager.load_level(level_index)
        if self.level_data is None:
            self.state = STATE_MENU
            return

        sx, sy = self.level_data['player_start']
        self.player = Player(sx, sy)
        self.particles = ParticleSystem()
        self.state = STATE_PLAYING

    def restart_level(self):
        """Startet das aktuelle Level neu."""
        self.start_level(self.level_manager.current_level)

    def handle_events(self, events):
        """Verarbeitet Eingabe-Events."""
        mouse_pos = pygame.mouse.get_pos()
        self._key_down_events = []

        for event in events:
            if event.type == pygame.QUIT:
                return False

            # Sammle KEYDOWN Events für den Spieler
            if event.type == pygame.KEYDOWN and self.state == STATE_PLAYING:
                self._key_down_events.append(event.key)

            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = ui.draw_main_menu(
                        pygame.Surface((1, 1)), mouse_pos, self.frame)
                    if buttons['start'][0]:
                        sound.play('click')
                        self.start_level(0)
                    elif buttons['select'][0]:
                        sound.play('click')
                        self.state = STATE_LEVEL_SELECT
                    elif buttons['quit'][0]:
                        return False

            elif self.state == STATE_LEVEL_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = ui.draw_level_select(
                        pygame.Surface((1, 1)), mouse_pos, self.level_manager)
                    for key, (hover, rect) in buttons.items():
                        if hover and isinstance(key, int):
                            sound.play('click')
                            self.start_level(key)
                            break
                    if 'back' in buttons and buttons['back'][0]:
                        sound.play('click')
                        self.state = STATE_MENU

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = STATE_MENU

            elif self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_PAUSED

            elif self.state == STATE_PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_q:
                        self.state = STATE_MENU

            elif self.state == STATE_GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = ui.draw_game_over(pygame.Surface((1, 1)), mouse_pos)
                    if buttons['retry'][0]:
                        sound.play('click')
                        self.restart_level()
                    elif buttons['menu'][0]:
                        sound.play('click')
                        self.state = STATE_MENU

            elif self.state == STATE_LEVEL_COMPLETE:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = ui.draw_level_complete(
                        pygame.Surface((1, 1)), mouse_pos,
                        self.level_manager.current_level,
                        self.level_manager.total_levels)
                    if 'next' in buttons and buttons['next'][0]:
                        sound.play('click')
                        next_data = self.level_manager.next_level()
                        if next_data:
                            self.level_data = next_data
                            sx, sy = self.level_data['player_start']
                            self.player = Player(sx, sy)
                            self.particles = ParticleSystem()
                            self.state = STATE_PLAYING
                    if buttons['menu'][0]:
                        sound.play('click')
                        self.state = STATE_MENU

        return True

    def update(self):
        """Aktualisiert den Spielzustand."""
        self.frame += 1
        sketch.tick()

        if self.state != STATE_PLAYING:
            return

        if self.player is None or self.level_data is None:
            return

        # Spieler-Eingabe
        keys = pygame.key.get_pressed()
        self.player.jumped = False
        self.player.handle_input(keys, self._key_down_events)

        # Sprung-Sound
        if self.player.jumped:
            sound.play('jump')

        # Furz-Partikel
        if self.player.fart_active:
            self.particles.emit_fart(
                self.player.x + self.player.w // 2,
                self.player.y + self.player.h
            )
            sound.play('fart')

        # Vorherige on_ground Zustand
        was_on_ground = self.player.on_ground

        # Spieler Update
        jumped_before = self.player.jumped
        platforms = self.level_data['platforms']
        moving = self.level_data['moving_platforms']
        falling = self.level_data['falling_platforms']
        self.player.update(platforms, moving, falling)

        # Jump Buffer kann auch Sprung auslösen
        if not jumped_before and self.player.jumped:
            sound.play('jump')

        # Landestaub
        if not was_on_ground and self.player.on_ground:
            self.particles.emit_dust(
                self.player.x + self.player.w // 2,
                self.player.y + self.player.h
            )

        # Gegner Update + Kollision
        for enemy in self.level_data['enemies']:
            if not enemy.alive:
                continue
            enemy.update(platforms)

            if self.player.rect.colliderect(enemy.rect):
                # Draufspringen?
                if self.player.vy > 0 and self.player.rect.bottom < enemy.rect.centery:
                    enemy.stomp()
                    self.player.vy = -8  # Abprallen
                    self.particles.emit_stomp(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2)
                    sound.play('stomp')
                else:
                    if self.player.take_damage():
                        self.particles.emit_damage(
                            self.player.x + self.player.w // 2,
                            self.player.y + self.player.h // 2
                        )
                        sound.play('damage')

        # Stacheln
        for spike in self.level_data['spikes']:
            if self.player.rect.colliderect(spike.rect):
                if self.player.take_damage():
                    self.particles.emit_damage(
                        self.player.x + self.player.w // 2,
                        self.player.y + self.player.h // 2
                    )
                    sound.play('damage')

        # Bewegliche Plattformen
        for mp in moving:
            mp.update()

        # Fallende Plattformen
        for fp in falling:
            fp.update()

        # Herz-Pickups
        for heart in self.level_data['hearts']:
            if not heart.collected and self.player.rect.colliderect(heart.rect):
                if self.player.hp < self.player.max_hp:
                    heart.collected = True
                    self.player.heal()
                    sound.play('pickup')

        # Flagge (Level-Ende)
        flag = self.level_data['flag']
        if flag and self.player.rect.colliderect(flag.rect):
            self.level_manager.complete_level()
            sound.play('win')
            self.state = STATE_LEVEL_COMPLETE

        # Spieler-Tod
        if not self.player.alive:
            sound.play('death')
            self.state = STATE_GAME_OVER

        # Kamera
        cam = self.level_data['camera']
        cam.update(
            self.player.x + self.player.w // 2,
            self.player.y + self.player.h // 2
        )

        # Partikel
        self.particles.update()

    def draw(self, surface):
        """Zeichnet den aktuellen Zustand."""
        mouse_pos = pygame.mouse.get_pos()

        if self.state == STATE_MENU:
            ui.draw_main_menu(surface, mouse_pos, self.frame)

        elif self.state == STATE_LEVEL_SELECT:
            ui.draw_level_select(surface, mouse_pos, self.level_manager)

        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_LEVEL_COMPLETE):
            self._draw_gameplay(surface)

            if self.state == STATE_PAUSED:
                ui.draw_pause(surface)
            elif self.state == STATE_GAME_OVER:
                ui.draw_game_over(surface, mouse_pos)
            elif self.state == STATE_LEVEL_COMPLETE:
                ui.draw_level_complete(
                    surface, mouse_pos,
                    self.level_manager.current_level,
                    self.level_manager.total_levels
                )

    def _draw_gameplay(self, surface):
        """Zeichnet das eigentliche Spiel."""
        if self.level_data is None or self.player is None:
            return

        cam = self.level_data['camera']
        sketch.draw_paper_background(surface)

        # Plattformen
        for p in self.level_data['platforms']:
            p.draw(surface, cam)

        # Bewegliche Plattformen
        for mp in self.level_data['moving_platforms']:
            mp.draw(surface, cam)

        # Fallende Plattformen
        for fp in self.level_data['falling_platforms']:
            fp.draw(surface, cam)

        # Stacheln
        for spike in self.level_data['spikes']:
            spike.draw(surface, cam)

        # Herzen
        for heart in self.level_data['hearts']:
            heart.draw(surface, cam)

        # Flagge
        if self.level_data['flag']:
            self.level_data['flag'].draw(surface, cam)

        # Gegner
        for enemy in self.level_data['enemies']:
            enemy.draw(surface, cam)

        # Spieler
        self.player.draw(surface, cam)

        # Partikel
        self.particles.draw(surface, cam)

        # HUD
        ui.draw_hud(surface, self.player, self.level_manager.current_level,
                     self.player.fart_cooldown)
