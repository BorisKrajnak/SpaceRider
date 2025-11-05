# --- Načítanie knižníc ---
import json
import pygame
import sys
import os
import random
import subprocess
import time
from music_manager import toggle_music, set_volume, get_music_state, start_music, toggle_mute
from vyber_pozadia import nacitaj_pozadie

start_music()

def save_game_config(game_name):
    if not os.path.exists("game_config.json"):
        config = {"active_game": game_name}
        with open("game_config.json", "w") as f:
            json.dump(config, f, indent=4)
    else:
        with open("game_config.json", "r") as f:
            config = json.load(f)
        config["active_game"] = game_name
        with open("game_config.json", "w") as f:
            json.dump(config, f, indent=4)

#Uloží skóre a čas do súboru skore.json
def save_score(score, elapsed_time):
    data = {"skore": score, "cas": int(elapsed_time)}
    with open("skore.json", "w") as f:
        json.dump(data, f, indent=4)

#Porovná aktuálne skóre s najlepším a ak je vyššie, uloží ho
def uloz_best_score(score):
    try:
        with open("best_score_ufo.json", "r") as f:
            data = json.load(f)
            best = data.get("best", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        best = 0

    if score > best:
        with open("best_score_ufo.json", "w") as f:
            json.dump({"best": score}, f)

# --- Inicializácia Pygame ---
pygame.init()
info = pygame.display.Info()
width, height = info.current_w, info.current_h
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("UFO")

# Farby
WHITE = (255, 255, 255)
PURPLE = (31, 10, 30)
DARK_GRAY = (50, 50, 50)

# Tlačidlo pre hudbu (v pravom hornom rohu)
music_button_size = 60
music_button_rect = pygame.Rect(width - music_button_size - 20, 20, music_button_size, music_button_size)

# --- Farby ---
LIGHT_BLUE = (173, 216, 230)

# --- Pozadie a fonty ---
background = nacitaj_pozadie("game_config.json", width, height)
font = pygame.font.Font("Font/VOYAGER.ttf", 40)

# --- Načítanie obrázkov ---
star_img = pygame.transform.scale(pygame.image.load(r"img/doplnky/star.png"), (45, 45))
time_img = pygame.transform.scale(pygame.image.load(r"img/doplnky/time.png"), (45, 45))
barrel_img = pygame.image.load(r"img/palivo/barrel_ufo.png")
meteor_img = pygame.image.load(r"img/prekazky/meteor2.png")
shield_img = pygame.image.load(r"img/doplnky/shield.png")
heart_img = pygame.transform.scale(pygame.image.load(r"img/doplnky/heart.png"), (40, 40))

# --- UFO ---
def nacitaj_animaciu(cesta, x, y, scale=0.25):
    frames = []
    for filename in sorted(os.listdir(cesta)):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image = pygame.image.load(os.path.join(cesta, filename)).convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width()*scale), int(image.get_height()*scale)))
            rect = image.get_rect(center=(x, y))
            frames.append((image, rect))
    return frames

ufo_x, ufo_y = width // 2, height // 2
ufo_speed, gravity = 0, 0.5
jump_strength, move_speed = -10, 5
ufo_frames = nacitaj_animaciu("img/ufo_frames", ufo_x, ufo_y)
ufo_width, ufo_height = ufo_frames[0][0].get_size()

# --- Palivo ---
fuel, max_fuel = 100, 100
fuel_depletion_rate = 0.2
last_fuel_update = pygame.time.get_ticks()


class Barrel:
    def __init__(self):
        self.size = 30
        self.image = pygame.transform.scale(barrel_img, (self.size, self.size))
        self.x = width + self.size
        self.y = random.randint(0, height - self.size)
        self.speed = random.uniform(3, 6)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self): self.x -= self.speed; self.rect.x = int(self.x)
    def draw(self): screen.blit(self.image, (self.x, self.y))
    def is_off_screen(self): return self.x < -self.size

# --- Meteory ---
class Meteor:
    def __init__(self, speed_multiplier):
        self.size = random.randint(40, 100)
        self.image = pygame.transform.rotate(pygame.transform.scale(meteor_img, (self.size, self.size)), -45)
        self.x, self.y = width + self.image.get_width(), random.randint(0, height - self.image.get_height())
        self.speed = random.uniform(6, 12) * speed_multiplier
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.mask = pygame.mask.from_surface(self.image)
    def update(self): self.x -= self.speed; self.rect.x = int(self.x)
    def draw(self): screen.blit(self.image, (self.x, self.y))
    def is_off_screen(self): return self.x + self.image.get_width() < 0

# --- Shield ---
class Shield:
    def __init__(self):
        self.size = 30
        self.image = pygame.transform.scale(shield_img, (self.size, self.size))
        self.x = width + self.size
        self.y = random.randint(0, height - self.size)
        self.speed = 4
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self): self.x -= self.speed; self.rect.x = int(self.x)
    def draw(self): screen.blit(self.image, (self.x, self.y))
    def is_off_screen(self): return self.x < -self.size

# --- Heart ---
class Heart:
    def __init__(self):
        self.size = 30
        self.image = heart_img
        self.x = width + self.size
        self.y = random.randint(0, height - self.size)
        self.speed = 3
        self.rect = pygame.Rect(self.x, self.y, 40, 40)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self): self.x -= self.speed; self.rect.x = int(self.x)
    def draw(self): screen.blit(self.image, (self.x, self.y))
    def is_off_screen(self): return self.x < -self.size

# --- Stav ---
save_game_config("ufo")
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
frame_index, last_update, frame_delay = 0, pygame.time.get_ticks(), 70
meteory, barrels, shields, hearts = [], [], [], []
shield_icons, heart_icons = [], []
shield_active = False
shield_start_time = 0
max_shields, max_hearts = 3, 3
spawn_delay = 500
last_spawn_time = last_barrel_spawn = last_shield_spawn = last_heart_spawn = pygame.time.get_ticks()
meteory_prelietane = 0

# --- Najlepšie skóre ---
try:
    with open("best_score_ufo.json", "r") as f: best_score = json.load(f).get("best", 0)
except: best_score = 0

running = True
while running:
    screen.blit(background, (0, 0))
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - start_time) // 1000
    current_score = meteory_prelietane + elapsed_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                ufo_speed = jump_strength
            if event.type == pygame.MOUSEBUTTONDOWN and music_button_rect.collidepoint(event.pos):  # Ovládanie hudbyAdd commentMore actions

                if event.button == 3:  # Pravé tlačidlo myši
                    # Nastavenie štandardnej hlasitosti (0.5)
                    set_volume(0.5)
                    MUSIC_STATE = get_music_state()
                    MUSIC_STATE["muted"] = False
                # Pri kliknutí ľavým tlačidlom - stlmenie/obnovenie
                else:
                    toggle_mute()
            if event.key == pygame.K_e and shield_icons and not shield_active:
                shield_icons.pop()
                shield_active = True
                shield_start_time = current_time
        if event.type == pygame.MOUSEBUTTONDOWN and music_button_rect.collidepoint(event.pos):
            if event.button == 3:
                set_volume(0.5); get_music_state()["muted"] = False
            else:
                toggle_mute()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: ufo_x -= move_speed
    if keys[pygame.K_d]: ufo_x += move_speed

    ufo_speed += gravity
    ufo_y += ufo_speed
    ufo_x = max(0, min(ufo_x, width - ufo_width))
    ufo_y = max(0, min(ufo_y, height - ufo_height))
    if ufo_y == height - ufo_height: ufo_speed = 0

    if current_time - last_fuel_update > 100:
        fuel -= fuel_depletion_rate
        last_fuel_update = current_time
        if fuel <= 0:
            save_score(current_score, elapsed_time)
            uloz_best_score(current_score)
            subprocess.Popen(["python", "game_over.py"], creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(0.5); pygame.quit(); sys.exit()

    if current_time - last_update > frame_delay:
        frame_index = (frame_index + 1) % len(ufo_frames)
        last_update = current_time

    current_ufo_image = ufo_frames[frame_index][0]
    screen.blit(current_ufo_image, (ufo_x, ufo_y))
    ufo_rect = current_ufo_image.get_rect(topleft=(ufo_x, ufo_y))
    ufo_mask = pygame.mask.from_surface(current_ufo_image)

    # Vykreslenie tlačidla pre hudbuAdd commentMore actions
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

    # HUD
    screen.blit(star_img, (10, 10))
    screen.blit(font.render(f"SCORE: {current_score}", True, WHITE), (60, 15))
    screen.blit(time_img, (10, 65))
    screen.blit(font.render(f"TIME: {elapsed_time}s", True, WHITE), (60, 70))
    fuel_ratio = fuel / max_fuel
    pygame.draw.rect(screen, (0, 0, 0), (10, 125, 234, 44))
    pygame.draw.rect(screen,
                     (0, 255, 0) if fuel_ratio >= 0.65 else (255, 165, 0) if fuel_ratio >= 0.25 else (255, 0, 0),
                     (20, 135, int(214 * fuel_ratio), 24))

    # --- Veľkosť štítov a pozícia v ľavom dolnom rohu ---
    hotbar_slot_size = 50  # môžeš upraviť podľa potreby
    shield_icon_size = hotbar_slot_size - 10
    shield_icon_scaled = pygame.transform.scale(shield_img, (shield_icon_size, shield_icon_size))

    for i in range(len(shield_icons)):
        x = 10 + i * (shield_icon_size + 5)  # medzera medzi ikonami
        y = height - shield_icon_size - 10  # 10 px od spodného okraja
        screen.blit(shield_icon_scaled, (x, y))

    for i, icon in enumerate(heart_icons):
        screen.blit(heart_img, (20 + i * 45, 180))

    if shield_active:
        pygame.draw.circle(screen, LIGHT_BLUE, ufo_rect.center, max(ufo_width, ufo_height), 4)
        if current_time - shield_start_time > 10000:
            shield_active = False
        else:
            shield_left = 10 - (current_time - shield_start_time)//1000
            pygame.draw.rect(screen, LIGHT_BLUE, (width//2 - 100, 30, int(200 * shield_left / 10), 20))

    # Spawny
    if current_time - last_spawn_time > max(300, spawn_delay - (elapsed_time * 10)):
        meteory.append(Meteor(1 + (elapsed_time//30) * 0.2))
        last_spawn_time = current_time
    if current_time - last_barrel_spawn > 10000:
        barrels.append(Barrel()); last_barrel_spawn = current_time
    if current_time - last_shield_spawn > 20000:
        shields.append(Shield()); last_shield_spawn = current_time
    if current_time - last_heart_spawn > 25000:
        hearts.append(Heart()); last_heart_spawn = current_time

    for meteor in meteory[:]:
        meteor.update()
        if meteor.is_off_screen(): meteory.remove(meteor); meteory_prelietane += 1; continue
        if not shield_active:
            offset = (int(meteor.x - ufo_rect.left), int(meteor.y - ufo_rect.top))
            if ufo_mask.overlap(meteor.mask, offset):
                if heart_icons:
                    heart_icons.pop()
                    meteory.remove(meteor)
                    continue
                save_score(current_score, elapsed_time); uloz_best_score(current_score)
                subprocess.Popen(["python", "game_over.py"], creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(0.5); pygame.quit(); sys.exit()
        meteor.draw()

    for barrel in barrels[:]:
        barrel.update()
        if barrel.is_off_screen(): barrels.remove(barrel); continue
        offset = (int(barrel.x - ufo_rect.left), int(barrel.y - ufo_rect.top))
        if ufo_mask.overlap(barrel.mask, offset):
            fuel = min(max_fuel, fuel + 15)
            barrels.remove(barrel)
            continue
        barrel.draw()

    for shield in shields[:]:
        shield.update()
        if shield.is_off_screen(): shields.remove(shield); continue
        offset = (int(shield.x - ufo_rect.left), int(shield.y - ufo_rect.top))
        if ufo_mask.overlap(shield.mask, offset) and len(shield_icons) < max_shields:
            shield_icons.append(True); shields.remove(shield)
            continue
        shield.draw()

    for heart in hearts[:]:
        heart.update()
        if heart.is_off_screen(): hearts.remove(heart); continue
        offset = (int(heart.x - ufo_rect.left), int(heart.y - ufo_rect.top))
        if ufo_mask.overlap(heart.mask, offset) and len(heart_icons) < max_hearts:
            heart_icons.append(True); hearts.remove(heart)
            continue
        heart.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
