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
        small_font = pygame.font.SysFont("Arial", 25)
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
        "                                                       CIEĽ HRY ",
        "Tvojím cieľom je prežiť čo najdlhšie vo vesmíre.",
        "Za prežitie, zbieranie objektov a vyhýbanie sa prekážkam získavaš skóre.",
        "Čím dlhšie prežiješ, tým vyššie skóre dosiahneš.",
        "",
        "                                                   HERNÉ MÓDY",
        "RAKETKA:",
        "- Pohyb vo všetkých smeroch (WASD)",
        "- Stabilný a plne ovládateľný štýl letu",
        "",
        "UFO:",
        "- Funguje na princípe gravitácie (neustále padá dole)",
        "- W = skok / zdvih nahor",
        "- A / D = pohyb do strán",
        "- Vyžaduje presné načasovanie pohybu",
        "",
        "ŠKOLSKÝ MÓD:",
        "- 20-sekundová minihra zameraná na zručnosť a presnosť",
        "- Tvojou úlohou je nazbierať čo najlepší priemer známok v krátkom čase",
        "- Ovládanie rovnaké ako raketka (WASD)",
        "- Ideálny režim na tréning reakcií a ovládania",
        "",
        "OVLÁDANIE ",
        "W - pohyb hore / skok (UFO)",
        "A - pohyb doľava",
        "S - pohyb dole (raketka a školský mód)",
        "D - pohyb doprava",
        "E - aktivovanie štítu",
        "",
        "                                                   HERNÉ PRVKY",
        "METEORITY:",
        "- Hlavná prekážka v hre",
        "- Pri zrážke hra končí",
        "",
        "PALIVO:",
        "- Potrebné na prežitie",
        "- Ak ho nezbieraš, môžeš prehrať",
        "",
        "POWER-UPY:",
        "- Poskytujú dočasné výhody",
        "- Srdiečka sa aktivujú automaticky pri náraze",
        "- Štít musíš aktivovať klávesou E",
        "",
        "KLÁVESOVÉ SKRATKY",
        "M - zapnutie / vypnutie hudby",
        "P - pauza hry (UFO a raketka)",
        "TAB - prepinanie stlpca v leaderboerde",
        "← - prepinanie stlpca v leaderboerde smerom do lava",
        "→ - prepinanie stlpca v leaderboerde smerom do doprava",
        "↑ - posuvanie riadka v leaderboerde smerom hore",
        "↓ - posuvanie riadka v leaderboerde smerom dole",
        "ESC - návrat späť do menu",
        "",
        "TIPY PRE HRÁČA",
        "- Sleduj okolie a plánuj pohyb dopred",
        "- Pri UFO móde dávaj pozor na gravitáciu",
        "- Power-upy používaj strategicky",
        "- Zbieraj palivo čo najčastejšie",

        "",
        "VEĽA ŠŤASTIA!"
    ]

    start_music()
    music_state = get_music_state()

    pygame.event.clear()
    start_time = pygame.time.get_ticks()
    running = True

    scroll_offset = 0
    scroll_speed = 20

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

                if event.button == 4:
                    scroll_offset = max(scroll_offset - scroll_speed, 0)

                if event.button == 5:
                    scroll_offset += scroll_speed

        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(SPACE_BLUE)

        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 140))

        draw_gradient_button(screen, logout_btn, "LOG OUT", button_font, (50, 0, 70), (20, 0, 20))
        draw_gradient_button(screen, rules_btn, "RULES", button_font, (50, 0, 70), (20, 0, 20))
        draw_gradient_button(screen, next_btn, "NEXT", button_font, (50, 0, 70), (20, 0, 20))
        draw_music_button(screen, music_btn, music_state)

        if showing_rules:
            popup_w, popup_h = 800, 500
            popup_rect = pygame.Rect((width - popup_w) // 2, (height - popup_h) // 2, popup_w, popup_h)
            draw_gradient_rect(screen, popup_rect, (50, 0, 50), (10, 0, 10))

            heading = button_font.render("PRAVIDLÁ HRY", True, WHITE)
            screen.blit(heading, heading.get_rect(center=(popup_rect.centerx, popup_rect.top + 60)))

            text_padding = 40
            line_height = 35

            # surface pre scroll
            content_height = len(rules_lines) * line_height + 50
            scroll_surface = pygame.Surface((popup_rect.width - 2 * text_padding, content_height), pygame.SRCALPHA)

            for i, line in enumerate(rules_lines):
                txt_surface = small_font.render(line, True, WHITE)
                scroll_surface.blit(txt_surface, (0, i * line_height))

            # limit scrollu
            max_scroll = max(0, content_height - (popup_rect.height - 150))
            scroll_offset = min(scroll_offset, max_scroll)

            view_rect = pygame.Rect(0, scroll_offset, popup_rect.width - 2 * text_padding, popup_rect.height - 150)

            screen.blit(
                scroll_surface,
                (popup_rect.left + text_padding, popup_rect.top + 120),
                view_rect
            )

            # === SCROLLBAR ===
            bar_width = 10
            bar_x = popup_rect.right - 15
            bar_y = popup_rect.top + 120
            bar_height = popup_rect.height - 150

            # pozadie scrollbaru
            pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), border_radius=5)

            if content_height > 0:
                thumb_height = max(40, bar_height * (bar_height / content_height))
            else:
                thumb_height = bar_height

            if max_scroll > 0:
                thumb_y = bar_y + (scroll_offset / max_scroll) * (bar_height - thumb_height)
            else:
                thumb_y = bar_y

            pygame.draw.rect(screen, (200, 200, 200), (bar_x, thumb_y, bar_width, thumb_height), border_radius=5)

            bar_width = 10
            bar_x = popup_rect.right - 15
            bar_y = popup_rect.top + 120
            bar_height = popup_rect.height - 150

            if content_height > 0:
                thumb_height = max(40, bar_height * (bar_height / content_height))
            else:
                thumb_height = bar_height

            if max_scroll > 0:
                thumb_y = bar_y + (scroll_offset / max_scroll) * (bar_height - thumb_height)
            else:
                thumb_y = bar_y

            thumb_rect = pygame.Rect(bar_x, thumb_y, bar_width, thumb_height)


        pygame.display.update()
        clock.tick(60)

    return None
