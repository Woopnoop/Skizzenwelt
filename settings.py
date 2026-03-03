# settings.py - Alle Konstanten für Skizzenwelt

# Bildschirm
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Skizzenwelt"

# Tile / Grid
TILE_SIZE = 40

# Physik
GRAVITY = 0.6
MAX_FALL_SPEED = 12
PLAYER_SPEED = 4
PLAYER_JUMP_FORCE = -11
COYOTE_TIME = 6          # Frames nach Plattformkante, in denen Sprung noch möglich
JUMP_BUFFER = 8           # Frames vor Landung, in denen Sprung vorgemerkt wird
FART_BOOST = -9           # Aufwärtskraft des Furz-Schubs
FART_COOLDOWN = 180       # 3 Sekunden bei 60 FPS
INVULNERABILITY_FRAMES = 90  # 1.5 Sekunden Unverwundbarkeit

# Spieler
PLAYER_WIDTH = 24
PLAYER_HEIGHT = 44
PLAYER_MAX_HP = 3

# Gegner
WALKER_SPEED = 1.5
JUMPER_SPEED = 1.5
JUMPER_JUMP_INTERVAL = 120   # Frames zwischen Sprüngen
JUMPER_JUMP_FORCE = -9
FLYER_SPEED = 1.2
FLYER_AMPLITUDE = 40        # Sinuswellen-Amplitude
FLYER_FREQUENCY = 0.03      # Sinuswellen-Frequenz

# Plattformen
MOVING_PLATFORM_SPEED = 1.5
FALLING_PLATFORM_SHAKE_TIME = 30   # Frames wackeln vor Fall
FALLING_PLATFORM_RESET_TIME = 180  # Frames bis Neuerscheinung

# Kamera
CAMERA_LERP = 0.08

# Bleistift-Stil
SKETCH_SEGMENTS = 6          # Segmente pro Linie
SKETCH_WOBBLE = 2.5          # Max Pixel-Verschiebung
SKETCH_REDRAW_INTERVAL = 6   # Alle N Frames neu zeichnen
LINE_WIDTH = 2               # Standard-Linienbreite

# Farben (Bleistift auf Papier)
PAPER_COLOR = (245, 235, 220)        # Cremefarbenes Papier
PAPER_LINE_COLOR = (210, 200, 185)   # Linien auf dem Papier
PENCIL_COLOR = (45, 40, 35)          # Graphit-Dunkel
PENCIL_LIGHT = (100, 95, 85)         # Helleres Graphit
PENCIL_VERY_LIGHT = (160, 150, 140)  # Sehr helles Graphit
HEART_COLOR = (180, 60, 60)          # Gedämpftes Rot für Herzen
SPIKE_COLOR = (60, 55, 50)           # Dunkle Stacheln
FLAG_COLOR = (120, 50, 50)           # Flaggenfarbe
HIGHLIGHT_COLOR = (200, 180, 150)    # Highlight für UI

# Partikel
DUST_PARTICLE_COUNT = 5
FART_PARTICLE_COUNT = 8
STOMP_PARTICLE_COUNT = 6
PARTICLE_LIFETIME = 30       # Frames

# Sound
SAMPLE_RATE = 22050
SOUND_VOLUME = 0.3
