import pygame
import os
import json
from core.game_state import GameState
from core.config import BASE_DIR, IMG_DIR
from core.music_manager import toggle_mute, get_music_state

WHITE = (255, 255, 255)

def draw_gradient_button(surface, rect, color1, color2):
    """Nakreslí gradient tlačidlo s rovným prechodom."""
    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        r = color1[0] + (color2[0] - color1[0]) * (y / rect.height)
        g = color1[1] + (color2[1] - color1[1]) * (y / rect.height)
        b = color1[2] + (color2[2] - color1[2]) * (y / rect.height)
        pygame.draw.line(gradient, (int(r), int(g), int(b), 220), (0, y), (rect.width, y))
    surface.blit(gradient, rect.topleft)
    pygame.draw.rect(surface, WHITE, rect, 3, border_radius=8)

def run(screen):
    pygame.font.init()
    clock = pygame.time.Clock()

    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    BG_COLOR = (30, 30, 60)
    gradient_color1 = (50, 0, 70)
    gradient_color2 = (20, 0, 20)

    # Font
    font_path = os.path.join(BASE_DIR, "assets", "Font", "VOYAGER.ttf")
    font_big = pygame.font.Font(font_path, 100) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 90)
    font = pygame.font.Font(font_path, 50) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 50)

    # Load saved score
    cfg_path = os.path.join(BASE_DIR, "data", "game_config.json")
    last_score = 0
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            data = json.load(f)
            last_score = data.get("last_score", 0)

    # Buttons
    restart_btn = pygame.Rect(width // 2 - 200, height // 2 + 50, 400, 90)
    settings_btn = pygame.Rect(width // 2 - 200, height // 2 + 170, 400, 90)
    quit_btn = pygame.Rect(width // 2 - 200, height // 2 + 290, 400, 90)

    # Music button
    music_button_rect = pygame.Rect(width - 100, 30, 70, 70)

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

        # Title
        title_text = font_big.render("VYSVEDCENIE", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(width // 2, height // 4)))

        # Score
        score_text = font.render(f"Priemer: {last_score:.2f}", True, WHITE)
        screen.blit(score_text, score_text.get_rect(center=(width // 2, height // 2 - 50)))

        # Buttons
        draw_gradient_button(screen, restart_btn, gradient_color1, gradient_color2)
        draw_gradient_button(screen, settings_btn, gradient_color1, gradient_color2)
        draw_gradient_button(screen, quit_btn, gradient_color1, gradient_color2)

        screen.blit(font.render("RESTART", True, WHITE), font.render("RESTART", True, WHITE).get_rect(center=restart_btn.center))
        screen.blit(font.render("SETTINGS", True, WHITE), font.render("SETTINGS", True, WHITE).get_rect(center=settings_btn.center))
        screen.blit(font.render("QUIT", True, WHITE), font.render("QUIT", True, WHITE).get_rect(center=quit_btn.center))

        # Music Button
        draw_gradient_button(screen, music_button_rect, gradient_color1, gradient_color2)

        icon_file = "mute.png" if get_music_state()["muted"] else "unmute.png"
        icon_path = os.path.join(IMG_DIR, icon_file)
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path).convert_alpha()
            icon = pygame.transform.smoothscale(icon, (music_button_rect.width - 10, music_button_rect.height - 10))
            screen.blit(icon, (music_button_rect.x + 5, music_button_rect.y + 5))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos):
                    return GameState.SCHOOL_GAME
                if settings_btn.collidepoint(event.pos):
                    return GameState.SETTINGS
                if quit_btn.collidepoint(event.pos):
                    return None
                if music_button_rect.collidepoint(event.pos):
                    toggle_mute()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_r:
                    return GameState.SCHOOL_GAME
                if event.key == pygame.K_n:
                    return GameState.SETTINGS
                if event.key == pygame.K_m:
                    toggle_mute()

        pygame.display.update()
        clock.tick(60)
