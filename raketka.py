import json
import pygame
import sys
import os
import random
import subprocess
import time
from music_manager import toggle_music, set_volume, get_music_state, start_music, toggle_mute

from vyber_pozadia import nacitaj_pozadie


from music_manager import start_music
start_music()


# Funkcia na uloženie aktívnej hry do JSON
def save_game_config(game_name):
    # Skontroluj, či súbor existuje
    if not os.path.exists("game_config.json"):
        # Ak neexistuje, vytvor nový súbor s default hodnotou
        config = {"active_game": game_name}
        with open("game_config.json", "w") as f:
            json.dump(config, f, indent=4)
    else:
        # Ak súbor existuje, načítaj aktuálne nastavenia a uprav hodnotu
        with open("game_config.json", "r") as f:
            config = json.load(f)

        config["active_game"] = game_name  # Uprav hodnotu aktívnej hry

        # Ulož upravený config späť do súboru
        with open("game_config.json", "w") as f:
            json.dump(config, f, indent=4)


def uloz_best_score(score):
    try:
        with open("best_score_raketka.json", "r") as f:
            data = json.load(f)
            best = data.get("best", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        best = 0

    if score > best:
        with open("best_score_raketka.json", "w") as f:
            json.dump({"best": score}, f)


# Inicializácia Pygame
pygame.init()

# Nastavenie rozlíšenia na celé okno
info = pygame.display.Info()
width, height = info.current_w, info.current_h
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Raketka")
clock = pygame.time.Clock()

# Farby
WHITE = (255, 255, 255)
PURPLE = (31, 10, 30)
DARK_GRAY = (50, 50, 50)

# Načítanie pozadia
background = nacitaj_pozadie("game_config.json", width, height)

# Parametre raketky
player_width, player_height = 120, 120
player_speed = 10

# Načítanie snímkov animácie
player_frames = []
gif_folder = os.path.join("img", "raketka_frames")  # aktualizovaná cesta
frame_rate = 100
last_frame_time = pygame.time.get_ticks()
current_frame = 0

# Načítanie a otočenie snímkov
for filename in sorted(os.listdir(gif_folder)):
    frame = pygame.image.load(os.path.join(gif_folder, filename))
    frame = pygame.transform.scale(frame, (player_width, player_height))
    frame = pygame.transform.rotate(frame, -45)
    player_frames.append(frame)

# Načítanie obrázka meteoritu
meteor_image = pygame.image.load(os.path.join("img", "prekazky", "meteor.png")).convert_alpha()

# Trieda Meteor
class Meteor:
    def __init__(self):
        self.size = random.randint(40, 100)
        self.image = pygame.transform.scale(meteor_image, (self.size, self.size))
        self.x = width + self.size
        self.y = random.randint(0, height - self.size)
        self.speed = random.uniform(3.0, 8.0)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.x + self.size < 0

# Hlavná hra
def spusti_hru():
    global current_frame, last_frame_time

    player_x, player_y = width // 2, height // 2
    current_frame = 0
    last_frame_time = pygame.time.get_ticks()

    meteory = []
    spawn_delay = 1200
    last_spawn_time = pygame.time.get_ticks()
    running = True

    start_time = pygame.time.get_ticks()

    # Tlačidlo pre hudbu (v pravom hornom rohu)
    music_button_size = 60
    music_button_rect = pygame.Rect(width - music_button_size - 20, 20, music_button_size, music_button_size)

    font_path = "Font/VOYAGER.ttf"
    font = pygame.font.Font(font_path, 50)

    # --- HUD obrázky ---
    star_img = pygame.image.load(r"img/doplnky/star.png").convert_alpha()
    star_img = pygame.transform.scale(star_img, (45, 45))

    time_img = pygame.image.load(r"img/doplnky/time.png").convert_alpha()
    time_img = pygame.transform.scale(time_img, (45, 45))

    shield_image = pygame.image.load(os.path.join("img", "doplnky", "shield.png")).convert_alpha()
    shield_image = pygame.transform.scale(shield_image, (60, 60))

    shield_spawn_pos = None
    shield_spawn_time = pygame.time.get_ticks()
    shield_spawn_interval = random.randint(30000, 40000)
    shield_duration_on_map = 5000  # 5 sekúnd, kým štít zostane na mape
    has_shield = False  # hráč štít nemá
    shield_active = False  # či je štít aktívny

    shield_active_duration = 10000  # 10 sekúnd aktívny štít

    shield_end_time = 0
    shield_duration = 10000  # 10 sekúnd v ms

    max_bar_width = 300  # šírka progress baru
    bar_x, bar_y = 20, 160  # pozícia progress baru na obrazovke
    bar_height = 25

    base_speed = 3.0
    max_speed = 20.0
    min_spawn_delay = 400
    meteory_velkost_min = 40
    meteory_velkost_max = 100
    meteory_obehol = 0

    fuel = 100
    fuel_depletion_rate = 0.04
    fuel_bar_position = (20, 120)
    fuel_bar_size = (300, 25)

    fuel_spawn_time = 0
    fuel_duration = 5000
    fuel_pos = None
    fuel_size = 60

    hotbar_shields = []
    max_shields = 5

    fuel_image = pygame.image.load(os.path.join("img", "palivo", "fuel.png")).convert_alpha()
    fuel_image = pygame.transform.scale(fuel_image, (fuel_size, fuel_size))
    fuel_mask = pygame.mask.from_surface(fuel_image)

    def spawn_fuel():
        x = random.randint(fuel_size, width - fuel_size)
        y = random.randint(fuel_size, height - fuel_size)
        return (x, y)

    def spawn_shield():
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)
        return (x, y)

    # Hlavný cyklus
    while running:
        screen.blit(background, (0, 0))

        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        score = meteory_obehol + elapsed_time

        hud_x = 10
        hud_y = 10
        line_height = 55

        screen.blit(star_img, (hud_x, hud_y))
        score_surface = font.render(f"SCORE: {score}", True, (255, 255, 255))
        screen.blit(score_surface, (hud_x + 50, hud_y + 5))

        screen.blit(time_img, (hud_x, hud_y + line_height))
        time_surface = font.render(f"TIME: {elapsed_time}s", True, (255, 255, 255))
        screen.blit(time_surface, (hud_x + 50, hud_y + line_height + 5))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if music_button_rect.collidepoint(event.pos):  # Ovládanie hudby
                    # Pri kliknutí pravým tlačidlom - nastavenie štandardnej hlasitosti
                    if event.button == 3:  # Pravé tlačidlo myši
                        # Nastavenie štandardnej hlasitosti (0.5)
                        set_volume(0.5)
                        MUSIC_STATE = get_music_state()
                        MUSIC_STATE["muted"] = False
                    # Pri kliknutí ľavým tlačidlom - stlmenie/obnovenie
                    else:
                        toggle_mute()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if len(hotbar_shields) > 0 and not shield_active:
                        shield_active = True
                        shield_active_start = pygame.time.get_ticks()
                        shield_end_time = shield_active_start + shield_active_duration
                        hotbar_shields.pop(0)  # odstránime prvý štít (spotrebovaný)

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        hotbar_x = 20
        hotbar_y = height - 70
        hotbar_slot_size = 50
        hotbar_spacing = 10

        for i in range(len(hotbar_shields)):
            slot_rect = pygame.Rect(hotbar_x + i * (hotbar_slot_size + hotbar_spacing), hotbar_y, hotbar_slot_size,
                                    hotbar_slot_size)
            pygame.draw.rect(screen, (50, 50, 50), slot_rect, border_radius=10)  # pozadie slotu so zaoblením
            pygame.draw.rect(screen, (50, 50, 50), slot_rect, 1, border_radius=10)  # obrys slotu so zaoblením
            # ikonka štítu
            shield_icon_scaled = pygame.transform.scale(shield_image, (hotbar_slot_size - 10, hotbar_slot_size - 10))
            screen.blit(shield_icon_scaled, (slot_rect.x + 5, slot_rect.y + 5))

        if shield_active:
            remaining_time = max(0, shield_end_time - pygame.time.get_ticks())
            bar_width = int((remaining_time / shield_duration) * max_bar_width)
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, max_bar_width, bar_height))  # pozadie
            pygame.draw.rect(screen, (0, 100, 255), (bar_x, bar_y, bar_width, bar_height))  # aktívny progress
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, max_bar_width, bar_height), 2)  # obrys

        if shield_active and pygame.time.get_ticks() > shield_end_time:
            shield_active = False

        # --- Spawn štítu ---
        current_time = pygame.time.get_ticks()
        if shield_spawn_pos is None and current_time - shield_spawn_time > shield_spawn_interval:
            shield_spawn_pos = spawn_shield()
            shield_spawn_time = current_time

        # Ak štít je na mape, ale už vypršal čas, zmizne
        if shield_spawn_pos is not None and current_time - shield_spawn_time > shield_duration_on_map:
            shield_spawn_pos = None
            shield_spawn_time = current_time


        if elapsed_time % 5 == 0:
            base_speed = min(base_speed + 0.2, max_speed)
            spawn_delay = max(spawn_delay - 10, min_spawn_delay)
            meteory_velkost_max = min(meteory_velkost_max + 1, 160)



        keys = pygame.key.get_pressed()
        rotation_angle = 0
        if keys[pygame.K_w]:
            rotation_angle = +45
            player_y -= player_speed
        elif keys[pygame.K_s]:
            rotation_angle = -45
            player_y += player_speed
        else:
            rotation_angle = 0

        if keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_d]:
            player_x += player_speed

        # Obmedzenie pohybu na základe stredu raketky
        half_width = player_width // 2
        half_height = player_height // 2
        player_x = max(half_width, min(player_x, width - half_width))
        player_y = max(half_height - 30, min(player_y, height - half_height + 30))

        # Animácia raketky
        if pygame.time.get_ticks() - last_frame_time > frame_rate:
            current_frame = (current_frame + 1) % len(player_frames)
            last_frame_time = pygame.time.get_ticks()

        # Spawn meteorov
        if pygame.time.get_ticks() - last_spawn_time > spawn_delay:
            meteorit = Meteor()
            meteorit.size = random.randint(meteory_velkost_min, meteory_velkost_max)
            meteorit.image = pygame.transform.scale(meteor_image, (meteorit.size, meteorit.size))
            meteorit.x = width + meteorit.size
            meteorit.y = random.randint(0, height - meteorit.size)
            meteorit.speed = random.uniform(base_speed, base_speed + 5.0)
            meteorit.rect = pygame.Rect(meteorit.x, meteorit.y, meteorit.size, meteorit.size)
            meteorit.mask = pygame.mask.from_surface(meteorit.image)
            meteory.append(meteorit)
            last_spawn_time = pygame.time.get_ticks()

        # Kreslenie scény
        rotated_frame = pygame.transform.rotate(player_frames[current_frame], rotation_angle)
        frame_rect = rotated_frame.get_rect(center=(player_x, player_y))
        player_mask = pygame.mask.from_surface(rotated_frame)

        rotated_frame = pygame.transform.rotate(player_frames[current_frame], rotation_angle)
        frame_rect = rotated_frame.get_rect(center=(player_x, player_y))
        player_mask = pygame.mask.from_surface(rotated_frame)

        # --- Fuel mechanics ---
        fuel -= fuel_depletion_rate
        fuel = max(fuel, 0)
        if fuel == 0:
            final_score = meteory_obehol + elapsed_time
            with open("skore.json", "w") as f:
                json.dump({"skore": final_score, "cas": elapsed_time}, f)
            uloz_best_score(score)
            subprocess.Popen(["python", "game_over.py"], creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(0.5)
            running = False
            pygame.quit()
            sys.exit()

        current_time = pygame.time.get_ticks()
        if fuel_pos is None and current_time - fuel_spawn_time > 13500:
            fuel_pos = spawn_fuel()
            fuel_spawn_time = current_time
        elif fuel_pos is not None and current_time - fuel_spawn_time > fuel_duration:
            fuel_pos = None

        # Zobraz palivo a kontroluj kolíziu podľa masky (presný hitbox)
        if fuel_pos is not None:
            screen.blit(fuel_image, fuel_pos)
            fuel_rect = pygame.Rect(fuel_pos[0], fuel_pos[1], fuel_size, fuel_size)
            offset = (fuel_rect.left - frame_rect.left, fuel_rect.top - frame_rect.top)
            if player_mask.overlap(fuel_mask, offset):
                fuel = min(fuel + 30, 100)
                fuel_pos = None

        # --- Zobraz štít na mape ---
        if shield_spawn_pos is not None:
            screen.blit(shield_image, shield_spawn_pos)
            shield_rect = pygame.Rect(shield_spawn_pos[0], shield_spawn_pos[1], 50, 50)
            offset_shield = (shield_rect.left - frame_rect.left, shield_rect.top - frame_rect.top)
            if player_mask.overlap(pygame.mask.from_surface(shield_image), offset_shield):
                shield_spawn_pos = None
                shield_spawn_time = pygame.time.get_ticks()
                if len(hotbar_shields) < max_shields:
                    hotbar_shields.append(True)
            if player_mask.overlap(pygame.mask.from_surface(shield_image), offset_shield):
                has_shield = True
                shield_spawn_pos = None
                shield_spawn_time = pygame.time.get_ticks()

        # --- Ak je štít aktívny, zobraz ho okolo raketky ---
        if shield_active:
            # Napr. nakreslíme polopriesvitný kruh okolo hráča ako indikátor štítu
            shield_radius = max(player_width, player_height)
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 150, 255, 100), (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surface, (player_x - shield_radius, player_y - shield_radius))

        # --- Aktualizácia meteorov ---
        for meteor in meteory[:]:
            meteor.update()
            meteor.draw(screen)
            if meteor.is_off_screen():
                meteory.remove(meteor)
                meteory_obehol += 1

            # Kolízia meteoru s hráčom (len ak štít nie je aktívny)
            if not shield_active:
                offset = (meteor.rect.left - frame_rect.left, meteor.rect.top - frame_rect.top)
                if player_mask.overlap(meteor.mask, offset):
                    final_score = meteory_obehol + elapsed_time
                    with open("skore.json", "w") as f:
                        json.dump({"skore": final_score, "cas": elapsed_time}, f)
                    uloz_best_score(score)
                    subprocess.Popen(["python", "game_over.py"], creationflags=subprocess.CREATE_NO_WINDOW)
                    time.sleep(0.5)
                    running = False
                    pygame.quit()
                    sys.exit()

        # --- Zobrazenie progress baru (napr. pre štít alebo palivo) ---
        # Príklad: fuel bar
        pygame.draw.rect(screen, (255, 0, 0), (fuel_bar_position[0], fuel_bar_position[1], 300, 25))
        pygame.draw.rect(screen, (0, 255, 0), (fuel_bar_position[0], fuel_bar_position[1], int(3 * fuel), 25))

        # Kreslenie raketky
        screen.blit(rotated_frame, frame_rect.topleft)

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

        # Draw fuel bar
        if fuel > 60:
            fuel_color = (0, 255, 0)
        elif fuel > 30:
            fuel_color = (255, 165, 0)
        else:
            fuel_color = (255, 0, 0)

        pygame.draw.rect(screen, (50, 50, 50), (*fuel_bar_position, *fuel_bar_size))
        filled_width = int(fuel_bar_size[0] * (fuel / 100))
        pygame.draw.rect(screen, fuel_color,
                         (fuel_bar_position[0], fuel_bar_position[1], filled_width, fuel_bar_size[1]))
        pygame.draw.rect(screen, (255, 255, 255), (*fuel_bar_position, *fuel_bar_size), 2)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    spusti_hru()
