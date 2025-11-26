# screens/ufo.py
import os
import json
import random
import time
import pygame

from core.config import get_path
from core.music_manager import start_music, set_volume, get_music_state, toggle_mute
from core.game_state import GameState
from screens.vyber_pozadia import nacitaj_pozadie

# --- Konštanty (podobne ako v raketka.py) ---
UFO_WIDTH = 120
UFO_HEIGHT = 120
UFO_SPEED = 5
GRAVITY = 0.5
JUMP_STRENGTH = -10
FRAME_RATE_MS = 70

# --- Pomocné funkcie pre ukladanie skóre / config ---
def save_score_file(score, elapsed_time):
    path = get_path("data", "skore.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"skore": score, "cas": int(elapsed_time)}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def uloz_best_score_ufo(score):
    path = get_path("data", "best_score_ufo.json")
    best = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            best = json.load(f).get("best", 0)
    except Exception:
        best = 0
    if score > best:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"best": score}, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

def save_game_config(game_name):
    cfg = {}
    cfg_path = get_path("data", "game_config.json")
    try:
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
    except Exception:
        cfg = {}
    cfg["active_game"] = game_name
    try:
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

# --- Triedy pre objekty ---
class Barrel:
    def __init__(self, screen_w, screen_h, image):
        self.size = 30
        self.image = pygame.transform.scale(image, (self.size, self.size))
        self.x = screen_w + self.size
        self.y = random.randint(0, screen_h - self.size)
        self.speed = random.uniform(3, 6)
        self.rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    def is_off_screen(self):
        return self.x < -self.size

class Meteor:
    def __init__(self, screen_w, screen_h, image, speed_multiplier=1.0):
        self.size = random.randint(40, 100)
        self.image = pygame.transform.rotate(pygame.transform.scale(image, (self.size, self.size)), -45)
        self.x = screen_w + self.image.get_width()
        self.y = random.randint(0, screen_h - self.image.get_height())
        self.speed = random.uniform(6, 12) * speed_multiplier
        self.rect = pygame.Rect(int(self.x), int(self.y), self.image.get_width(), self.image.get_height())
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    def is_off_screen(self):
        return self.x + self.image.get_width() < 0

class ShieldPickup:
    def __init__(self, screen_w, screen_h, image):
        self.size = 30
        self.image = pygame.transform.scale(image, (self.size, self.size))
        self.x = screen_w + self.size
        self.y = random.randint(0, screen_h - self.size)
        self.speed = 4
        self.rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    def is_off_screen(self):
        return self.x < -self.size

class HeartPickup:
    def __init__(self, screen_w, screen_h, image):
        self.size = 30
        self.image = pygame.transform.scale(image, (40, 40))
        self.x = screen_w + self.size
        self.y = random.randint(0, screen_h - self.size)
        self.speed = 3
        self.rect = pygame.Rect(int(self.x), int(self.y), 40, 40)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    def is_off_screen(self):
        return self.x < -self.size

# --- UFO (hráč) ---
class PlayerUFO:
    def __init__(self, frames, x, y):
        self.frames = frames
        self.frame_index = 0
        self.last_frame = pygame.time.get_ticks()
        self.frame_delay = FRAME_RATE_MS
        self.x = float(x)
        self.y = float(y)
        self.speed_y = 0.0
        self.move_speed = UFO_SPEED
        self.width, self.height = frames[0].get_size()
        # shield
        self.shield_active = False
        self.shield_start = 0
        self.shield_duration = 10000
        base = max(self.width, self.height)
        self.shield_radius = int(base * 1.0)  # pevná veľkosť štítu

    def update_anim(self):
        now = pygame.time.get_ticks()
        if now - self.last_frame > self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_frame = now

    def apply_physics(self):
        self.speed_y += GRAVITY
        self.y += self.speed_y
        # clamp later in main

    def flap(self):
        self.speed_y = JUMP_STRENGTH

    def draw(self, screen):
        current = self.frames[self.frame_index]
        screen.blit(current, (int(self.x), int(self.y)))
        rect = current.get_rect(topleft=(int(self.x), int(self.y)))
        mask = pygame.mask.from_surface(current)
        # draw shield visual if active
        if self.shield_active:
            surf = pygame.Surface((self.shield_radius * 2, self.shield_radius * 2), pygame.SRCALPHA)
            pulse = 10 * abs((pygame.time.get_ticks() // 150) % 2 - 1)
            pygame.draw.circle(surf, (0,170,255,80 + pulse), (self.shield_radius, self.shield_radius), self.shield_radius)
            screen.blit(surf, (int(self.x + self.width/2 - self.shield_radius), int(self.y + self.height/2 - self.shield_radius)))
        return rect, mask

    def activate_shield(self):
        self.shield_active = True
        self.shield_start = pygame.time.get_ticks()

    def update_shield(self):
        if self.shield_active and (pygame.time.get_ticks() - self.shield_start > self.shield_duration):
            self.shield_active = False

# ---------------------------------------------------------
#  run(screen) — hlavný modul (vráti GameState)
# ---------------------------------------------------------
def run(screen):
    start_music()
    save_game_config("ufo")

    width, height = screen.get_size()
    clock = pygame.time.Clock()

    # načítanie background podľa configu
    config_path = get_path("data", "game_config.json")
    try:
        background = nacitaj_pozadie(config_path, width, height)
    except Exception:
        background = None

    # načítanie fontu
    font_path = get_path("assets", "Font", "VOYAGER.ttf")
    try:
        font = pygame.font.Font(font_path, 40)
    except Exception:
        font = pygame.font.SysFont("Arial", 40)

    # načítanie obrázkov
    def load_img(*parts):
        p = get_path("assets", "img", *parts)
        if os.path.exists(p):
            return pygame.image.load(p).convert_alpha()
        return None

    star_img = load_img("doplnky", "star.png")
    time_img = load_img("doplnky", "time.png")
    barrel_img = load_img("palivo", "barrel_ufo.png")
    meteor_img = load_img("prekazky", "meteor2.png")
    shield_img = load_img("doplnky", "shield.png")
    heart_img = load_img("doplnky", "heart.png")

    # fallback placeholders
    if star_img is None: star_img = pygame.Surface((45,45), pygame.SRCALPHA)
    if time_img is None: time_img = pygame.Surface((45,45), pygame.SRCALPHA)
    if barrel_img is None: barrel_img = pygame.Surface((30,30), pygame.SRCALPHA)
    if meteor_img is None:
        meteor_img = pygame.Surface((60,60), pygame.SRCALPHA)
        pygame.draw.circle(meteor_img, (150,150,150), (30,30), 30)
    if shield_img is None: shield_img = pygame.Surface((30,30), pygame.SRCALPHA)
    if heart_img is None:
        heart_img = pygame.Surface((40,40), pygame.SRCALPHA)
        pygame.draw.circle(heart_img, (255,100,100), (20,20), 20)

    # načítanie animácie ufo frames
    frames_folder = get_path("assets","img","ufo_frames")
    ufo_frames = []
    if os.path.exists(frames_folder):
        for fn in sorted(os.listdir(frames_folder)):
            if fn.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    im = pygame.image.load(os.path.join(frames_folder, fn)).convert_alpha()
                    im = pygame.transform.scale(im, (UFO_WIDTH, UFO_HEIGHT))
                    ufo_frames.append(im)
                except Exception:
                    pass
    if not ufo_frames:
        surf = pygame.Surface((UFO_WIDTH, UFO_HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (80,200,200), surf.get_rect())
        ufo_frames = [surf]

    # player
    player = PlayerUFO(ufo_frames, width//2 - UFO_WIDTH//2, height//2 - UFO_HEIGHT//2)

    # herné objekty
    meteors = []
    barrels = []
    shields = []
    hearts = []
    shield_icons = []
    heart_icons = []

    # stav a časovače
    start_time = pygame.time.get_ticks()
    last_frame = pygame.time.get_ticks()
    last_spawn = pygame.time.get_ticks()
    last_barrel_spawn = pygame.time.get_ticks()
    last_shield_spawn = pygame.time.get_ticks()
    last_heart_spawn = pygame.time.get_ticks()
    last_fuel_update = pygame.time.get_ticks()

    spawn_delay = 500
    meteory_prelietane = 0

    # fuel
    fuel = 100.0
    max_fuel = 100.0
    fuel_depletion_rate = 0.2

    max_shields = 3
    max_hearts = 3

    music_button_size = 60
    music_button_rect = pygame.Rect(width - music_button_size - 20, 20, music_button_size, music_button_size)

    # načítanie best score
    try:
        best_score = json.load(open(get_path("data","best_score_ufo.json"),"r")).get("best",0)
    except Exception:
        best_score = 0

    running = True
    while running:
        now = pygame.time.get_ticks()
        elapsed_time = (now - start_time) // 1000
        current_score = meteory_prelietane + elapsed_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameState.MENU
                if event.key == pygame.K_w:
                    player.flap()
                if event.key == pygame.K_e and shield_icons and not player.shield_active:
                    shield_icons.pop()
                    player.activate_shield()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if music_button_rect.collidepoint(event.pos):
                    if event.button == 3:
                        set_volume(0.5)
                        get_music_state()["muted"] = False
                    else:
                        toggle_mute()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.x -= player.move_speed
        if keys[pygame.K_d]:
            player.x += player.move_speed

        # apply physics
        player.apply_physics()
        player.update_anim()
        player.update_shield()

        # clamp player to screen
        player.x = max(0, min(player.x, width - player.width))
        player.y = max(0, min(player.y, height - player.height))
        if player.y >= height - player.height:
            player.speed_y = 0

        # fuel depletion
        if now - last_fuel_update > 100:
            fuel -= fuel_depletion_rate
            last_fuel_update = now
            if fuel <= 0:
                # save score and goto game over
                save_score_file(current_score, elapsed_time)
                uloz_best_score_ufo(current_score)
                return GameState.GAME_OVER

        # spawn meteors (becomes faster with time)
        if now - last_spawn > max(300, spawn_delay - (elapsed_time * 10)):
            meteors.append(Meteor(width, height, meteor_img, 1 + (elapsed_time//30)*0.2))
            last_spawn = now

        # spawn barrel (fuel)
        if now - last_barrel_spawn > 10000:
            barrels.append(Barrel(width, height, barrel_img))
            last_barrel_spawn = now

        # spawn shield pickup
        if now - last_shield_spawn > 20000:
            shields.append(ShieldPickup(width, height, shield_img))
            last_shield_spawn = now

        # spawn heart pickup
        if now - last_heart_spawn > 25000:
            hearts.append(HeartPickup(width, height, heart_img))
            last_heart_spawn = now

        # update meteors and collisions
        for m in meteors[:]:
            m.update()
            if m.is_off_screen():
                meteors.remove(m)
                meteory_prelietane += 1
                continue
            # collision if no shield
            # compute offset from player rect (player draw not yet called, so create current frame rect)
            player_frame = player.frames[player.frame_index]
            player_rect = player_frame.get_rect(topleft=(int(player.x), int(player.y)))
            player_mask = pygame.mask.from_surface(player_frame)
            if not player.shield_active:
                offset = (int(m.rect.x - player_rect.left), int(m.rect.y - player_rect.top))
                if player_mask.overlap(m.mask, offset):
                    # if have hearts -> remove heart instead of dying
                    if heart_icons:
                        heart_icons.pop()
                        try:
                            meteors.remove(m)
                        except ValueError:
                            pass
                        continue
                    save_score_file(current_score, elapsed_time)
                    uloz_best_score_ufo(current_score)
                    return GameState.GAME_OVER

        # barrels collisions
        for b in barrels[:]:
            b.update()
            if b.is_off_screen():
                barrels.remove(b)
                continue
            player_frame = player.frames[player.frame_index]
            player_rect = player_frame.get_rect(topleft=(int(player.x), int(player.y)))
            player_mask = pygame.mask.from_surface(player_frame)
            offset = (int(b.rect.x - player_rect.left), int(b.rect.y - player_rect.top))
            if player_mask.overlap(b.mask, offset):
                fuel = min(max_fuel, fuel + 15)
                try:
                    barrels.remove(b)
                except ValueError:
                    pass

        # shield pickups collisions
        for s in shields[:]:
            s.update()
            if s.is_off_screen():
                shields.remove(s)
                continue
            player_frame = player.frames[player.frame_index]
            player_rect = player_frame.get_rect(topleft=(int(player.x), int(player.y)))
            player_mask = pygame.mask.from_surface(player_frame)
            offset = (int(s.rect.x - player_rect.left), int(s.rect.y - player_rect.top))
            if player_mask.overlap(s.mask, offset):
                if len(shield_icons) < max_shields:
                    shield_icons.append(True)
                try:
                    shields.remove(s)
                except ValueError:
                    pass

        # heart pickups collisions
        for h in hearts[:]:
            h.update()
            if h.is_off_screen():
                hearts.remove(h)
                continue
            player_frame = player.frames[player.frame_index]
            player_rect = player_frame.get_rect(topleft=(int(player.x), int(player.y)))
            player_mask = pygame.mask.from_surface(player_frame)
            offset = (int(h.rect.x - player_rect.left), int(h.rect.y - player_rect.top))
            if player_mask.overlap(h.mask, offset):
                if len(heart_icons) < max_hearts:
                    heart_icons.append(True)
                try:
                    hearts.remove(h)
                except ValueError:
                    pass

        # ----------------- RENDER -----------------
        if background:
            screen.blit(background, (0,0))
        else:
            screen.fill((0,0,0))

        # draw barrels, shields, hearts, meteors
        for b in barrels:
            b.draw(screen)
        for s in shields:
            s.draw(screen)
        for h in hearts:
            h.draw(screen)
        for m in meteors:
            m.draw(screen)

        # draw player and get rect/mask for HUD/shield drawing
        player_rect, player_mask = player.draw(screen)

        # HUD
        # score & time
        if star_img:
            screen.blit(pygame.transform.scale(star_img, (45,45)), (10,10))
        screen.blit(font.render(f"SCORE: {current_score}", True, (255,255,255)), (60,15))
        if time_img:
            screen.blit(pygame.transform.scale(time_img, (45,45)), (10,65))
        screen.blit(font.render(f"TIME: {elapsed_time}s", True, (255,255,255)), (60,70))

        # fuel bar
        fuel_ratio = fuel / max_fuel
        pygame.draw.rect(screen, (0,0,0), (10,125,234,44))
        color = (0,255,0) if fuel_ratio >= 0.65 else (255,165,0) if fuel_ratio >= 0.25 else (255,0,0)
        pygame.draw.rect(screen, color, (20,135, int(214 * fuel_ratio), 24))

        # hotbar shields
        hotbar_slot_size = 50
        shield_icon_size = hotbar_slot_size - 10
        shield_icon_scaled = pygame.transform.scale(shield_img, (shield_icon_size, shield_icon_size))
        for i in range(len(shield_icons)):
            x = 10 + i * (shield_icon_size + 5)
            y = height - shield_icon_size - 10
            screen.blit(shield_icon_scaled, (x,y))

        # heart icons
        heart_scaled = pygame.transform.scale(heart_img, (40,40))
        for i in range(len(heart_icons)):
            screen.blit(heart_scaled, (20 + i * 45, 180))

        # shield status bar
        if player.shield_active:
            remaining = max(0, (player.shield_start + player.shield_duration - pygame.time.get_ticks()) // 1000)
            pygame.draw.rect(screen, (173,216,230), (width//2 - 100, 30, int(200 * remaining / (player.shield_duration//1000)), 20))

        # music button (simple icon)
        music_state = get_music_state()
        music_color = (31,10,30) if not music_state.get("muted", False) else (50,50,50)
        pygame.draw.circle(screen, music_color, music_button_rect.center, music_button_size // 2)
        pygame.draw.circle(screen, (255,255,255), music_button_rect.center, music_button_size // 2, 2)
        # two bars
        bar_w = 5; bar_h = music_button_size // 3; spacing = 10
        cx, cy = music_button_rect.center
        pygame.draw.rect(screen, (255,255,255), (cx - spacing//2 - bar_w, cy - bar_h//2, bar_w, bar_h))
        pygame.draw.rect(screen, (255,255,255), (cx + spacing//2, cy - bar_h//2, bar_w, bar_h))
        if music_state.get("muted", False):
            slash = music_button_size // 3
            pygame.draw.line(screen, (255,255,255), (cx - slash, cy - slash), (cx + slash, cy + slash), 3)

        pygame.display.flip()
        clock.tick(60)

    return GameState.MENU
