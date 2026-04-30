# screens/ufo.py
import os
import json
import random
import pygame



from core.config import get_path, IMG_DIR
from core.music_manager import set_volume, get_music_state, toggle_mute
from core.game_state import GameState
from core.vyber_pozadia import nacitaj_pozadie
from core.config import save_json, load_json, get_path
from core.game_result import GameResult
from core.score_manager import save_score


# --- Konštanty  ---
UFO_WIDTH = 120
UFO_HEIGHT = 120
UFO_SPEED = 5
GRAVITY = 0.5
JUMP_STRENGTH = -10
FRAME_RATE_MS = 70

def game_over_return(score, elapsed_time):
    is_best = save_score("ufo", score, elapsed_time)

    return GameResult(
        next_state=GameState.GAME_OVER,
        score=score,
        time=elapsed_time,
        is_best=is_best,
        game_name="ufo"
    )

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

def draw_music_button(surface, rect, music_state, img_mute, img_unmute):
    # --- gradient background ---
    color1 = (50, 0, 70)
    color2 = (20, 0, 20)
    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        r = color1[0] + (color2[0] - color1[0]) * (y / rect.height)
        g = color1[1] + (color2[1] - color1[1]) * (y / rect.height)
        b = color1[2] + (color2[2] - color1[2]) * (y / rect.height)
        pygame.draw.line(gradient, (int(r), int(g), int(b), 220), (0, y), (rect.width, y))

    # maskovanie podľa border_radius
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=8)
    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # vykresleniegradientu na hlavný surface
    surface.blit(gradient, rect.topleft)

    # biele orámovanie
    pygame.draw.rect(surface, (255, 255, 255), rect, 3, border_radius=8)

    # --- ikona ---
    img = img_mute if music_state.get("muted", False) else img_unmute

    if isinstance(img, pygame.Surface):
        img_scaled = pygame.transform.smoothscale(img, (rect.width - 10, rect.height - 10))
        surface.blit(img_scaled, (rect.left + (rect.width - img_scaled.get_width()) // 2,
                                      rect.top + (rect.height - img_scaled.get_height()) // 2))

def draw_gradient_rect(surface, rect, color_top, color_bottom, radius=12):
    x, y, w, h = rect
    gradient = pygame.Surface((w, h), pygame.SRCALPHA)

    for i in range(h):
        ratio = i / h
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        pygame.draw.line(gradient, (r, g, b), (0, i), (w, i))

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, w, h), border_radius=radius)
    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    surface.blit(gradient, (x, y))
    pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=radius)

def draw_pause_button(surface, rect, paused):
    color1 = (50, 0, 70)
    color2 = (20, 0, 20)

    # --- gradient ---
    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        pygame.draw.line(gradient, (r, g, b, 220), (0, y), (rect.width, y))

    #zaoblené rohy
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=8)

    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # vykreslenie
    surface.blit(gradient, rect.topleft)

    # orámovanie
    pygame.draw.rect(surface, (255, 255, 255), rect, 3, border_radius=8)

    cx, cy = rect.center

    if paused:
        size = rect.height // 4
        points = [
            (cx - size//2, cy - size),
            (cx - size//2, cy + size),
            (cx + size, cy)
        ]
        pygame.draw.polygon(surface, (255, 255, 255), points)
    else:
        bar_w = 6
        bar_h = rect.height // 2
        spacing = 10

        pygame.draw.rect(surface, (255,255,255), (cx - spacing, cy - bar_h//2, bar_w, bar_h))
        pygame.draw.rect(surface, (255,255,255), (cx + spacing - bar_w, cy - bar_h//2, bar_w, bar_h))


def draw_pause_menu(screen, width, height, font):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0,0,0,180))
    screen.blit(overlay, (0,0))

    btn_w, btn_h = 300, 70
    center_x = width // 2 - btn_w // 2
    start_y = height // 2 - 100

    buttons = {
        "resume": pygame.Rect(center_x, start_y-90, btn_w, btn_h),
        "restart": pygame.Rect(center_x, start_y, btn_w, btn_h),
        "menu": pygame.Rect(center_x, start_y + 90, btn_w, btn_h),
        "quit": pygame.Rect(center_x, start_y + 180, btn_w, btn_h)
    }

    for text, rect in buttons.items():
        draw_gradient_rect(screen, rect, (100,0,120), (40,0,50))
        label = font.render(text.upper(), True, (255,255,255))
        screen.blit(label, (rect.centerx - label.get_width()//2,
                            rect.centery - label.get_height()//2))

    return buttons

# --- Triedy pre objekty ---
class Barrel:
    def __init__(self, screen_w, screen_h, image):
        self.size = 32
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
        self.size = 50
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
        self.size = 50
        self.image = pygame.transform.scale(image, (50, 50))
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
        self.shield_radius = int(base * 1.0)
        self.shield_pause_total = 0
        self.shield_pause_start = 0

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

        self.shield_pause_total = 0
        self.shield_pause_start = 0

    def update_shield(self, paused=False):
        if not self.shield_active:
            return

        if paused:
            return

        real_time = pygame.time.get_ticks() - self.shield_start - self.shield_pause_total

        if real_time > self.shield_duration:
            self.shield_active = False
# ---------------------------------------------------------
#  run(screen) — hlavný modul
# ---------------------------------------------------------
def run(screen):
    music_state = get_music_state()
    save_game_config("ufo")

    width, height = screen.get_size()
    clock = pygame.time.Clock()

    music_size = 60
    music_button_rect = pygame.Rect(width - music_size - 20, 20, music_size, music_size)
    music_state = get_music_state()

    pause_button_size = 60
    pause_button_rect = pygame.Rect(
        width - pause_button_size - 20,
        height - pause_button_size - 20,
        pause_button_size,
        pause_button_size
    )

    # načítanie background
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

    # načítanie animácie - ufo frames
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

    paused = False
    pause_start_time = 0
    paused_time_total = 0
    buttons = None

    running = True
    while running:
        now = pygame.time.get_ticks()
        if not paused:
            elapsed_time = (now - start_time - paused_time_total) // 1000
        current_score = meteory_prelietane + elapsed_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameState.MENU

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        if paused:
                            pause_start_time = pygame.time.get_ticks()
                            if player.shield_active:
                                player.shield_pause_start = pygame.time.get_ticks()
                        else:
                            paused_time_total += pygame.time.get_ticks() - pause_start_time
                            if player.shield_active:
                                player.shield_pause_total += pygame.time.get_ticks() - player.shield_pause_start

                if not paused:
                    if event.key == pygame.K_w:
                        player.flap()

                    if event.key == pygame.K_e and shield_icons and not player.shield_active:
                        shield_icons.pop()
                        player.activate_shield()

                if event.key == pygame.K_m:
                    toggle_mute()
                    music_state = get_music_state()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if music_button_rect.collidepoint(event.pos):
                    toggle_mute()
                    music_state = get_music_state()
                if pause_button_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pause_start_time = pygame.time.get_ticks()
                        if player.shield_active:
                            player.shield_pause_start = pygame.time.get_ticks()
                    else:
                        paused_time_total += pygame.time.get_ticks() - pause_start_time
                        if player.shield_active:
                            player.shield_pause_total += pygame.time.get_ticks() - player.shield_pause_start

                if paused and buttons:
                    if buttons["resume"].collidepoint(event.pos):
                        paused = False
                        paused_time_total += pygame.time.get_ticks() - pause_start_time
                    elif buttons["restart"].collidepoint(event.pos):
                        return GameState.UFO_GAME

                    elif buttons["menu"].collidepoint(event.pos):
                        return GameState.MENU

                    elif buttons["quit"].collidepoint(event.pos):
                        pygame.quit()
                        exit()

        keys = pygame.key.get_pressed()
        if not paused:
            if keys[pygame.K_a]:
                player.x -= player.move_speed
            if keys[pygame.K_d]:
                player.x += player.move_speed


        player.update_anim()

        if not paused:

            # apply physics
            player.apply_physics()
            #player.update_anim()
            player.update_shield(paused)

            player.x = max(0, min(player.x, width - player.width))
            player.y = max(0, min(player.y, height - player.height))
            if player.y >= height - player.height:
                player.speed_y = 0

            # fuel
            if now - last_fuel_update > 100:
                fuel -= fuel_depletion_rate
                last_fuel_update = now
                if fuel <= 0:
                    return GameResult(
                        next_state=GameState.GAME_OVER,
                        score=current_score,
                        time=elapsed_time,
                        is_best=save_score("ufo", current_score, elapsed_time),
                        game_name="ufo"
                    )

            # spawn meteors
            if now - last_spawn > max(300, spawn_delay - (elapsed_time * 10)):
                meteors.append(Meteor(width, height, meteor_img, 1 + (elapsed_time//30)*0.2))
                last_spawn = now

            # spawn barrel
            if now - last_barrel_spawn > 10000:
                barrels.append(Barrel(width, height, barrel_img))
                last_barrel_spawn = now

            # spawn shield
            if now - last_shield_spawn > 20000:
                shields.append(ShieldPickup(width, height, shield_img))
                last_shield_spawn = now

            # spawn heart
            if now - last_heart_spawn > 25000:
                hearts.append(HeartPickup(width, height, heart_img))
                last_heart_spawn = now

            # update meteoritov a kolízií
            for m in meteors[:]:
                m.update()
                if m.is_off_screen():
                    meteors.remove(m)
                    meteory_prelietane += 1
                    continue
                player_frame = player.frames[player.frame_index]
                player_rect = player_frame.get_rect(topleft=(int(player.x), int(player.y)))
                player_mask = pygame.mask.from_surface(player_frame)
                if not player.shield_active:
                    offset = (int(m.rect.x - player_rect.left), int(m.rect.y - player_rect.top))
                    if player_mask.overlap(m.mask, offset):
                        if heart_icons:
                            heart_icons.pop()
                            try:
                                meteors.remove(m)
                            except ValueError:
                                pass
                            continue
                        return GameResult(
                            next_state=GameState.GAME_OVER,
                            score=current_score,
                            time=elapsed_time,
                            is_best=save_score("ufo", current_score, elapsed_time),
                            game_name="ufo"
                        )

            # barrel-kolízia
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

            # shield-kolízia
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

            # heart-kolízia
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

        # --- HOTBAR UFO ---
        hotbar_x = 20
        hotbar_slot_size = 50
        hotbar_spacing = 12

        # hearts
        heart_y = screen.get_height() - 140
        for i in range(len(heart_icons)):
            slot_rect = pygame.Rect(hotbar_x + i * (hotbar_slot_size + hotbar_spacing),
                                    heart_y, hotbar_slot_size, hotbar_slot_size)
            draw_gradient_rect(screen, slot_rect,
                                color_top=(100, 0, 110),
                                color_bottom=(40, 0, 45),
                                radius=12)
            heart_scaled = pygame.transform.scale(heart_img, (hotbar_slot_size - 12, hotbar_slot_size - 12))
            screen.blit(heart_scaled, (slot_rect.x + 6, slot_rect.y + 6))

        # shields
        shield_y = heart_y + hotbar_slot_size + 10
        for i in range(len(shield_icons)):
            slot_rect = pygame.Rect(hotbar_x + i * (hotbar_slot_size + hotbar_spacing),
                                    shield_y, hotbar_slot_size, hotbar_slot_size)
            draw_gradient_rect(screen, slot_rect,
                                color_top=(100, 0, 110),
                                color_bottom=(40, 0, 45),
                                radius=12)
            shield_scaled = pygame.transform.scale(shield_img, (hotbar_slot_size - 12, hotbar_slot_size - 12))
            screen.blit(shield_scaled, (slot_rect.x + 6, slot_rect.y + 6))

        # --- shield status bar ---
        if player.shield_active:
            effective_time = pygame.time.get_ticks() - player.shield_pause_total

            remaining_ratio = max(0, (
                    player.shield_start + player.shield_duration - effective_time
            ) / player.shield_duration)
            bar_width = 200
            bar_height = 25
            x = width // 2 - bar_width // 2
            y = 30
            if not paused:
                # pozadie pruhu
                pygame.draw.rect(screen, (20, 40, 100), (x, y, bar_width, bar_height))

                # fill pruhu
                fill_width = int(bar_width * remaining_ratio)
                pygame.draw.rect(screen, (0, 170, 255), (x, y, fill_width, bar_height))

                # orámovanie
                pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 3)

        music_button_size = 60
        music_button_rect = pygame.Rect(width - music_button_size - 20, 20, music_button_size, music_button_size)

        mute_icon_path = os.path.join(IMG_DIR, "mute.png")
        unmute_icon_path = os.path.join(IMG_DIR, "unmute.png")
        mute_img = None
        unmute_img = None
        try:
            if os.path.exists(mute_icon_path):
                mute_img = pygame.image.load(mute_icon_path).convert_alpha()
                mute_img = pygame.transform.smoothscale(mute_img, (music_button_size - 10, music_button_size - 10))
            if os.path.exists(unmute_icon_path):
                unmute_img = pygame.image.load(unmute_icon_path).convert_alpha()
                unmute_img = pygame.transform.smoothscale(unmute_img, (music_button_size - 10, music_button_size - 10))
        except Exception:
            mute_img = None
            unmute_img = None
        bar_w = 5; bar_h = music_button_size // 3; spacing = 10
        cx, cy = music_button_rect.center
        pygame.draw.rect(screen, (255,255,255), (cx - spacing//2 - bar_w, cy - bar_h//2, bar_w, bar_h))
        pygame.draw.rect(screen, (255,255,255), (cx + spacing//2, cy - bar_h//2, bar_w, bar_h))
        if music_state.get("muted", False):
            slash = music_button_size // 3
            pygame.draw.line(screen, (255,255,255), (cx - slash, cy - slash), (cx + slash, cy + slash), 3)

        if paused:
            buttons = draw_pause_menu(screen, width, height, font)

        music_state = get_music_state()
        draw_music_button(screen, music_button_rect, music_state, mute_img if mute_img else mute_icon_path,
                          unmute_img if unmute_img else unmute_icon_path)

        draw_pause_button(screen, pause_button_rect, paused)

        pygame.display.flip()
        clock.tick(60)

    return GameState.MENU