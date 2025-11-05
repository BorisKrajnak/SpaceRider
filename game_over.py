import json
import pygame
import subprocess
import sys
import time
import os

from music_manager import start_music
start_music()

# Funkcia na načítanie aktívnej hry z JSON
def load_game_config():
    try:
        with open("game_config.json", "r") as f:
            config = json.load(f)
            return config.get("active_game", "unknown")
    except FileNotFoundError:
        return "unknown"

def load_score():
    try:
        with open("skore.json", "r") as f:
            data = json.load(f)
            return data.get("skore", 0)
    except:
        return 0

def load_time():
    try:
        with open("skore.json", "r") as f:
            data = json.load(f)
            return data.get("cas", 0)
    except:
        return 0

def nacitaj_best_score(subor):
    try:
        with open(subor, "r") as f:
            data = json.load(f)
            return data.get("best", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

# Načítanie skóre a času
score = load_score()
cas = load_time()
best_score_raketka = nacitaj_best_score("best_score_raketka.json")
best_score_ufo = nacitaj_best_score("best_score_ufo.json")
active_game = load_game_config()

# Inicializácia pygame
pygame.init()
info = pygame.display.Info()
width, height = info.current_w, info.current_h
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game Over")

# Farby
WHITE = (255, 255, 255)
SPACE_BLUE = (10, 10, 40)
PURPLE = (31, 10, 30)

# Fonty
font_path = "Font/VOYAGER.ttf"
font = pygame.font.Font(font_path, 80)
button_font = pygame.font.Font(font_path, 50)
loading_font = pygame.font.Font(font_path, 200)

# Načítanie obrázkov
star_img = pygame.image.load("img/doplnky/star.png")
time_img = pygame.image.load("img/doplnky/time.png")
trofej_img = pygame.image.load("img/doplnky/trofej.png")

star_img = pygame.transform.scale(star_img, (60, 60))
time_img = pygame.transform.scale(time_img, (60, 60))
trofej_img = pygame.transform.scale(trofej_img, (50, 50))

# Funkcia na gradiet pozadie
def draw_vertical_gradient(surface, top_color, bottom_color):
    for y in range(surface.get_height()):
        ratio = y / surface.get_height()
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

# Funkcia na kreslenie tlačidla s prechodom
def draw_gradient_button(rect, color1, color2, text):
    button_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(button_surf, (r, g, b), (0, y), (rect.width, y))

    pygame.draw.rect(button_surf, WHITE, button_surf.get_rect(), 3, border_radius=10)
    screen.blit(button_surf, (rect.x, rect.y))

    text_surf = button_font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Zobrazenie úvodného textu
draw_vertical_gradient(screen, SPACE_BLUE, PURPLE)
welcome_text = loading_font.render("GAME OVER", True, WHITE)
screen.blit(welcome_text, (
    width // 2 - welcome_text.get_width() // 2,
    height // 2 - welcome_text.get_height() // 2
))
pygame.display.update()
time.sleep(0.5)

# Hlavný cyklus
running = True
while running:
    draw_vertical_gradient(screen, SPACE_BLUE, PURPLE)

    base_y = height // 3 - 100
    # Nadpis
    game_over_text = font.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, game_over_text.get_rect(center=(width // 2, base_y)))

    # BEST SCORE RAKETKA
    best_score_text = button_font.render(f"BEST SCORE RAKETKA: {best_score_raketka}", True, WHITE)
    screen.blit(best_score_text, (10, 10))
    trofej_rect1 = trofej_img.get_rect(midleft=(10 + best_score_text.get_width() + 15, 10 + best_score_text.get_height() // 2))
    screen.blit(trofej_img, trofej_rect1)

    # BEST SCORE UFO
    best_score_ufo_text = button_font.render(f"BEST SCORE UFO: {best_score_ufo}", True, WHITE)
    screen.blit(best_score_ufo_text, (10, 70))
    trofej_rect2 = trofej_img.get_rect(midleft=(10 + best_score_ufo_text.get_width() + 15, 70 + best_score_ufo_text.get_height() // 2))
    screen.blit(trofej_img, trofej_rect2)

    # SCORE + obrázok vpravo
    score_text = font.render(f"SCORE: {score}", True, WHITE)
    score_text_rect = score_text.get_rect()
    score_text_rect.center = (width // 2 - 50, base_y + 100)
    screen.blit(score_text, score_text_rect)

    star_img_scaled = pygame.transform.scale(star_img, (60, 60))
    star_rect = star_img_scaled.get_rect()
    star_rect.midleft = (score_text_rect.right + 2, score_text_rect.centery)
    screen.blit(star_img_scaled, star_rect)

    # TIME + obrázok vpravo
    cas_text = font.render(f"TIME: {cas}", True, WHITE)
    cas_text_rect = cas_text.get_rect()
    cas_text_rect.center = (width // 2 - 50, base_y + 180)
    screen.blit(cas_text, cas_text_rect)

    time_img_scaled = pygame.transform.scale(time_img, (60, 60))
    time_rect = time_img_scaled.get_rect()
    time_rect.midleft = (cas_text_rect.right + 2, cas_text_rect.centery)
    screen.blit(time_img_scaled, time_rect)

    # Tlačidlá
    btn_width, btn_height = 300, 70
    restart_button = pygame.Rect(width // 2 - 150, height // 2, btn_width, btn_height)
    settings_button = pygame.Rect(width // 2 - 150, height // 2 + 100, btn_width, btn_height)
    quit_button = pygame.Rect(width // 2 - 150, height // 2 + 200, btn_width, btn_height)

    draw_gradient_button(restart_button, SPACE_BLUE, PURPLE, "RESTART")
    draw_gradient_button(settings_button, SPACE_BLUE, PURPLE, "SETTINGS")
    draw_gradient_button(quit_button, SPACE_BLUE, PURPLE, "QUIT")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.collidepoint(event.pos):
                if active_game != "unknown":
                    subprocess.Popen(["python", f"{active_game}.py"], creationflags=subprocess.CREATE_NO_WINDOW)
                    time.sleep(0.5)
                    pygame.quit()
                    sys.exit()
            if quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
            if settings_button.collidepoint(event.pos):
                subprocess.Popen(["python", "nastavenia_hry.py"], creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(0.5)
                pygame.quit()
                sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_r:
                if active_game != "unknown":
                    subprocess.Popen(["python", f"{active_game}.py"], creationflags=subprocess.CREATE_NO_WINDOW)
                    time.sleep(0.5)
                    pygame.quit()
                    sys.exit()

    pygame.display.flip()

pygame.quit()
