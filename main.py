import pygame
import sys
from core.game_state import GameState
from screens import uvodne_okno, raketka, ufo, skola, game_over, vysvedcenie, nastavenia_hry, vyber_pozadia

pygame.init()
info = pygame.display.Info()
screen = pygame.display.set_mode(
    (info.current_w, info.current_h),
    pygame.DOUBLEBUF | pygame.HWSURFACE
)
pygame.display.set_caption("Space Rider")
clock = pygame.time.Clock()

# --- Počiatočný stav hry ---
state = GameState.MENU
running = True

# --- Hlavný cyklus ---
while running:
    new_state = None

    # --- Spustenie obrazovky podľa stavu ---
    if state == GameState.MENU:
        new_state = uvodne_okno.run(screen)

    elif state == GameState.SETTINGS:
        # Nastavenia hry určujú, ktorú hru spustiť
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

    # --- Update stavu ---
    if new_state is None:
        running = False
    else:
        state = new_state

    clock.tick(60)

pygame.quit()
sys.exit()
