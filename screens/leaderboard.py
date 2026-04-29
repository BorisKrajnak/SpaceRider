import pygame
import os
from core.config import IMG_DIR, FONT_DIR
from core.game_state import GameState
from core.music_manager import start_music, get_music_state, toggle_mute
from core.score_manager import get_leaderboard
from core.auth_manager import get_user

start_music()

WHITE = (255, 255, 255)
SPACE_BLUE = (10, 10, 40)
PURPLE = (31, 10, 30)

PADDING_X = 25  # 👈 zarovnanie doľava


# ---------------- UI ----------------
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

    txt = font.render(text, True, WHITE)
    surface.blit(txt, txt.get_rect(center=rect.center))


def draw_music_button(surface, rect, music_state):
    color1 = (50, 0, 70)
    color2 = (20, 0, 20)

    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        r = color1[0] + (color2[0] - color1[0]) * (y / rect.height)
        g = color1[1] + (color2[1] - color1[1]) * (y / rect.height)
        b = color1[2] + (color2[2] - color1[2]) * (y / rect.height)
        pygame.draw.line(gradient, (int(r), int(g), int(b), 220), (0, y), (rect.width, y))

    surface.blit(gradient, rect.topleft)
    pygame.draw.rect(surface, WHITE, rect, 3, border_radius=8)

    img_path = os.path.join(IMG_DIR, "mute.png" if music_state["muted"] else "unmute.png")
    if os.path.exists(img_path):
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.smoothscale(img, (rect.width - 10, rect.height - 10))
        surface.blit(img, (rect.x + (rect.width - img.get_width()) // 2,
                           rect.y + (rect.height - img.get_height()) // 2))


# ---------------- MAIN ----------------
def run(screen):

    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    font_path = os.path.join(FONT_DIR, "VOYAGER.ttf")

    title_font = pygame.font.Font(font_path, 90) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 90, bold=True)
    font = pygame.font.Font(font_path, 32) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 32, bold=True)
    button_font = pygame.font.Font(font_path, 50) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 50, bold=True)

    games = ["raketka", "ufo", "school"]
    leaderboards = {g: [] for g in games}
    user = get_user()

    if isinstance(user, dict):
        email = user.get("email", "")
    else:
        email = user or ""

    # z emailu sprav meno (boris@gmail.com → boris)
    current_user = email.split("@")[0].lower()

    active_game_index = 0

    # ---------------- SCROLL ----------------
    scroll_index = {g: 0 for g in games}
    VISIBLE_ROWS = 10
    ROW_HEIGHT = 40

    back_button = pygame.Rect(width // 2 - 200, height - 150, 400, 90)
    mute_button = pygame.Rect(width - 100, 30, 70, 70)

    clock = pygame.time.Clock()
    last_update = 0

    while True:

        # ---------------- UPDATE DATA ----------------
        now = pygame.time.get_ticks()
        if now - last_update > 2000:
            for g in games:
                leaderboards[g] = get_leaderboard(g)
            last_update = now

        active_game = games[active_game_index]
        data = leaderboards.get(active_game, [])

        # clamp scroll
        max_scroll = max(0, len(data) - VISIBLE_ROWS)
        scroll_index[active_game] = max(0, min(scroll_index[active_game], max_scroll))

        # ---------------- BACKGROUND ----------------
        screen.fill((20, 0, 40))

        # ---------------- TITLE ----------------
        title = title_font.render("GLOBAL LEADERBOARD", True, WHITE)
        screen.blit(title, (width // 2 - title.get_width() // 2, 50))

        column_width = width // 3
        start_y = 210

        # ---------------- COLUMNS ----------------
        for col, game in enumerate(games):

            x_center = col * column_width

            if col == active_game_index:
                pygame.draw.rect(screen, (70, 0, 90),
                                 (col * column_width, 140, column_width, height - 140), 2)

            color = WHITE if col == active_game_index else (150, 150, 150)

            # title stĺpca
            screen.blit(font.render(game.upper(), True, color),
                        (x_center + PADDING_X, 150))

            data = leaderboards.get(game, [])
            start = scroll_index[game]

            # ---------------- LIST ----------------
            for i in range(VISIBLE_ROWS):
                idx = start + i
                if idx >= len(data):
                    break

                player = data[idx]


                score = player["score"]
                if game == "school":
                    score = f"{float(score):.2f}"

                text = f"{idx + 1}. {player['name']} - {score}"

                is_current_user = player.get("name", "").lower() == current_user
                text_color = (255, 215, 0) if is_current_user else WHITE

                surf = font.render(text, True, text_color)

                y = start_y + i * ROW_HEIGHT

                # 👈 LEFT ALIGN v stĺpci
                screen.blit(surf, (x_center + PADDING_X, y))

        # ---------------- BUTTONS ----------------
        draw_gradient_button(screen, back_button, "BACK", button_font, SPACE_BLUE, PURPLE)
        draw_music_button(screen, mute_button, get_music_state())

        # ---------------- EVENTS ----------------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    return GameState.MENU

                if event.key == pygame.K_m:
                    toggle_mute()

                # TAB → switch column
                if event.key == pygame.K_TAB:
                    active_game_index = (active_game_index + 1) % len(games)

                if event.key == pygame.K_RIGHT:
                    active_game_index = (active_game_index + 1) % len(games)

                if event.key == pygame.K_LEFT:
                    active_game_index = (active_game_index - 1) % len(games)

                if event.key == pygame.K_UP:
                    scroll_index[active_game] -= 1

                if event.key == pygame.K_DOWN:
                    scroll_index[active_game] += 1

            # mouse wheel scroll
            if event.type == pygame.MOUSEWHEEL:
                scroll_index[active_game] -= event.y

            if event.type == pygame.MOUSEBUTTONDOWN:

                if back_button.collidepoint(event.pos):
                    return GameState.MENU

                if mute_button.collidepoint(event.pos):
                    toggle_mute()

        pygame.display.update()
        clock.tick(60)