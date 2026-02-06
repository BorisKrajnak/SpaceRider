import pygame
import sys
from core.game_state import GameState
from screens import uvodne_okno, raketka, ufo, skola, game_over, vysvedcenie, nastavenia_hry
from core import vyber_pozadia
from screens.prihlasovanie_registrovanie import login_screen

# ---------------- Inicializácia pygame ----------------
pygame.init()
pygame.key.set_repeat(400, 40)
info = pygame.display.Info()
screen = pygame.display.set_mode(
    (info.current_w, info.current_h),
    pygame.DOUBLEBUF | pygame.HWSURFACE
)
pygame.display.set_caption("Space Rider")
clock = pygame.time.Clock()

# ---------------- Hlavný herný cyklus ----------------
state = GameState.LOGIN
running = True

while running:
    new_state = None

    # --- Spustenie obrazovky podľa stavu ---
    if state == GameState.LOGIN:
        prihlasenie_uspesne = login_screen(screen, clock)
        if prihlasenie_uspesne:
            new_state = GameState.MENU
        else:
            running = False

    elif state == GameState.MENU:
        new_state = uvodne_okno.run(screen)
        if new_state == GameState.LOGIN:
            state = GameState.LOGIN
            continue

    elif state == GameState.SETTINGS:
        new_state = nastavenia_hry.run(screen)
    elif state == GameState.ROCKET_GAME:
        new_state = raketka.run(screen)
    elif state == GameState.UFO_GAME:
        new_state = ufo.run(screen)
    elif state == GameState.SCHOOL_GAME:
        new_state = skola.run(screen)
    elif state == GameState.GAME_OVER:
        new_state = game_over.run(screen)
    elif state == GameState.VYSVEDCENIE:
        new_state = vysvedcenie.run(screen)
    elif state == GameState.BACKGROUND_SELECT:
        new_state = vyber_pozadia.run(screen)

    # --- Aktualizácia stavu ---
    if new_state is None:
        running = False
    else:
        state = new_state

    clock.tick(60)

# --- Ukončenie hry ---
pygame.quit()
sys.exit()
