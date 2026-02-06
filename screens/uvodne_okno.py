import pygame
import os
from core.config import IMG_DIR, FONT_DIR
from core.music_manager import start_music, get_music_state, toggle_mute
from core.game_state import GameState

# --- Farby ---
WHITE = (255, 255, 255)
SPACE_BLUE = (10, 10, 40)

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

# === Gradient pozadia pre pravidlá ===
def draw_gradient_rect(surface, rect, color_top, color_bottom):
    gradient = pygame.Surface((rect.width, rect.height))
    for y in range(rect.height):
        r = color_top[0] + (color_bottom[0] - color_top[0]) * (y / rect.height)
        g = color_top[1] + (color_bottom[1] - color_top[1]) * (y / rect.height)
        b = color_top[2] + (color_bottom[2] - color_top[2]) * (y / rect.height)
        pygame.draw.line(gradient, (int(r), int(g), int(b)), (0, y), (rect.width, y))
    gradient.set_alpha(230)
    surface.blit(gradient, rect.topleft)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)

# === Hudobné tlačidlo Mute/Unmute s obrázkami ===
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

    img_path = os.path.join(IMG_DIR, "mute.png") if music_state["muted"] else os.path.join(IMG_DIR, "unmute.png")
    if os.path.exists(img_path):
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.smoothscale(img, (rect.width - 10, rect.height - 10))
        surface.blit(img, (rect.left + (rect.width - img.get_width()) // 2,
                          rect.top + (rect.height - img.get_height()) // 2))


def run(screen):
    pygame.display.set_caption("Space Rider")
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    voyager_path = os.path.join(FONT_DIR, "VOYAGER.ttf")
    if os.path.exists(voyager_path):
        title_font = pygame.font.Font(voyager_path, 170)
        button_font = pygame.font.Font(voyager_path, 50)
        small_font = pygame.font.Font(voyager_path, 25)
    else:
        title_font = pygame.font.SysFont("Arial", 170, bold=True)
        button_font = pygame.font.SysFont("Arial", 50, bold=True)
        small_font = pygame.font.SysFont("Arial", 25)

    try:
        background_img = pygame.image.load(f"{IMG_DIR}/pozadie_uvodne_okno.jpg")
        background_img = pygame.transform.scale(background_img, (width, height))
    except:
        background_img = None

    button_w, button_h = 260, 80
    padding = 150
    logout_btn = pygame.Rect(padding, height - button_h - padding, button_w, button_h)  # <- ODHLÁSIŤ SA
    rules_btn = pygame.Rect((width - button_w) // 2, height - button_h - padding, button_w, button_h)
    next_btn = pygame.Rect(width - button_w - padding, height - button_h - padding, button_w, button_h)
    music_size = 60
    music_btn = pygame.Rect(width - music_size - 20, 20, music_size, music_size)

    title_text = title_font.render("SPACE  RIDER", True, WHITE)

    showing_rules = False
    clock = pygame.time.Clock()

    rules_lines = [
        "Cielom je prezit co najdlhsie vo vesmire a ziskat skore.",
        "Vyber si mapu, raketku alebo UFO.",
        "Vyhybaj sa meteoritom, zbieraj palivo a body.",
        "Niektore power-upy su docasne a aktivuj ich klavesou E.",
        "Ovladanie: WASD alebo gamepad."
    ]

    start_music()
    music_state = get_music_state()

    pygame.event.clear()
    start_time = pygame.time.get_ticks()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if pygame.time.get_ticks() - start_time < 400:
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameState.LOGIN
                elif event.key == pygame.K_RETURN:
                    return GameState.SETTINGS
                elif event.key == pygame.K_m:
                    toggle_mute()

                    music_state = get_music_state()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if logout_btn.collidepoint(event.pos):
                    return GameState.LOGIN
                if next_btn.collidepoint(event.pos):
                    return GameState.SETTINGS
                if rules_btn.collidepoint(event.pos):
                    showing_rules = not showing_rules
                if music_btn.collidepoint(event.pos):
                    toggle_mute()
                    music_state = get_music_state()

        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(SPACE_BLUE)

        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 140))

        draw_gradient_button(screen, logout_btn, "LOG OUT", button_font, (50, 0, 70), (20, 0, 20))  # <- text zmenený
        draw_gradient_button(screen, rules_btn, "RULES", button_font, (50, 0, 70), (20, 0, 20))
        draw_gradient_button(screen, next_btn, "NEXT", button_font, (50, 0, 70), (20, 0, 20))
        draw_music_button(screen, music_btn, music_state)

        if showing_rules:
            popup_w, popup_h = 800, 500
            popup_rect = pygame.Rect((width - popup_w)//2, (height - popup_h)//2, popup_w, popup_h)
            draw_gradient_rect(screen, popup_rect, (50, 0, 50), (10, 0, 10))

            heading = button_font.render("PRAVIDLÁ HRY", True, WHITE)
            screen.blit(heading, heading.get_rect(center=(popup_rect.centerx, popup_rect.top + 60)))

            text_padding = 40
            max_text_width = popup_rect.width - 2 * text_padding
            line_height = 40
            for i, line in enumerate(rules_lines):
                txt_surface = small_font.render(line, True, WHITE)
                if txt_surface.get_width() > max_text_width:
                    scale = max_text_width / txt_surface.get_width()
                    txt_surface = pygame.transform.smoothscale(txt_surface, (int(txt_surface.get_width()*scale), int(txt_surface.get_height()*scale)))
                txt_rect = txt_surface.get_rect()
                txt_rect.topleft = (popup_rect.left + text_padding, popup_rect.top + 150 + i * line_height)
                screen.blit(txt_surface, txt_rect)

        pygame.display.update()
        clock.tick(60)

    return None
