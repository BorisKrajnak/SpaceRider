# screens/raketka.py
import os
import json
import random
import pygame

from core.config import get_path, IMG_DIR
from core.music_manager import set_volume, get_music_state, toggle_mute
from core.game_state import GameState
from core.vyber_pozadia import nacitaj_pozadie
from core.score_manager import save_score




# --- Hrateľné parametre (konštanty) ---
PLAYER_WIDTH = 120
PLAYER_HEIGHT = 120
PLAYER_SPEED = 10
FRAME_RATE_MS = 100  # how fast animation frames change (ms)

# --- Pomocné funkcie pre ukladanie skóre / config ---
def save_game_config_file(game_name):
    cfg_path = get_path("data", "game_config.json")
    config = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
    config["active_game"] = game_name
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


# --- Trieda Meteor ---
class Meteor:
    def __init__(self, meteor_image, width, height, min_size=40, max_size=100, base_speed=3.0):
        self.size = random.randint(min_size, max_size)
        self.image = pygame.transform.scale(meteor_image, (self.size, self.size))
        self.x = width + self.size
        self.y = random.randint(0, height - self.size)
        self.speed = random.uniform(base_speed, base_speed + 5.0)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.x + self.size < 0

# --- Helper: draw music button (same style as settings) ---
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

    # nakresliť gradient na hlavný surface
    surface.blit(gradient, rect.topleft)

    # biele orámovanie
    pygame.draw.rect(surface, (255, 255, 255), rect, 3, border_radius=8)

    # --- ikona ---
    img = img_mute if music_state.get("muted", False) else img_unmute

    if isinstance(img, pygame.Surface):
        # škálovanie ikony tak, aby nepresahovala rect
        img_scaled = pygame.transform.smoothscale(img, (rect.width - 10, rect.height - 10))
        surface.blit(img_scaled, (rect.left + (rect.width - img_scaled.get_width()) // 2,
                                  rect.top + (rect.height - img_scaled.get_height()) // 2))


def draw_gradient_rect(surface, rect, color_top, color_bottom, radius=12):
    """Vykreslí gradient box perfektne zarovnaný s border-radius rámikom."""

    x, y, w, h = rect

    # 1) vytvoríme gradient surface presne vo veľkosti slotu
    gradient = pygame.Surface((w, h), pygame.SRCALPHA)

    # 2) vykreslíme vertikálny prechod
    for i in range(h):
        ratio = i / h
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        pygame.draw.line(gradient, (r, g, b), (0, i), (w, i))

    # 3) vytvoríme masku podľa border-radius
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, w, h), border_radius=radius)

    # 4) aplikujeme maskovanie gradientu
    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # 5) vykreslíme hotový gradient box
    surface.blit(gradient, (x, y))

    # 6) teraz presne nakreslíme rámček
    pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=radius)




# --- Hlavná funkcia (voláme z main.py ako state = raketka.run(screen)) ---
def run(screen, map_image=None):
    width, height = screen.get_size()

    # Ak je map_image None → použije default alebo náhodnú mapu
    # --- FIX pre náhodnú mapu pri reštarte ---
    settings_file = get_path("data", "settings.json")
    try:
        with open(settings_file, "r") as f:
            settings = json.load(f)
            random_map_enabled = settings.get("random_map", False)
    except Exception:
        random_map_enabled = False

    # Ak je zapnutá random mapa → vždy vyber NOVÚ pri štarte hry (aj pri restart)
    if random_map_enabled:
        available_maps = [f"pozadie_vesmir_n{i}.jpg" for i in range(1, 12)]
        new_map = random.choice(available_maps)

        # zabráni vybraniu tej istej mapy po reštarte
        while new_map == map_image:
            new_map = random.choice(available_maps)

        map_image = new_map

    # načítanie pozadia
    background = nacitaj_pozadie(get_path("data", "game_config.json"), width, height, map_image)
    clock = pygame.time.Clock()

    WHITE = (255, 255, 255)
    # načítanie rámcov animácie (raketka)
    gif_folder = get_path("assets", "img", "raketka_frames")
    player_frames = []
    if os.path.exists(gif_folder):
        for filename in sorted(os.listdir(gif_folder)):
            full = os.path.join(gif_folder, filename)
            if os.path.isfile(full):
                try:
                    frame = pygame.image.load(full).convert_alpha()
                    frame = pygame.transform.scale(frame, (PLAYER_WIDTH, PLAYER_HEIGHT))
                    frame = pygame.transform.rotate(frame, -45)
                    player_frames.append(frame)
                except Exception:
                    pass
    if not player_frames:
        # placeholder frame ak chýbajú snímky
        surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (200,200,255), [(0,PLAYER_HEIGHT),(PLAYER_WIDTH//2,0),(PLAYER_WIDTH,PLAYER_HEIGHT)])
        player_frames = [surf]

    # meteor image
    meteor_img_path = get_path("assets", "img", "prekazky", "meteor.png")
    if os.path.exists(meteor_img_path):
        meteor_image = pygame.image.load(meteor_img_path).convert_alpha()
    else:
        # fallback
        meteor_image = pygame.Surface((50,50), pygame.SRCALPHA)
        pygame.draw.circle(meteor_image, (150,150,150), (25,25), 25)

    # HUD images (fuel, star, time, shield)
    def load_asset(*parts, size=None):
        p = get_path("assets", "img", *parts)
        if os.path.exists(p):
            surf = pygame.image.load(p).convert_alpha()
            if size:
                surf = pygame.transform.scale(surf, size)
            return surf
        return None

    star_img = load_asset("doplnky","star.png", size=(45,45)) or pygame.Surface((45,45))
    time_img = load_asset("doplnky","time.png", size=(45,45)) or pygame.Surface((45,45))
    shield_image = load_asset("doplnky","shield.png", size=(60,60)) or pygame.Surface((60,60))
    fuel_image = load_asset("palivo","fuel.png", size=(60,60)) or pygame.Surface((60,60))

    # herné premenné
    player_x, player_y = width // 2, height // 2
    current_frame = 0
    last_frame_time = pygame.time.get_ticks()

    meteory = []
    spawn_delay = 1200
    last_spawn_time = pygame.time.get_ticks()

    start_time = pygame.time.get_ticks()
    meteory_obehol = 0

    base_speed = 3.0
    max_speed = 20.0
    min_spawn_delay = 400
    meteory_velkost_min = 40
    meteory_velkost_max = 100

    fuel = 100.0
    fuel_depletion_rate = 0.04
    fuel_pos = None
    fuel_size = 60
    fuel_spawn_time = 0
    fuel_duration = 5000

    # --- HEART POWERUP (extra životy) ---
    heart_image = load_asset("doplnky", "heart.png", size=(55, 55)) or pygame.Surface((55, 55))
    heart_spawn_pos = None
    heart_spawn_time = pygame.time.get_ticks()
    heart_spawn_interval = random.randint(3500, 5000)
    heart_duration_on_map = 5000
    lives = 0 # default ako vo UFO (3 životy)
    max_lives = 3

    shield_spawn_pos = None
    shield_spawn_time = pygame.time.get_ticks()
    shield_spawn_interval = random.randint(3000, 4000)
    shield_duration_on_map = 5000
    hotbar_shields = []
    max_shields = 5
    shield_active = False
    shield_active_duration = 10000
    shield_end_time = 0

    music_button_size = 60
    music_button_rect = pygame.Rect(width - music_button_size - 20, 20, music_button_size, music_button_size)

    # --- prepare music icons (try load from IMG_DIR, fallback None) ---
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

    # --- pridaj pred hlavným loopom (hneď po načítaní animácie rakety) ---
    BASE_PLAYER_SIZE = max(PLAYER_WIDTH, PLAYER_HEIGHT)
    SHIELD_RADIUS = int(BASE_PLAYER_SIZE * 1.2)  # veľkosť štítu (možno si upravíš podľa vkusu)

    # fonts
    font_path = get_path("assets", "Font", "VOYAGER.ttf")
    try:
        font = pygame.font.Font(font_path, 50)
    except Exception:
        font = pygame.font.SysFont("Arial", 40)

    # pomocné generátory
    def spawn_fuel():
        x = random.randint(fuel_size, width - fuel_size)
        y = random.randint(fuel_size, height - fuel_size)
        return (x, y)

    def spawn_shield():
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)
        return (x, y)

    # hlavný loop
    running = True
    while running:
        # eventy
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # ukonči hru
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if len(hotbar_shields) > 0 and not shield_active:
                        shield_active = True
                        shield_active_start = pygame.time.get_ticks()
                        shield_end_time = shield_active_start + shield_active_duration
                        hotbar_shields.pop(0)
                if event.key == pygame.K_ESCAPE:
                    return GameState.MENU
                if event.key == pygame.K_m:  # --- M pre mute/unmute ---
                    toggle_mute()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if music_button_rect.collidepoint(event.pos):
                    if event.button == 3:
                        set_volume(0.5)
                    else:
                        toggle_mute()

        # update herného času a score
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        score = meteory_obehol + elapsed_time

        # postupné zrýchľovanie
        if elapsed_time > 0 and elapsed_time % 5 == 0:
            base_speed = min(base_speed + 0.02, max_speed)
            spawn_delay = max(spawn_delay - 10, min_spawn_delay)
            meteory_velkost_max = min(meteory_velkost_max + 1, 160)

        # pohyb hráča
        keys = pygame.key.get_pressed()
        rotation_angle = 0
        if keys[pygame.K_w]:
            rotation_angle = +45
            player_y -= PLAYER_SPEED
        elif keys[pygame.K_s]:
            rotation_angle = -45
            player_y += PLAYER_SPEED
        else:
            rotation_angle = 0
        if keys[pygame.K_a]:
            player_x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            player_x += PLAYER_SPEED

        # hranice
        half_w = PLAYER_WIDTH // 2
        half_h = PLAYER_HEIGHT // 2
        player_x = max(half_w, min(player_x, width - half_w))
        player_y = max(half_h - 30, min(player_y, height - half_h + 30))

        # animácia hráča
        if pygame.time.get_ticks() - last_frame_time > FRAME_RATE_MS:
            current_frame = (current_frame + 1) % len(player_frames)
            last_frame_time = pygame.time.get_ticks()

        rotated_frame = pygame.transform.rotate(player_frames[current_frame], rotation_angle)
        frame_rect = rotated_frame.get_rect(center=(player_x, player_y))
        player_mask = pygame.mask.from_surface(rotated_frame)

        # spawn meteorov
        if pygame.time.get_ticks() - last_spawn_time > spawn_delay:
            m = Meteor(meteor_image, width, height,
                       min_size=meteory_velkost_min, max_size=meteory_velkost_max,
                       base_speed=base_speed)
            meteory.append(m)
            last_spawn_time = pygame.time.get_ticks()

        # update fuel
        fuel -= fuel_depletion_rate
        fuel = max(fuel, 0)

        # spawn fuel
        now = pygame.time.get_ticks()
        if fuel_pos is None and now - fuel_spawn_time > 13500:
            fuel_pos = spawn_fuel()
            fuel_spawn_time = now
        elif fuel_pos is not None and now - fuel_spawn_time > fuel_duration:
            fuel_pos = None

        # --- spawn shield on map
        if shield_spawn_pos is None and now - shield_spawn_time > shield_spawn_interval:
            # spawn iba ak ešte nemáme plný počet
            if len(hotbar_shields) < max_shields:
                shield_spawn_pos = spawn_shield()
            shield_spawn_time = now

        if shield_spawn_pos is not None and now - shield_spawn_time > shield_duration_on_map:
            shield_spawn_pos = None
            shield_spawn_time = now

        # --- spawn heart on map ---
        if heart_spawn_pos is None and now - heart_spawn_time > heart_spawn_interval:
            # spawn iba ak ešte nemáme plný počet životov
            if lives < max_lives:
                heart_spawn_pos = (random.randint(50, width - 50), random.randint(50, height - 50))
            heart_spawn_time = now

        elif heart_spawn_pos is not None and now - heart_spawn_time > heart_duration_on_map:
            heart_spawn_pos = None
            heart_spawn_time = now

        # kolízie a logika
        # fuel collision
        if fuel_pos is not None:
            fuel_rect = pygame.Rect(fuel_pos[0], fuel_pos[1], fuel_size, fuel_size)
            offset = (fuel_rect.left - frame_rect.left, fuel_rect.top - frame_rect.top)
            fuel_mask = pygame.mask.from_surface(fuel_image)
            if player_mask.overlap(fuel_mask, offset):
                fuel = min(fuel + 30, 100)
                fuel_pos = None

        # shield pickup
        if shield_spawn_pos is not None:
            shield_rect = pygame.Rect(shield_spawn_pos[0], shield_spawn_pos[1], 50, 50)
            offset_shield = (shield_rect.left - frame_rect.left, shield_rect.top - frame_rect.top)
            if player_mask.overlap(pygame.mask.from_surface(shield_image), offset_shield):
                if len(hotbar_shields) < max_shields:
                    hotbar_shields.append(True)
                shield_spawn_pos = None
                shield_spawn_time = now

        # heart pickup
        if heart_spawn_pos is not None:
            heart_rect = pygame.Rect(heart_spawn_pos[0], heart_spawn_pos[1], 55, 55)
            offset_heart = (heart_rect.left - frame_rect.left, heart_rect.top - frame_rect.top)
            if player_mask.overlap(pygame.mask.from_surface(heart_image), offset_heart):
                if lives < max_lives:
                    lives += 1
                heart_spawn_pos = None
                heart_spawn_time = now

        # update meteory list and collisions
        for meteor in meteory[:]:
            meteor.update()
            if meteor.is_off_screen():
                meteory.remove(meteor)
                meteory_obehol += 1
                continue

            # collision with player (if shield not active)
            if not shield_active:
                offset = (meteor.rect.left - frame_rect.left, meteor.rect.top - frame_rect.top)
                if player_mask.overlap(meteor.mask, offset):

                    if lives > 0:
                        # consume one life and remove meteor (you survive)
                        lives -= 1
                        meteory.remove(meteor)
                        continue
                    else:
                        final_score = meteory_obehol + elapsed_time
                        # uloženie skóre
                        skore_path = get_path("data", "skore.json")
                        try:
                            with open(skore_path, "w", encoding="utf-8") as f:
                                json.dump({"skore": final_score, "cas": elapsed_time}, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                        save_score("raketka", final_score, elapsed_time)
                        return GameState.GAME_OVER

        # fuel 0 -> koniec hry
        if fuel <= 0:
            final_score = meteory_obehol + elapsed_time
            skore_path = get_path("data", "skore.json")
            try:
                with open(skore_path, "w", encoding="utf-8") as f:
                    json.dump({"skore": final_score, "cas": elapsed_time}, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            save_score("raketka", final_score, elapsed_time)
            return GameState.GAME_OVER

        # vykreslenie scény
        if background:
            screen.blit(background, (0,0))
        else:
            screen.fill((0,0,0))

        # hud
        hud_x, hud_y = 10, 10
        line_h = 55
        if star_img: screen.blit(star_img, (hud_x, hud_y))
        score_surface = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_surface, (hud_x + 50, hud_y + 5))
        if time_img: screen.blit(time_img, (hud_x, hud_y + line_h))
        time_surface = font.render(f"TIME: {elapsed_time}s", True, WHITE)
        screen.blit(time_surface, (hud_x + 50, hud_y + line_h + 5))

        # --- Hotbar pozície ---
        hotbar_x = 20
        hotbar_slot_size = 50
        hotbar_spacing = 12

        # --- HEART HOTBAR (nad štítmi) ---
        heart_hotbar_y = height - 140  # o level vyššie

        for i in range(lives):
            slot_rect = pygame.Rect(hotbar_x + i * (hotbar_slot_size + hotbar_spacing),
                                    heart_hotbar_y, hotbar_slot_size, hotbar_slot_size)

            draw_gradient_rect(screen, slot_rect,
                               color_top=(100, 0, 110),
                               color_bottom=(40, 0, 45),
                               radius=12)

            heart_icon_scaled = pygame.transform.scale(heart_image, (hotbar_slot_size - 12, hotbar_slot_size - 12))
            screen.blit(heart_icon_scaled, (slot_rect.x + 6, slot_rect.y + 6))

        # --- SHIELD HOTBAR (pod srdiečkami) ---
        shield_hotbar_y = heart_hotbar_y + hotbar_slot_size + 10

        for i in range(len(hotbar_shields)):
            slot_rect = pygame.Rect(hotbar_x + i * (hotbar_slot_size + hotbar_spacing),
                                    shield_hotbar_y, hotbar_slot_size, hotbar_slot_size)

            draw_gradient_rect(screen, slot_rect,
                               color_top=(100, 0, 110),
                               color_bottom=(40, 0, 45),
                               radius=12)

            shield_icon_scaled = pygame.transform.scale(shield_image, (hotbar_slot_size - 12, hotbar_slot_size - 12))
            screen.blit(shield_icon_scaled, (slot_rect.x + 6, slot_rect.y + 6))

        if shield_active:
            remaining_time = max(0, shield_end_time - pygame.time.get_ticks())
            max_bar_width = 300
            bar_height = 25
            bar_x, bar_y = 20, 160
            bar_width = int((remaining_time / shield_active_duration) * max_bar_width)
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, max_bar_width, bar_height))
            pygame.draw.rect(screen, (0, 100, 255), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, max_bar_width, bar_height), 2)
            if pygame.time.get_ticks() > shield_end_time:
                shield_active = False

        # draw meteors
        for meteor in meteory:
            meteor.draw(screen)

        # draw fuel if exists
        if fuel_pos is not None:
            screen.blit(fuel_image, fuel_pos)

        # draw shield pickup if exists
        if shield_spawn_pos is not None:
            screen.blit(shield_image, shield_spawn_pos)

        if heart_spawn_pos is not None:
            screen.blit(heart_image, heart_spawn_pos)

        # draw player
        screen.blit(rotated_frame, frame_rect.topleft)

        # --- draw shield effect (fixed size, no distortion) ---
        if shield_active:
            # vytvoríme Surface raz podľa pevnej veľkosti
            shield_surface = pygame.Surface((SHIELD_RADIUS * 2, SHIELD_RADIUS * 2), pygame.SRCALPHA)

            # jemný pulz (voliteľné – necháš, ak chceš pekný efekt)
            pulse = 10 * abs((pygame.time.get_ticks() // 150) % 2 - 1)

            # štít
            pygame.draw.circle(
                shield_surface,
                (0, 170, 255, 80 + pulse),
                (SHIELD_RADIUS, SHIELD_RADIUS),
                SHIELD_RADIUS
            )

            # umiestnenie presne na stred rakety
            screen.blit(shield_surface, (player_x - SHIELD_RADIUS, player_y - SHIELD_RADIUS))

        # --- Draw music button using same style as settings ---
        music_state = get_music_state()
        draw_music_button(screen, music_button_rect, music_state, mute_img if mute_img else mute_icon_path, unmute_img if unmute_img else unmute_icon_path)

        # fuel bar
        fuel_bar_pos = (20, 120)
        fuel_bar_size = (300, 25)
        pygame.draw.rect(screen, (50,50,50), (*fuel_bar_pos, *fuel_bar_size))
        filled_width = int(fuel_bar_size[0] * (fuel / 100))
        if fuel > 60:
            fuel_color = (0,255,0)
        elif fuel > 30:
            fuel_color = (255,165,0)
        else:
            fuel_color = (255,0,0)
        pygame.draw.rect(screen, fuel_color, (fuel_bar_pos[0], fuel_bar_pos[1], filled_width, fuel_bar_size[1]))
        pygame.draw.rect(screen, (255,255,255), (*fuel_bar_pos, *fuel_bar_size), 2)

        pygame.display.flip()
        clock.tick(60)

    # fallback
    return GameState.MENU

# --- optional standalone runner (for testing) ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Raketka - test")
    res = run(screen)
    print("Returned state:", res)
    pygame.quit()
