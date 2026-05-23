import pygame
import sys
from pathlib import Path

# -----------------------------------
# AUDIO INIT
# -----------------------------------
pygame.mixer.pre_init(
    44100,
    -16,
    2,
    512
)

pygame.init()

from title_screen import run_title
from game import run_game
from level_select import run_level_select

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "MindBreakout"
)

clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont(
    None,
    80
)

MENU_FONT = pygame.font.SysFont(
    None,
    42
)

# -----------------------------------
# CURRENT LEVEL
# -----------------------------------
current_level = (
    "levels/default_level.json"
)

# -----------------------------------
# MAIN LOOP
# -----------------------------------
while True:

    selection = run_title(
        screen,
        clock,
        TITLE_FONT,
        MENU_FONT,
        Path(current_level).name
    )

    # -------------------------------
    # START GAME
    # -------------------------------
    if selection == "Start":

        run_game(
            screen,
            clock,
            current_level
        )

    # -------------------------------
    # LOAD LEVEL
    # -------------------------------
    elif selection == "Load Level":

        chosen_level = run_level_select(
            screen,
            clock,
            TITLE_FONT,
            MENU_FONT
        )

        if chosen_level is not None:
            current_level = chosen_level

    # -------------------------------
    # QUIT
    # -------------------------------
    elif selection == "Quit":

        pygame.quit()
        sys.exit()