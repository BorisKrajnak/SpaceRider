import json
import pygame
import os
import random
from core.music_manager import start_music, get_music_state, toggle_mute
from core.game_state import GameState
from core.config import IMG_DIR, FONT_DIR, get_path

# Spustenie hudby
start_music()

# --- Funkcie na načítanie dát ---
def load_game_config():
    try:
        with open(get_path("data", "game_config.json"), "r") as f:
            config = json.load(f)
            return config.get("active_game", "unknown")
    except FileNotFoundError:
        return "unknown"

def load_score():
    try:
        with open(get_path("data", "skore.json"), "r") as f:
            data = json.load(f)
            return data.get("skore", 0), data.get("cas", 0)
    except:
        return 0, 0

def load_best(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get("best", 0)
    except:
        return 0

def save_game_config(active_game, map_image):
    """Uloží aktuálnu hru a mapu do game_config.json"""
    config_file = get_path("data", "game_config.json")
    config = {"active_game": active_game, "map_image": map_image}
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)

# --- Bezpečné načítanie obrázkov ---
def safe_load_image(path, size=None):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    else:
        w, h = size if size else (50, 50)
        placeholder = pygame.Surface((w, h))
        placeholder.fill((255, 255, 255))
        return placeholder

# --- Farby ---
WHITE = (255, 255, 255)
SPACE_BLUE = (10, 10, 40)
PURPLE = (31, 10, 30)


# === Gradient tlačidlo ===
def draw_gradient_button(surface, rect, text, font, color1, color2):
    gradient = pygame.Surface((rect.width, rect.height))
    for y in range(rect.height):
        r = color1[0] + (color2[0] - color1[0]) * (y / rect.height)
        g = color1[1] + (color2[1] - color1[1]) * (y / rect.height)
        b = color1[2] + (color2[2] - color1[2]) * (y / rect.height)
        pygame.draw.line(gradient, (int(r), int(g), int(b)), (0, y), (rect.width, y))
    gradient.set_alpha(220)
    surface.blit(gradient, rect.topleft)
    pygame.draw.rect(surface, WHITE, rect, 3, border_radius=8)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


# === Hudobné tlačidlo ===
def draw_music_button(surface, rect, music_state):
    color1 = (50, 0, 70)
    color2 = (20, 0, 20)
    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        r = color1[0] + (color2[0] - color1[0]) * (y / rect.height)
        g = color1[1] + (color2[1] - color1[1]) * (y / rect.height)
        b = color1[2] + (color2[2] - color1[2]) * (y / rect.height)
        pygame.draw.line(gradient, (int(r), int(g), int(b), 220), (0, y), (rect.width, y))
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=8)
    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(gradient, rect.topleft)
    pygame.draw.rect(surface, WHITE, rect, 3, border_radius=8)

    img_path = os.path.join(IMG_DIR, "mute.png" if music_state["muted"] else "unmute.png")
    if os.path.exists(img_path):
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.smoothscale(img, (rect.width - 10, rect.height - 10))
        surface.blit(img, (rect.left + (rect.width - img.get_width()) // 2,
                          rect.top + (rect.height - img.get_height()) // 2))


# --- Hlavná funkcia ---
def run(screen):
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    # Font
    font_path = os.path.join(FONT_DIR, "VOYAGER.ttf")
    font = pygame.font.Font(font_path, 80) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 80, bold=True)
    button_font = pygame.font.Font(font_path, 50) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 50, bold=True)
    big_font = pygame.font.Font(font_path, 100) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 100, bold=True)

    score, cas = load_score()
    best_score_raketka = load_best(get_path("data", "best_score_raketka.json"))
    best_score_ufo = load_best(get_path("data", "best_score_ufo.json"))
    active_game = load_game_config()

    star_img = safe_load_image(os.path.join(IMG_DIR, "doplnky", "star.png"), (80, 80))
    time_img = safe_load_image(os.path.join(IMG_DIR, "doplnky", "time.png"), (80, 80))
    trofej_img = safe_load_image(os.path.join(IMG_DIR, "doplnky", "trofej.png"), (45, 45))

    restart_button = pygame.Rect(width // 2 - 150, height // 2 + 90, 300, 70)
    settings_button = pygame.Rect(width // 2 - 150, height // 2 + 190, 300, 70)
    quit_button = pygame.Rect(width // 2 - 150, height // 2 + 290, 300, 70)

    mute_button = pygame.Rect(width - 80, 20, 60, 60)

    gradient_color1 = (50, 0, 70)
    gradient_color2 = (20, 0, 20)
    clock = pygame.time.Clock()
    running = True

    while running:
        # --- Gradient pozadia ---
        background = pygame.Surface((width, height))
        for y in range(height):
            r = gradient_color1[0] + (gradient_color2[0] - gradient_color1[0]) * (y / height)
            g = gradient_color1[1] + (gradient_color2[1] - gradient_color1[1]) * (y / height)
            b = gradient_color1[2] + (gradient_color2[2] - gradient_color1[2]) * (y / height)
            pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (width, y))
        background.set_alpha(180)  # jemná priehľadnosť
        screen.blit(background, (0, 0))

        # Nadpis
        screen.blit(big_font.render("GAME OVER", True, WHITE), (width // 2 - 300, height // 3 - 100))

        # Best scores
        b1 = button_font.render(f"BEST SCORE RAKETKA: {best_score_raketka}", True, WHITE)
        screen.blit(b1, (10, 10))
        screen.blit(trofej_img, (10 + b1.get_width() + 15, 15))

        b2 = button_font.render(f"BEST SCORE UFO: {best_score_ufo}", True, WHITE)
        screen.blit(b2, (10, 70))
        screen.blit(trofej_img, (10 + b2.get_width() + 15, 75))

        # Score
        score_text = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 3 + 60))
        screen.blit(star_img, (width // 2 + score_text.get_width() // 2 + 10, height // 3 + 65))

        # Time
        time_text = font.render(f"TIME: {cas}", True, WHITE)
        screen.blit(time_text, (width // 2 - time_text.get_width() // 2, height // 3 + 140))
        screen.blit(time_img, (width // 2 + time_text.get_width() // 2 + 10, height // 3 + 145))

        # Buttons
        draw_gradient_button(screen, restart_button, "RESTART", button_font, SPACE_BLUE, PURPLE)
        draw_gradient_button(screen, settings_button, "SETTINGS", button_font, SPACE_BLUE, PURPLE)
        draw_gradient_button(screen, quit_button, "QUIT", button_font, SPACE_BLUE, PURPLE)

        # Music Icon
        draw_music_button(screen, mute_button, get_music_state())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

            # CLICK / KEY HANDLING
            restart_pressed = (
                (event.type == pygame.MOUSEBUTTONDOWN and restart_button.collidepoint(event.pos)) or
                (event.type == pygame.KEYDOWN and event.key == pygame.K_r)
            )

            if restart_pressed:
                active_now = load_game_config()

                # ALWAYS RANDOM MAP
                random_index = random.randint(1, 11)
                extension = "jpg"
                chosen_map = f"pozadie_vesmir_n{random_index}.{extension}"

                save_game_config(active_now, chosen_map)

                return GameState.ROCKET_GAME if active_now == "raketka" else GameState.UFO_GAME

            if (event.type == pygame.MOUSEBUTTONDOWN and settings_button.collidepoint(event.pos)) or (event.type == pygame.KEYDOWN and event.key == pygame.K_n):
                return GameState.SETTINGS

            if event.type == pygame.MOUSEBUTTONDOWN and quit_button.collidepoint(event.pos):
                return None

            if (event.type == pygame.MOUSEBUTTONDOWN and mute_button.collidepoint(event.pos)) \
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_m):
                toggle_mute()

        pygame.display.update()
        clock.tick(60)
