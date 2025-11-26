import os
import json
import pygame
import random

def nacitaj_pozadie(config_file, screen_width, screen_height, map_image=None):
    """
    Načíta pozadie podľa configu, alebo použije map_image ak je zadané.
    """
    if map_image is None:
        # Načítame z configu
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                map_image_name = config.get("map_image", "pozadie_default.jpg")
        except Exception:
            map_image_name = "pozadie_default.jpg"
    else:
        map_image_name = map_image

    # cesta k obrázku
    map_path = os.path.join(os.path.dirname(__file__), "..", "assets", "img", "map_imagines", map_image_name)
    if os.path.exists(map_path):
        return pygame.transform.scale(pygame.image.load(map_path), (screen_width, screen_height))
    else:
        # fallback čierne pozadie
        surface = pygame.Surface((screen_width, screen_height))
        surface.fill((0,0,0))
        return surface

