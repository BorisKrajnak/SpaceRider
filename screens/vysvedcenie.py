import pygame
import os
import json
from core.game_state import GameState
from core.config import BASE_DIR, IMG_DIR, get_path
from core.music_manager import toggle_mute, get_music_state
from core.score_manager import load_best, save_score

WHITE = (255, 255, 255)

# --- Funkcia na gradient button s textom ---
def draw_gradient_button(surface, rect, text, font, color1, color2):
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

    if text:
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

# --- Prevod hodnotenia ---
def grade_to_text(grade):
    return {
        1: "výborný/á",
        2: "chválitebný/á",
        3: "dobrý/á",
        4: "dostatočný/á",
        5: "nedostatočný/á"
    }.get(grade, "neznáme hodnotenie")

# --- Funkcia pre popup nové best score ---
def show_best_popup(screen, value, trofej_img, draw_bg_func):
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    popup_width, popup_height = 1100, 400
    popup_rect = pygame.Rect((width - popup_width)//2, (height - popup_height)//2, popup_width, popup_height)

    font_path = os.path.join(BASE_DIR, "assets", "Font", "VOYAGER.ttf")
    title_font = pygame.font.Font(font_path, 60) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 60, bold=True)
    score_font = pygame.font.Font(font_path, 90) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 90, bold=True)
    x_font = pygame.font.Font(font_path, 40) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 40, bold=True)

    POPUP_BG = (50, 0, 70)
    running = True
    clock = pygame.time.Clock()

    while running:
        draw_bg_func()

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        popup_surf = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        popup_surf.fill((0,0,0,0))  # priehľadné pozadie

        mask_surf = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (*POPUP_BG, 240), mask_surf.get_rect(), border_radius=20)
        pygame.draw.rect(mask_surf, WHITE, mask_surf.get_rect(), 3, border_radius=20)
        popup_surf.blit(mask_surf, (0, 0))

        # --- Text ---
        title_text = title_font.render("You beat your best average!", True, WHITE)
        score_text = score_font.render(f"{value:.2f}", True, WHITE)
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
    pygame.font.init()
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    gradient_color1 = (50, 0, 70)
    gradient_color2 = (20, 0, 20)

    # Fonty
    font_path = os.path.join(BASE_DIR, "assets", "Font", "VOYAGER.ttf")
    font_big = pygame.font.Font(font_path, 100) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 90)
    font = pygame.font.Font(font_path, 40) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 40)
    button_font = pygame.font.Font(font_path, 50) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 50)

    # --- Načítanie skóre z poslednej hry ---
    cfg_path = os.path.join(BASE_DIR, "data", "game_config.json")
    last_score = 0
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            data = json.load(f)
            last_score = data.get("last_score", 0)

    # --- Načítanie all-time best priemeru ---
    best_average = load_best("school")  # hra sa volá "school"

    # --- Aktualizácia best average ---
    new_best = False
    if best_average == 0 or last_score < best_average:
        best_average = last_score
        new_best = True

        # uloženie BEST DO SAMOSTATNÉHO SUBORU
        best_path = os.path.join(BASE_DIR, "data", "best_school.json")

        with open(best_path, "w") as f:
            json.dump({"best": best_average}, f)

    # --- Prepočet na známku ---
    grade = round(last_score)
    grade = max(1, min(5, grade))
    grade_text = grade_to_text(grade)

    # --- Tlačidlá ---
    restart_btn = pygame.Rect(width // 2 - 200, height // 2 + 50, 400, 90)
    settings_btn = pygame.Rect(width // 2 - 200, height // 2 + 170, 400, 90)
    quit_btn = pygame.Rect(width // 2 - 200, height // 2 + 290, 400, 90)
    music_button_rect = pygame.Rect(width - 100, 30, 70, 70)

    # --- Ikona trofeje ---
    trofej_img = None
    trofej_path = os.path.join(IMG_DIR, "doplnky", "trofej.png")
    if os.path.exists(trofej_path):
        trofej_img = pygame.image.load(trofej_path).convert_alpha()
        trofej_img = pygame.transform.scale(trofej_img, (45, 45))

    def draw_bg():
        # --- Gradient pozadia ---
        background = pygame.Surface((width, height))
        for y in range(height):
            r = gradient_color1[0] + (gradient_color2[0] - gradient_color1[0]) * (y / height)
            g = gradient_color1[1] + (gradient_color2[1] - gradient_color1[1]) * (y / height)
            b = gradient_color1[2] + (gradient_color2[2] - gradient_color1[2]) * (y / height)
            pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (width, y))
        background.set_alpha(180)
        screen.blit(background, (0, 0))

        # --- Nadpis ---
        title_text = font_big.render("REPORT CARD", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(width // 2, height // 4 - 110)))

        # --- Best priemer ---
        best_text_surf = font.render(f"BEST AVERAGE: {best_average:.2f}", True, WHITE)
        best_rect = best_text_surf.get_rect(center=(width // 2, height//3 - 110))
        screen.blit(best_text_surf, best_rect)
        if trofej_img:
            screen.blit(trofej_img, (best_rect.right + 10, best_rect.top))

        # --- Výpis skóre a hodnotenia ---
        avg_text = font.render(f"AVERAGE: {last_score:.2f}", True, WHITE)
        screen.blit(avg_text, avg_text.get_rect(center=(width // 2, height // 2 - 140)))
        grade_number_text = font.render(f"YOUR GRADE: {grade}", True, WHITE)
        screen.blit(grade_number_text, grade_number_text.get_rect(center=(width // 2, height // 2 - 70)))
        hodnotenie_text = font.render(f"RATING: {grade_text}", True, WHITE)
        screen.blit(hodnotenie_text, hodnotenie_text.get_rect(center=(width // 2, height // 2)))

        # --- Gradient tlačidlá ---
        draw_gradient_button(screen, restart_btn, "RESTART", button_font, gradient_color1, gradient_color2)
        draw_gradient_button(screen, settings_btn, "MENU", button_font, gradient_color1, gradient_color2)
        draw_gradient_button(screen, quit_btn, "QUIT", button_font, gradient_color1, gradient_color2)

        # --- Hudobné tlačidlo ---
        draw_gradient_button(screen, music_button_rect, "", button_font, gradient_color1, gradient_color2)
        icon_file = "mute.png" if get_music_state()["muted"] else "unmute.png"
        icon_path = os.path.join(IMG_DIR, icon_file)
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path).convert_alpha()
            icon = pygame.transform.smoothscale(icon, (music_button_rect.width - 10, music_button_rect.height - 10))
            screen.blit(icon, (music_button_rect.x + 5, music_button_rect.y + 5))

    # --- Popup ak je nové best score ---
    if new_best:
        res = show_best_popup(screen, best_average, trofej_img, draw_bg)
        if res == "QUIT":
            return None

    running = True
    while running:
        draw_bg()

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_r:
                    return GameState.SCHOOL_GAME
                if event.key == pygame.K_n:
                    return GameState.SETTINGS
                if event.key == pygame.K_m:
                    toggle_mute()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos):
                    return GameState.SCHOOL_GAME
                if settings_btn.collidepoint(event.pos):
                    return GameState.SETTINGS
                if quit_btn.collidepoint(event.pos):
                    return None
                if music_button_rect.collidepoint(event.pos):
                    toggle_mute()

        pygame.display.update()
        clock.tick(60)
