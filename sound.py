# sound.py - Prozedural generierte Soundeffekte
import pygame
import math
import array
import random
from settings import SAMPLE_RATE, SOUND_VOLUME


_initialized = False
_sounds = {}


def init():
    """Initialisiert das Sound-System und generiert alle Sounds."""
    global _initialized, _sounds
    if _initialized:
        return
    try:
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        _sounds['jump'] = _make_jump_sound()
        _sounds['fart'] = _make_fart_sound()
        _sounds['stomp'] = _make_stomp_sound()
        _sounds['damage'] = _make_damage_sound()
        _sounds['pickup'] = _make_pickup_sound()
        _sounds['death'] = _make_death_sound()
        _sounds['click'] = _make_click_sound()
        _sounds['win'] = _make_win_sound()
        _initialized = True
    except Exception:
        _initialized = False


def play(name):
    """Spielt einen Sound ab."""
    if not _initialized:
        return
    if name in _sounds and _sounds[name] is not None:
        _sounds[name].play()


def _make_sound(samples_list):
    """Erstellt einen pygame.mixer.Sound aus einer Sample-Liste."""
    # Normalisieren
    if not samples_list:
        return None
    max_val = max(abs(s) for s in samples_list) or 1
    scale = 32000 / max_val * SOUND_VOLUME
    int_samples = [max(-32768, min(32767, int(s * scale))) for s in samples_list]
    buf = array.array('h', int_samples)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound


def _make_jump_sound():
    """Kurzer aufsteigender Ton."""
    duration = 0.12
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 300 + t * 3000
        envelope = 1 - t / duration
        s = math.sin(2 * math.pi * freq * t) * envelope
        samples.append(s)
    return _make_sound(samples)


def _make_fart_sound():
    """Kurzes tiefes Blubbern."""
    duration = 0.25
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 80 + math.sin(t * 30) * 30
        envelope = (1 - t / duration) ** 2
        s = math.sin(2 * math.pi * freq * t) * envelope
        s += random.uniform(-0.3, 0.3) * envelope  # Rauschen
        samples.append(s)
    return _make_sound(samples)


def _make_stomp_sound():
    """Kurzer dumpfer Schlag."""
    duration = 0.1
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 200 - t * 1000
        if freq < 50:
            freq = 50
        envelope = (1 - t / duration) ** 3
        s = math.sin(2 * math.pi * freq * t) * envelope
        samples.append(s)
    return _make_sound(samples)


def _make_damage_sound():
    """Schmerz-Sound."""
    duration = 0.3
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 400 - t * 800
        if freq < 100:
            freq = 100
        envelope = (1 - t / duration)
        s = math.sin(2 * math.pi * freq * t) * envelope
        s += math.sin(2 * math.pi * freq * 1.5 * t) * envelope * 0.3
        samples.append(s)
    return _make_sound(samples)


def _make_pickup_sound():
    """Aufheb-Sound (aufsteigend, fröhlich)."""
    duration = 0.2
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 500 + t * 2000
        envelope = 1 - (t / duration) ** 2
        s = math.sin(2 * math.pi * freq * t) * envelope
        s += math.sin(2 * math.pi * freq * 2 * t) * envelope * 0.3
        samples.append(s)
    return _make_sound(samples)


def _make_death_sound():
    """Tod-Sound (absteigend)."""
    duration = 0.6
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 500 - t * 600
        if freq < 50:
            freq = 50
        envelope = 1 - t / duration
        s = math.sin(2 * math.pi * freq * t) * envelope
        s += math.sin(2 * math.pi * freq * 0.5 * t) * envelope * 0.5
        samples.append(s)
    return _make_sound(samples)


def _make_click_sound():
    """Menü-Klick."""
    duration = 0.05
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 800
        envelope = (1 - t / duration) ** 2
        s = math.sin(2 * math.pi * freq * t) * envelope
        samples.append(s)
    return _make_sound(samples)


def _make_win_sound():
    """Level-geschafft Fanfare."""
    duration = 0.5
    n = int(SAMPLE_RATE * duration)
    samples = []
    notes = [523, 659, 784, 1047]  # C E G C (Dur-Akkord)
    for i in range(n):
        t = i / SAMPLE_RATE
        note_idx = min(int(t / (duration / len(notes))), len(notes) - 1)
        freq = notes[note_idx]
        envelope = 1 - (t / duration) ** 0.5
        s = math.sin(2 * math.pi * freq * t) * envelope
        samples.append(s)
    return _make_sound(samples)
