import pygame
import os
import random
from core.config import IMG_DIR, FONT_DIR, save_game_config
from core.game_state import GameState
from core.music_manager import start_music, get_music_state, toggle_mute
from core.score_manager import load_score, save_score, load_best

# --- Spustenie hudby ---
start_music()

# --- Farby ---
WHITE = (255, 255, 255)
SPACE_BLUE = (10, 10, 40)
PURPLE = (31, 10, 30)
POPUP_BG = (50, 0, 70)


# --- Funkcie ---
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

# --- Funkcia na vykreslenie Game Over obrazovky ---
def draw_game_over_screen(screen, width, height, big_font, font, button_font,
                          score, cas, best_score, star_img, time_img, trofej_img,
                          restart_button, settings_button, quit_button, mute_button):
    SPACE_BLUE = (10, 10, 40)
    PURPLE = (31, 10, 30)

    # --- Gradient pozadia ---
    gradient_color1 = (50, 0, 70)
    gradient_color2 = (20, 0, 20)
    background = pygame.Surface((width, height))
    for y in range(height):
        r = gradient_color1[0] + (gradient_color2[0] - gradient_color1[0]) * (y / height)
        g = gradient_color1[1] + (gradient_color2[1] - gradient_color1[1]) * (y / height)
        b = gradient_color1[2] + (gradient_color2[2] - gradient_color1[2]) * (y / height)
        pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (width, y))
    screen.blit(background, (0, 0))

    # --- Nadpis ---
    screen.blit(big_font.render("GAME OVER", True, WHITE), (width//2 - 300, height//3 - 200))

    # --- Best score ---
    best_text = button_font.render(f"BEST SCORE: {best_score}", True, WHITE)
    screen.blit(best_text, (width//2 - best_text.get_width()//2, height//3 - 110))
    screen.blit(trofej_img, (width//2 + best_text.get_width()//2 + 10, height//3 - 105))

    # --- Score ---
    score_text = font.render(f"SCORE: {score}", True, WHITE)
    screen.blit(score_text, (width//2 - score_text.get_width()//2, height//3 + 10))
    screen.blit(star_img, (width//2 + score_text.get_width()//2 + 10, height//3 + 15))

    # --- Time ---
    time_text = font.render(f"TIME: {cas}", True, WHITE)
    screen.blit(time_text, (width//2 - time_text.get_width()//2, height//3 + 90))
    screen.blit(time_img, (width//2 + time_text.get_width()//2 + 10, height//3 + 95))

    # --- Buttons ---
    draw_gradient_button(screen, restart_button, "RESTART", button_font, SPACE_BLUE, PURPLE)
    draw_gradient_button(screen, settings_button, "SETTINGS", button_font, SPACE_BLUE, PURPLE)
    draw_gradient_button(screen, quit_button, "QUIT", button_font, SPACE_BLUE, PURPLE)
    draw_music_button(screen, mute_button, get_music_state())

# --- Funkcia na vyskakovacie okno best score ---
def show_best_popup(screen, value, trofej_img, draw_bg_func):
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    popup_width, popup_height = 1100, 400
    popup_rect = pygame.Rect((width - popup_width)//2, (height - popup_height)//2, popup_width, popup_height)

    font_path = os.path.join(FONT_DIR, "VOYAGER.ttf")
    title_font = pygame.font.Font(font_path, 60) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 60, bold=True)
    score_font = pygame.font.Font(font_path, 90) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 90, bold=True)
    x_font = pygame.font.Font(font_path, 40) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 40, bold=True)

    running = True
    clock = pygame.time.Clock()

    while running:
        # --- Prekreslenie pozadia (Game Over obrazovky) ---
        draw_bg_func()

        # --- Jemný overlay pre lepšiu čitateľnosť popupu ---
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # --- Popup ---
        popup_surf = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        popup_surf.fill((0, 0, 0, 0))

        # Vytvorenie masky s zaoblenými rohmi
        mask_surf = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (*POPUP_BG, 240), mask_surf.get_rect(), border_radius=20)
        pygame.draw.rect(mask_surf, WHITE, mask_surf.get_rect(), 3, border_radius=20)
        popup_surf.blit(mask_surf, (0, 0))

        # --- Text ---
        title_text = title_font.render("You beat your best score!", True, WHITE)
        score_text = score_font.render(f"{value}", True, WHITE)
        x_text = x_font.render("X", True, WHITE)

        popup_surf.blit(title_text, title_text.get_rect(center=(popup_width//2, 150)))
        popup_surf.blit(score_text, score_text.get_rect(center=(popup_width//2 - 20, 250)))
        popup_surf.blit(x_text, (popup_width - 50, 10))

        screen.blit(popup_surf, popup_rect.topleft)
        pygame.display.update()
        clock.tick(60)

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if popup_rect.left + popup_width - 50 <= mx <= popup_rect.left + popup_width - 10 \
                        and popup_rect.top + 10 <= my <= popup_rect.top + 50:
                    running = False


# --- Hlavná funkcia ---
def run(screen):
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    font_path = os.path.join(FONT_DIR, "VOYAGER.ttf")
    font = pygame.font.Font(font_path, 80) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 80, bold=True)
    button_font = pygame.font.Font(font_path, 50) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 50, bold=True)
    big_font = pygame.font.Font(font_path, 100) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 100, bold=True)

    # --- Načítanie skóre ---
    active_game = "raketka"
    score, cas = load_score(active_game)
    best_score = load_best(active_game)

    new_best = False
    if score > best_score:
        best_score = score
        save_score(active_game, best_score, cas, best=True)
        new_best = True

    # --- Obrázky ---
    star_img = safe_load_image(os.path.join(IMG_DIR, "doplnky", "star.png"), (80, 80))
    time_img = safe_load_image(os.path.join(IMG_DIR, "doplnky", "time.png"), (80, 80))
    trofej_img = safe_load_image(os.path.join(IMG_DIR, "doplnky", "trofej.png"), (45, 45))

    # --- Tlačidlá ---
    restart_button = pygame.Rect(width // 2 - 200, height // 2 + 50, 400, 90)
    settings_button = pygame.Rect(width // 2 - 200, height // 2 + 170, 400, 90)
    quit_button = pygame.Rect(width // 2 - 200, height // 2 + 290, 400, 90)
    mute_button = pygame.Rect(width - 100, 30, 70, 70)

    clock = pygame.time.Clock()
    running = True

    def draw_bg():
        draw_game_over_screen(screen, width, height, big_font, font, button_font,
                              score, cas, best_score, star_img, time_img, trofej_img,
                              restart_button, settings_button, quit_button, mute_button)

    # --- Popup ak je nové best score ---
    if new_best:
        res = show_best_popup(screen, best_score, trofej_img, draw_bg)
        if res == "QUIT":
            return None

    while running:
        draw_bg()

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

            restart_pressed = (
                (event.type == pygame.MOUSEBUTTONDOWN and restart_button.collidepoint(event.pos)) or
                (event.type == pygame.KEYDOWN and event.key == pygame.K_r)
            )
            if restart_pressed:
                save_score(active_game, score, cas)
                random_index = random.randint(1, 11)
                chosen_map = f"pozadie_vesmir_n{random_index}.jpg"
                save_game_config(active_game, chosen_map)
                return GameState.ROCKET_GAME if active_game == "raketka" else GameState.UFO_GAME

            if (event.type == pygame.MOUSEBUTTONDOWN and settings_button.collidepoint(event.pos)) or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_n):
                return GameState.SETTINGS

            if event.type == pygame.MOUSEBUTTONDOWN and quit_button.collidepoint(event.pos):
                return None

            if (event.type == pygame.MOUSEBUTTONDOWN and mute_button.collidepoint(event.pos)) \
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_m):
                toggle_mute()

        pygame.display.update()
        clock.tick(60)
