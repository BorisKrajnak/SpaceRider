import pygame
import os
import json
from core.config import get_path, IMG_DIR, FONT_DIR
from core.game_state import GameState
from core.music_manager import start_music, get_music_state, toggle_mute
from core.score_manager import get_leaderboard

# --- hudba ---
start_music()

# --- farby ---
WHITE = (255, 255, 255)
SPACE_BLUE = (10, 10, 40)
PURPLE = (31, 10, 30)


# --- UI ---
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


# --- HLAVNÁ FUNKCIA ---
def run(screen):
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    font_path = os.path.join(FONT_DIR, "VOYAGER.ttf")
    title_font = pygame.font.Font(font_path, 90) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 90, bold=True)
    font = pygame.font.Font(font_path, 40) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 40, bold=True)
    button_font = pygame.font.Font(font_path, 50) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 50, bold=True)

    # --- hry ---
    games = ["raketka", "ufo", "school"]

    # --- leaderboard cache ---
    leaderboards = {g: [] for g in games}
    last_update = 0

    # --- tlačidlá ---
    back_button = pygame.Rect(width // 2 - 200, height - 150, 400, 90)
    mute_button = pygame.Rect(width - 100, 30, 70, 70)

    clock = pygame.time.Clock()
    running = True

    while running:

        # ---------------- REFRESH (každé 2 sekundy) ----------------
        now = pygame.time.get_ticks()
        if now - last_update > 2000:
            for g in games:
                leaderboards[g] = get_leaderboard(g)
            last_update = now

        # --- pozadie ---
        gradient_color1 = (50, 0, 70)
        gradient_color2 = (20, 0, 20)
        background = pygame.Surface((width, height))

        for y in range(height):
            r = gradient_color1[0] + (gradient_color2[0] - gradient_color1[0]) * (y / height)
            g = gradient_color1[1] + (gradient_color2[1] - gradient_color1[1]) * (y / height)
            b = gradient_color1[2] + (gradient_color2[2] - gradient_color1[2]) * (y / height)
            pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (width, y))

        screen.blit(background, (0, 0))

        # --- titul ---
        title = title_font.render("GLOBAL LEADERBOARD", True, WHITE)
        screen.blit(title, (width // 2 - title.get_width() // 2, 50))

        # --- 3 stĺpce ---
        column_width = width // 3
        start_y = 210
        line_height = 40

        for col, game in enumerate(games):
            x_center = col * column_width + column_width // 2

            game_title = font.render(game.upper(), True, WHITE)
            screen.blit(game_title, (x_center - game_title.get_width() // 2, 150))

            data = leaderboards.get(game, [])

            if not data:
                no = font.render("No scores yet", True, WHITE)
                screen.blit(no, (x_center - no.get_width() // 2, start_y))
                continue

            for i, player in enumerate(data[:10]):
                score = player["score"]

                if game == "school":
                    score = f"{float(score):.2f}"
                else:
                    score = str(score)

                text = f"{i + 1}. {player['name']} - {score}"
                surf = font.render(text, True, WHITE)
                y = start_y + i * line_height
                screen.blit(surf, (x_center - surf.get_width() // 2, y))

        # --- buttons ---
        draw_gradient_button(screen, back_button, "BACK", button_font, SPACE_BLUE, PURPLE)
        draw_music_button(screen, mute_button, get_music_state())

        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameState.MENU
                if event.key == pygame.K_m:
                    toggle_mute()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return GameState.MENU

                if mute_button.collidepoint(event.pos):
                    toggle_mute()

        pygame.display.update()
        clock.tick(60)

    return GameState.MENU