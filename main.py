import pygame
import sys
from core.game_state import GameState
from screens import (
    uvodne_okno,
    raketka,
    ufo,
    skola,
    game_over,
    vysvedcenie,
    nastavenia_hry,
    leaderboard
)
from core import vyber_pozadia
from screens.prihlasovanie_registrovanie import login_screen
from core.game_result import GameResult

game_result = None

pygame.init()
pygame.key.set_repeat(400, 40)

info = pygame.display.Info()
screen = pygame.display.set_mode(
    (info.current_w, info.current_h),
    pygame.DOUBLEBUF | pygame.HWSURFACE
)

pygame.display.set_caption("Space Rider")
clock = pygame.time.Clock()

state = GameState.LOGIN
running = True



while running:
    new_state = None

    # --- LOGIN ---
    if state == GameState.LOGIN:
        prihlasenie_uspesne = login_screen(screen, clock)
        if prihlasenie_uspesne:
            new_state = GameState.MENU
        else:
            running = False

    # --- MENU ---
    elif state == GameState.MENU:
        new_state = uvodne_okno.run(screen)
        if new_state == GameState.LOGIN:
            state = GameState.LOGIN
            continue

    # --- SETTINGS ---
    elif state == GameState.SETTINGS:
        new_state = nastavenia_hry.run(screen)

    # --- RAKETKA ---
    elif state == GameState.ROCKET_GAME:
        game_result = raketka.run(screen)

        if isinstance(game_result, GameResult):
            new_state = game_result.next_state
        else:
            new_state = game_result
            game_result = None


    # --- UFO (FIX TU JE DÔLEŽITÝ) ---
    elif state == GameState.UFO_GAME:
        game_result = ufo.run(screen)

        if isinstance(game_result, GameResult):
            new_state = game_result.next_state
        elif isinstance(game_result, GameState):
            new_state = game_result
        else:
            new_state = GameState.MENU


    # --- SCHOOL ---
    elif state == GameState.SCHOOL_GAME:
        new_state = skola.run(screen)

    # --- GAME OVER ---
    elif state == GameState.GAME_OVER:
        if game_result is None:
            state = GameState.MENU
            continue

        new_state = game_over.run(screen, game_result)
        game_result = None


    # --- VYSVEDČENIE ---
    elif state == GameState.VYSVEDCENIE:
        new_state = vysvedcenie.run(screen)

    # --- LEADERBOARD ---
    elif state == GameState.LEADERBOARD:
        new_state = leaderboard.run(screen)

    # --- BACKGROUND SELECT ---
    elif state == GameState.BACKGROUND_SELECT:
        new_state = vyber_pozadia.run(screen)

    # --- UPDATE STATE ---
    if new_state is None:
        state = GameState.MENU
        continue
    else:
        state = new_state

    clock.tick(60)

pygame.quit()
sys.exit()