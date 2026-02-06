import os
import pygame

# --- Inicializácia mixéra ---
pygame.mixer.init()

# --- Globálne premenné pre správu hudby ---
MUSIC_STATE = {
    "playing": True,
    "volume": 0.5,
    "last_volume": 0.5,
    "muted": True
}

# --- Absolútna cesta k hudbe ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_FILE = os.path.join(BASE_DIR, "assets", "music", "music_02.mp3")


def start_music():
    if not os.path.exists(MUSIC_FILE):
        print(f"Hudba nenájdená: {MUSIC_FILE}")
        return

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play(-1)

        if MUSIC_STATE["muted"]:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(MUSIC_STATE["volume"])

        MUSIC_STATE["playing"] = True


def toggle_mute():
    MUSIC_STATE["muted"] = not MUSIC_STATE["muted"]

    if MUSIC_STATE["muted"]:
        MUSIC_STATE["last_volume"] = MUSIC_STATE["volume"]
        pygame.mixer.music.set_volume(0)
    else:
        MUSIC_STATE["volume"] = MUSIC_STATE["last_volume"]
        pygame.mixer.music.set_volume(MUSIC_STATE["volume"])

    if not pygame.mixer.music.get_busy():
        start_music()

    return MUSIC_STATE["muted"]


def set_volume(volume_level=0.5):
    volume = max(0.0, min(1.0, volume_level))
    MUSIC_STATE["volume"] = volume
    MUSIC_STATE["last_volume"] = volume
    if not MUSIC_STATE["muted"]:
        pygame.mixer.music.set_volume(volume)
    return volume


def get_music_state():
    return MUSIC_STATE
