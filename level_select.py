import pygame
import sys
from pathlib import Path

LEVEL_FOLDER = Path("levels")


def get_level_list():

    if not LEVEL_FOLDER.exists():
        return []

    levels = []

    for file in LEVEL_FOLDER.glob("*.json"):

        levels.append(file.name)

    levels.sort()

    return levels


def run_level_select(
    screen,
    clock,
    title_font,
    menu_font
):

    levels = get_level_list()

    if len(levels) == 0:
        return None

    selected = 0

    while True:

        # EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:

                    selected -= 1

                    if selected < 0:
                        selected = len(levels) - 1

                if event.key == pygame.K_DOWN:

                    selected += 1

                    if selected >= len(levels):
                        selected = 0

                if event.key == pygame.K_ESCAPE:

                    return None

                if event.key == pygame.K_RETURN:

                    return (
                        "levels/"
                        + levels[selected]
                    )

        # DRAW
        screen.fill((0, 0, 0))

        title = title_font.render(
            "Select Level",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                screen.get_width() // 2
                - title.get_width() // 2,
                80
            )
        )

        for i, level_name in enumerate(levels):

            prefix = "  "

            if i == selected:
                prefix = "> "

            text = menu_font.render(
                prefix + level_name,
                True,
                (255, 255, 255)
            )

            screen.blit(
                text,
                (
                    screen.get_width() // 2
                    - text.get_width() // 2,
                    220 + i * 50
                )
            )

        back_text = menu_font.render(
            "ESC = Back",
            True,
            (180, 180, 180)
        )

        screen.blit(
            back_text,
            (
                20,
                screen.get_height() - 50
            )
        )

        pygame.display.flip()

        clock.tick(60)