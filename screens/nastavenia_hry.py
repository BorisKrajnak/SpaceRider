import os
import random
import pygame
import json
from core.config import IMG_DIR
from core.music_manager import start_music, get_music_state, toggle_mute
from core.game_state import GameState

WHITE = (255, 255, 255)


# scale obrázka so zachovaním pomeru
def scale_to_fit(image, max_w, max_h):
    w, h = image.get_size()
    scale = min(max_w / w, max_h / h)
    new_size = (int(w * scale), int(h * scale))
    return pygame.transform.smoothscale(image, new_size)


# Gradient tlačidlo
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


# Hudobné tlačidlo Mute / Unmute
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
        surface.blit(
            img,
            (rect.left + (rect.width - img.get_width()) // 2,
             rect.top + (rect.height - img.get_height()) // 2)
        )


# HLAVNÁ FUNKCIA
def run(screen):
    start_music()

    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    # --- Fonty ---
    font_path = os.path.join("assets", "Font", "VOYAGER.ttf")
    if os.path.exists(font_path):
        title_font = pygame.font.Font(font_path, 100)
        button_font = pygame.font.Font(font_path, 50)
        custom_font = pygame.font.Font(font_path, 40)
    else:
        title_font = pygame.font.SysFont("Arial", 80, bold=True)
        button_font = pygame.font.SysFont("Arial", 50, bold=True)
        custom_font = pygame.font.SysFont("Arial", 40, bold=True)

    # --- Obrázky charakterov ---
    control_images = []
    for i in range(1, 4):
        cp = os.path.join(IMG_DIR, "ovladanie", f"ovladanie{i}.png")
        if os.path.exists(cp):
            img = pygame.image.load(cp).convert_alpha()
        else:
            img = pygame.Surface((200, 200))
            img.fill(WHITE)
        control_images.append(img)

    selected_control = None

    # --- UI prvky ---
    button_width, button_height = 250, 75
    start_button = pygame.Rect(width - button_width - 40, height - button_height - 40, button_width, button_height)
    back_button = pygame.Rect(40, height - button_height - 40, button_width, button_height)
    leaderboard_button = pygame.Rect(40, 40, 500, 75)  # 🔥 NOVÉ
    music_button_rect = pygame.Rect(width - 80, 20, 60, 60)

    control_rects = [pygame.Rect(0, 0, 0, 0) for _ in range(3)]

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
        background.set_alpha(180)
        screen.blit(background, (0, 0))

        # --- Text ---
        title_surf = title_font.render("MENU", True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(width // 2, 100)))

        control_text_surf = custom_font.render("CHOOSE CHARACTER", True, WHITE)
        screen.blit(control_text_surf, control_text_surf.get_rect(center=(width // 2, height // 2 - 200)))

        # --- Buttons ---
        draw_gradient_button(screen, start_button, "START", button_font, (50, 0, 70), (20, 0, 20))
        draw_gradient_button(screen, back_button, "BACK", button_font, (50, 0, 70), (20, 0, 20))
        draw_gradient_button(screen, leaderboard_button, "LEADEARBOARD", button_font, (50, 0, 70), (20, 0, 20))  # 🔥 NOVÉ

        # --- Hudba ---
        draw_music_button(screen, music_button_rect, get_music_state())

        # --- Pozície postáv ---
        positions_ctrl = [
            (width // 2 - 300, height // 2 - 120),
            (width // 2 + 80, height // 2 - 120),
            (width // 2 - 110, height // 2 + 60),
        ]

        # Vykreslenie výberu postáv
        for i, pos in enumerate(positions_ctrl):
            is_selected = selected_control == i
            original = control_images[i]

            if is_selected:
                box_w, box_h = 280, 160
                rect = pygame.Rect(pos[0] - 20, pos[1] - 20, box_w, box_h)
                img_scaled = scale_to_fit(original, box_w - 20, box_h - 20)
            else:
                box_w, box_h = 240, 140
                rect = pygame.Rect(pos[0], pos[1], box_w, box_h)
                img_scaled = scale_to_fit(original, box_w - 20, box_h - 20)

            pygame.draw.rect(
                screen,
                (255, 255, 0) if is_selected else WHITE,
                rect,
                width=6 if is_selected else 4,
                border_radius=10
            )

            img_rect = img_scaled.get_rect(center=rect.center)
            screen.blit(img_scaled, img_rect.topleft)

            control_rects[i] = rect

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return GameState.MENU

                if leaderboard_button.collidepoint(event.pos):
                    return GameState.LEADERBOARD

                if music_button_rect.collidepoint(event.pos):
                    toggle_mute()

                for i, rect in enumerate(control_rects):
                    if rect.collidepoint(event.pos):
                        selected_control = i

                if start_button.collidepoint(event.pos) and selected_control is not None:
                    random_index = random.randint(1, 11)

                    config = {
                        "map_image": f"pozadie_vesmir_n{random_index}.jpg",
                        "active_game": "raketka" if selected_control == 0 else "ufo" if selected_control == 1 else "skola"
                    }

                    with open("data/game_config.json", "w") as f:
                        json.dump(config, f, indent=2)

                    if selected_control == 0:
                        return GameState.ROCKET_GAME
                    elif selected_control == 1:
                        return GameState.UFO_GAME
                    else:
                        return GameState.SCHOOL_GAME

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameState.MENU
                if event.key == pygame.K_m:
                    toggle_mute()

        pygame.display.update()
        clock.tick(60)

    return GameState.MENU