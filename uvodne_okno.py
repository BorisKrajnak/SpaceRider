import subprocess
import pygame
import sys
import time

# Inicializácia Pygame
pygame.init()
icon = pygame.image.load("favicon.png")
pygame.display.set_icon(icon)

from music_manager import start_music, toggle_music, set_volume, get_music_state, toggle_mute
start_music()

# Nastavenie veľkosti okna na celú obrazovku
info = pygame.display.Info()
width, height = info.current_w, info.current_h
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Space Rider")  # Názov okna

#Farby
WHITE = (255, 255, 255)
SPACE_BLUE = (10, 10, 40)
DARK_GRAY = (169, 169, 169)
PURPLE = (31, 10, 30)

def draw_vertical_gradient(surface, top_color, bottom_color):
    for y in range(surface.get_height()):
        ratio = y / surface.get_height()
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))


# Načítanie vlastného fontu pre nadpis (názov hry)
font_path = "Font/VOYAGER.ttf"  # cesta k fontu
font_size = 175  # veľkosť písma
title_font = pygame.font.Font(font_path, font_size)  # Tento font sa použije iba pre nadpis

# Pôvodný font pre ostatné texty
font = pygame.font.SysFont("Arial", 40, bold=True)
small_font = pygame.font.SysFont("Arial", 28)
loading_font = pygame.font.Font(font_path, 200)

#Welcome
draw_vertical_gradient(screen, SPACE_BLUE, PURPLE)
welcome_text = loading_font.render("WELCOME", True, WHITE)
screen.blit(welcome_text, (
    width // 2 - welcome_text.get_width() // 2,
    height // 2 - welcome_text.get_height() // 2
))
pygame.display.update()
time.sleep(0.5)


# Načítanie obrázka pozadia
try:
    background_img = pygame.image.load(r"img/pozadie_uvodne_okno.jpg")
    background_img = pygame.transform.scale(background_img, (int(background_img.get_width()), int(background_img.get_height())))
except Exception as e:
    print(f"Chyba pri načítaní obrázka: {e}")
    background_img = None

# Parametre pre tlačidlá
button_width = 250
button_height = 75
border_radius = 7

# Nastavenie pozície tlačidiel
padding = 150
quit_button_rect = pygame.Rect(padding, height - button_height - padding, button_width, button_height)
rules_button_rect = pygame.Rect((width - button_width) // 2, height - button_height - padding, button_width, button_height)
next_button_rect = pygame.Rect(width - button_width - padding, height - button_height - padding, button_width, button_height)

# Tlačidlo pre hudbu (v pravom hornom rohu)
music_button_size = 60
music_button_rect = pygame.Rect(width - music_button_size - 20, 20, music_button_size, music_button_size)

# Text tlačidiel
quit_button_text = font.render("QUIT", True, WHITE)  # Tlačidlo "QUIT"
next_button_text = font.render("NEXT", True, WHITE)  # Tlačidlo "NEXT"
rules_button_text = font.render("RULES", True, WHITE)  # Tlačidlo "RULES"

# Určenie pozície textu v tlačidlách
quit_button_text_rect = quit_button_text.get_rect(center=quit_button_rect.center)
next_button_text_rect = next_button_text.get_rect(center=next_button_rect.center)
rules_button_text_rect = rules_button_text.get_rect(center=rules_button_rect.center)

# Nadpis (názov hry) s vlastným fontom
title_text = title_font.render("SPACE     RIDER", True, WHITE)

# Premenná na sledovanie, či sú pravidlá zobrazené
showing_rules = False


def draw_vertical_gradient(surface, rect, top_color, bottom_color, border_radius=0):
    """Nakreslí vertikálny gradient do zadaného rectu na surface."""
    x, y, w, h = rect
    for i in range(h):
        # Interpolácia medzi top a bottom color
        ratio = i / h
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))

    # Rám so zaoblením (teraz na vonkajšej strane)
    popup_rect_outer = pygame.Rect(rect.left - 3, rect.top - 3, rect.width + 6, rect.height + 6)
    pygame.draw.rect(surface, DARK_GRAY, popup_rect_outer, width=3, border_radius=border_radius)


def draw_rules_popup():
    # Veľkosť a pozícia popupu
    popup_width, popup_height = 800, 500
    popup_rect = pygame.Rect((width - popup_width) // 2, (height - popup_height) // 2, popup_width, popup_height)

    # Gradient pozadie (tmavo fialová → tmavomodrá)
    draw_vertical_gradient(screen, popup_rect, SPACE_BLUE, PURPLE, border_radius=10)

    # Nadpis
    heading = "PRAVIDLÁ HRY"
    heading_surface = font.render(heading, True, WHITE)
    heading_rect = heading_surface.get_rect(center=(popup_rect.centerx, popup_rect.top + 60))
    screen.blit(heading_surface, heading_rect)

    # Pravidlá – riadky
    rules_lines = [
        "",
        "Cieľom je prežiť čo najdlhšie vo vesmíre a získať maximálne skóre.",
        "Na ďalšej obrazovke si vyberáš mapu, alebo to necháš na náhodu.",
        "Vyber si svoj charakter – raketku, UFO.",
        "Obe majú svoj jedinečný štýl ovládania – zvládneš ich obe?",
        "V ceste ti budú stáť prekážky, nepriatelia a vesmírne pasce.",
        "Zbieraj body, palivo a power-upy pre lepšiu šancu na prežitie.",
        "Hra končí, keď narazíš, stratíš životy alebo palivo.",
        'Niektoré power-upy sú dočasné = využi ich múdro – aktivuj ich stlačením "E"',
        "Ovládanie: WASD alebo gamepad (ak je pripojený) :D :D :D"
    ]

    # Výpočet vertikálneho zarovnania pre pravidlá
    total_text_height = len(rules_lines) * 40  # výška všetkých riadkov
    start_y = popup_rect.top + (popup_rect.height - total_text_height) // 1.5  # začiatok v vertikálnom strede

    # Vykreslenie textu pravidiel do stredu
    for i, line in enumerate(rules_lines):
        text = small_font.render(line, True, WHITE)
        text_rect = text.get_rect(center=(popup_rect.centerx, start_y + i * 40))
        screen.blit(text, text_rect)


# Hlavná slučka hry
running = True
while running:
    # Skenovanie udalostí
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Ukončí hru, ak sa zavrie okno
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if showing_rules:
                    showing_rules = False # Zatvorenie pravidiel pomocou ESC
                else:
                    running = False # Ukončí hru, ak sa stlačí ESC
        if event.type == pygame.MOUSEBUTTONDOWN:
            if quit_button_rect.collidepoint(event.pos):  # Ak klikneš na "QUIT"
                running = False
            elif next_button_rect.collidepoint(event.pos):  # Ak klikneš na "NEXT"
                subprocess.Popen(["python", "nastavenia_hry.py"], creationflags=subprocess.CREATE_NO_WINDOW) # Toto potlačí okno príkazového riadku
                time.sleep(0.5)
                running = False
                pygame.quit()
                sys.exit()
            elif rules_button_rect.collidepoint(event.pos):  # Ak klikneš na "RULES"
                showing_rules = not showing_rules  # Toggle (prepínač) pre zobrazenie/skrytie pravidiel
            elif music_button_rect.collidepoint(event.pos):  # Ovládanie hudby
                # Pri kliknutí pravým tlačidlom - nastavenie štandardnej hlasitosti
                if event.button == 3:  # Pravé tlačidlo myši
                    # Nastavenie štandardnej hlasitosti (0.5)
                    set_volume(0.5)
                    MUSIC_STATE = get_music_state()
                    MUSIC_STATE["muted"] = False
                # Pri kliknutí ľavým tlačidlom - stlmenie/obnovenie
                else:
                    toggle_mute()

    # Vykreslenie pozadia hry
    if background_img:
        screen.blit(background_img, ((width - background_img.get_width()) // 2, (height - background_img.get_height()) // 4))  # Ak existuje obrázok, vykreslí ho
    else:
        screen.fill((0, 0, 0))  # Ak nie, vyplní obrazovku čiernou farbou

    # Vykreslenie tlačidiel na obrazovke
    draw_vertical_gradient(screen, quit_button_rect, SPACE_BLUE, PURPLE, border_radius)
    draw_vertical_gradient(screen, next_button_rect, SPACE_BLUE, PURPLE, border_radius)
    draw_vertical_gradient(screen, rules_button_rect, SPACE_BLUE, PURPLE, border_radius)

    # Vykreslenie tlačidla pre hudbu
    music_state = get_music_state()
    music_color = PURPLE if not music_state["muted"] else DARK_GRAY
    pygame.draw.circle(screen, music_color, music_button_rect.center, music_button_size // 2)
    pygame.draw.circle(screen, WHITE, music_button_rect.center, music_button_size // 2, 2)  # Obrys

    # Ikona hudby v tlačidle - dve paličky
    bar_width = 5
    bar_height = music_button_size // 3
    spacing = 10
    center_x = music_button_rect.centerx
    center_y = music_button_rect.centery

    # Prvá palička
    left_bar_x = center_x - spacing // 2 - bar_width
    pygame.draw.rect(screen, WHITE, (left_bar_x, center_y - bar_height // 2, bar_width, bar_height))

    # Druhá palička
    right_bar_x = center_x + spacing // 2
    pygame.draw.rect(screen, WHITE, (right_bar_x, center_y - bar_height // 2, bar_width, bar_height))

    # Indikátor stlmenia - ak je stlmené, prekrížiť paličky
    if music_state["muted"]:
        slash_length = music_button_size // 3
        slash_width = 3
        # Diagonálna čiara cez ikonu
        pygame.draw.line(screen, WHITE, 
                        (center_x - slash_length, center_y - slash_length),
                        (center_x + slash_length, center_y + slash_length), slash_width)

    # Zobrazenie textu na tlačidlách
    screen.blit(quit_button_text, quit_button_text_rect)
    screen.blit(next_button_text, next_button_text_rect)
    screen.blit(rules_button_text, rules_button_text_rect)

    # Zobrazenie nadpisu (názov hry) s vlastným fontom
    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 150))  # Názov hry

    # Zobrazenie pravidiel, ak sú zvolené
    if showing_rules:
        draw_rules_popup()

    # Aktualizácia obrazovky
    pygame.display.update()  # Prekreslí obrazovku s novými prvkami

# Ukončenie Pygame
pygame.quit()
sys.exit()
