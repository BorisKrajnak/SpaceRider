import pygame
import os

pygame.mixer.init()

# Globálne premenné pre správu hudby
MUSIC_STATE = {
    "playing": True,
    "volume": 0.5,
    "last_volume": 0.5,  # Uloženie poslednej hlasitosti pre obnovenie po stlmení
    "muted": False     # Nový stav pre indikáciu stlmenia
}

def start_music():
    if not pygame.mixer.music.get_busy() and MUSIC_STATE["playing"]:
        music_file = 'music/music_02.mp3'
        if os.path.exists(music_file):
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(MUSIC_STATE["volume"])

def toggle_music():
    """Prepína medzi prehrávaním a pozastavením hudby"""
    MUSIC_STATE["playing"] = not MUSIC_STATE["playing"]

    if MUSIC_STATE["playing"]:
        # Zapnutie hudby
        if not pygame.mixer.music.get_busy():
            start_music()
        else:
            pygame.mixer.music.unpause()
    else:
        # Vypnutie hudby
        pygame.mixer.music.pause()

    return MUSIC_STATE["playing"]

def set_volume(volume_level=0.5):
    """Nastaví hlasitosť hudby (0.0 až 1.0)"""
    volume = max(0.0, min(1.0, volume_level))  # Obmedzenie na rozsah 0.0-1.0
    MUSIC_STATE["volume"] = volume
    MUSIC_STATE["last_volume"] = volume
    pygame.mixer.music.set_volume(volume)
    return volume

def get_music_state():
    """Vráti aktuálny stav hudby"""
    return MUSIC_STATE

def toggle_mute():
    """Prepína medzi stlmením a obnovením hlasitosti hudby"""
    MUSIC_STATE["muted"] = not MUSIC_STATE["muted"]

    if MUSIC_STATE["muted"]:
        # Stlmenie hudby - uložíme aktuálnu hlasitosť a nastavíme na 0
        MUSIC_STATE["last_volume"] = MUSIC_STATE["volume"]
        pygame.mixer.music.set_volume(0)
    else:
        # Obnovenie hlasitosti
        MUSIC_STATE["volume"] = MUSIC_STATE["last_volume"]
        pygame.mixer.music.set_volume(MUSIC_STATE["volume"])

    return MUSIC_STATE["muted"]
