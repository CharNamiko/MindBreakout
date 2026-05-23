import pygame
import sys
import os

from sound_manager import (
    menu_move_sound,
    menu_select_sound
)


def load_title_image():

    image_path = os.path.join(
        "assets",
        "backgrounds",
        "MindBreakout.png"
    )

    if os.path.exists(image_path):

        image = pygame.image.load(
            image_path
        ).convert_alpha()

        image = pygame.transform.smoothscale(
            image,
            (707, 228)
        )

        return image

    return None


def run_title(
    screen,
    clock,
    title_font,
    menu_font,
    current_level
):

    options = [
        "Start",
        "Load Level",
        "Quit"
    ]

    selected = 0

    title_image = load_title_image()

    while True:

        # EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:

                    selected -= 1

                    menu_move_sound.play()

                    if selected < 0:
                        selected = len(options) - 1

                if event.key == pygame.K_DOWN:

                    selected += 1

                    menu_move_sound.play()

                    if selected >= len(options):
                        selected = 0

                if event.key == pygame.K_RETURN:

                    menu_select_sound.play()

                    return options[selected]

        # DRAW
        screen.fill((0, 0, 0))

        # TITLE IMAGE
        if title_image is not None:

            screen.blit(
                title_image,
                (
                    screen.get_width() // 2
                    - title_image.get_width() // 2,
                    40
                )
            )

        else:

            title = title_font.render(
                "MindBreakout",
                True,
                (255, 255, 255)
            )

            screen.blit(
                title,
                (
                    screen.get_width() // 2
                    - title.get_width() // 2,
                    100
                )
            )

        # CURRENT LEVEL
        level_text = menu_font.render(
            f"Loaded Level: {current_level}",
            True,
            (180, 180, 180)
        )

        screen.blit(
            level_text,
            (
                screen.get_width() // 2
                - level_text.get_width() // 2,
                300
            )
        )

        # OPTIONS
        for i, option in enumerate(options):

            prefix = "  "

            if i == selected:
                prefix = "> "

            text = menu_font.render(
                prefix + option,
                True,
                (255, 255, 255)
            )

            screen.blit(
                text,
                (
                    screen.get_width() // 2
                    - text.get_width() // 2,
                    400 + i * 60
                )
            )

        pygame.display.flip()

        clock.tick(60)