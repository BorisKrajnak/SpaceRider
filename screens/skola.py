import os
import random
import pygame
import json
from core.game_state import GameState
from core.config import IMG_DIR, BASE_DIR, get_path
from core.music_manager import start_music, get_music_state, toggle_mute
from core.score_manager import save_score

WHITE = (255, 255, 255)


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


def run(screen):
    pygame.mixer.init()
    clock = pygame.time.Clock()
    start_music()

    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    font_path = os.path.join(BASE_DIR, "assets", "Font", "VOYAGER.ttf")
    font = pygame.font.Font(font_path, 40) if os.path.exists(font_path) else pygame.font.SysFont("Arial", 40)

    # --- PLAYER ---
    player_img_path = os.path.join(IMG_DIR, "ovladanie", "ovladanie_skola.png")
    player_width, player_height = 100, 100

    try:
        player_img = pygame.image.load(player_img_path).convert_alpha()
        player_img = pygame.transform.smoothscale(player_img, (player_width, player_height))
    except:
        player_img = pygame.Surface((player_width, player_height))
        player_img.fill(WHITE)

    player = pygame.Rect(100, height // 2, player_width, player_height)
    player_speed = 10

    # --- GAME DATA ---
    items = []
    grades = []

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 100)

    music_button_rect = pygame.Rect(width - 80, 20, 60, 60)

    start_time = pygame.time.get_ticks()
    game_duration = 20000

    background_img_path = get_path("assets", "img", "map_imagines", "pozadie_pycharm.png")

    if os.path.exists(background_img_path):
        background_img = pygame.image.load(background_img_path).convert()
    else:
        background_img = pygame.Surface((width, height))
        background_img.fill((30, 30, 60))

    def get_grade_color(n):
        return {
            1: (0, 255, 0),
            2: (170, 255, 0),
            3: (255, 165, 0),
            4: (255, 85, 0),
            5: (255, 0, 0)
        }.get(n, (255, 255, 255))

    running = True
    while running:

        screen.blit(background_img, (0, 0))

        # --- movement ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += player_speed

        player.x = max(0, min(player.x, width - player.width))
        player.y = max(0, min(player.y, height - player.height))

        # --- EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameState.MENU
                if event.key == pygame.K_m:
                    toggle_mute()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if music_button_rect.collidepoint(event.pos):
                    toggle_mute()

            if event.type == SPAWN_EVENT:
                number = random.randint(1, 5)
                rect = pygame.Rect(width + 50, random.randint(50, height - 50), 30, 30)
                items.append({"rect": rect, "number": number})

        # --- ITEMS ---
        for item in items[:]:
            item["rect"].x -= 7

            text_surf = font.render(str(item["number"]), True, get_grade_color(item["number"]))
            text_rect = text_surf.get_rect(center=item["rect"].center)

            screen.blit(text_surf, text_rect)

            if player.colliderect(text_rect):
                grades.append(item["number"])
                items.remove(item)

            elif text_rect.right < 0:
                items.remove(item)

        screen.blit(player_img, player.topleft)

        # --- SCORE ---
        avg = sum(grades) / len(grades) if grades else 0

        screen.blit(font.render(f"Average: {avg:.2f}", True, WHITE), (20, 20))

        elapsed = pygame.time.get_ticks() - start_time
        time_left = max(0, (game_duration - elapsed) // 1000)
        screen.blit(font.render(f"Time: {time_left}s", True, WHITE), (20, 70))

        draw_music_button(screen, music_button_rect, get_music_state())

        # --- END GAME ---
        if elapsed >= game_duration:

            cfg_path = os.path.join(BASE_DIR, "data", "game_config.json")

            # --- load config bezpečne ---
            cfg = {}
            if os.path.exists(cfg_path):
                with open(cfg_path, "r") as f:
                    try:
                        cfg = json.load(f)
                    except:
                        cfg = {}

            # --- uloz last score ---
            cfg["last_score"] = round(avg, 2)

            # --- leaderboard save (TO JE HLAVNÉ) ---
            save_score("school", avg, cas=0)

            # --- write config ---
            with open(cfg_path, "w") as f:
                json.dump(cfg, f, indent=2)

            return GameState.VYSVEDCENIE

        pygame.display.update()
        clock.tick(60)