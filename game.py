import pygame
import math
import sys

from level_loader import load_level

from ui import (
    draw_spiral,
    draw_launch_arrow,
    draw_phrases,
    draw_ui
)

from sound_manager import (
    paddle_sound,
    brick_sound,
    launch_sound,
    lose_life_sound,
    ambient_drone
)

WIDTH = 1000
HEIGHT = 700


def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def run_game(screen, clock, level_path):

    # -----------------------------------
    # LOAD LEVEL
    # -----------------------------------
    level = load_level(level_path)

    # START AMBIENT AUDIO
    ambient_drone.play(loops=-1)

    background_colors = [
        hex_to_rgb(c)
        for c in level["Background_Color"]
    ]

    block_colors = [
        hex_to_rgb(c)
        for c in level["Block_Colors"]
    ]

    spiral_colors = [
        hex_to_rgb(c)
        for c in level["Spiral_Colors"]
    ]

    phrase_color = hex_to_rgb(
        level["Phrase_Color"]
    )

    # -----------------------------------
    # SETTINGS
    # -----------------------------------
    lives = level["Lives"]

    difficulty = max(
        0,
        min(10, level["Difficulty"])
    )

    spiral_speed = level["Spiral_Speed"]

    base_speed = (
        4 + level["Ball_Starting_Speed"] * 8
    )

    speed_growth = difficulty * 0.00005

    # -----------------------------------
    # PADDLE
    # -----------------------------------
    paddle = pygame.Rect(
        WIDTH // 2 - 60,
        HEIGHT - 40,
        120,
        15
    )

    paddle_speed = 8

    # -----------------------------------
    # BALL
    # -----------------------------------
    ball = pygame.Rect(0, 0, 20, 20)

    ball_speed = [0.0, 0.0]

    launch_angle = -60

    ball_attached = True

    def reset_ball():

        nonlocal ball_attached

        ball.centerx = paddle.centerx
        ball.bottom = paddle.top - 5

        ball_attached = True

    def launch_ball():

        nonlocal ball_attached

        angle = math.radians(launch_angle)

        ball_speed[0] = (
            math.cos(angle) * base_speed
        )

        ball_speed[1] = (
            math.sin(angle) * base_speed
        )

        ball_attached = False

        launch_sound.play()

    reset_ball()

    # -----------------------------------
    # BRICKS
    # -----------------------------------
    bricks = []

    rows = 5
    cols = 10

    brick_width = 80
    brick_height = 25

    padding = 10

    total_width = (
        cols * brick_width
        + (cols - 1) * padding
    )

    start_x = (
        WIDTH - total_width
    ) // 2

    for row in range(rows):

        for col in range(cols):

            x = (
                start_x
                + col * (brick_width + padding)
            )

            y = (
                70
                + row * (brick_height + padding)
            )

            bricks.append(
                pygame.Rect(
                    x,
                    y,
                    brick_width,
                    brick_height
                )
            )

    total_bricks = len(bricks)

    # -----------------------------------
    # TIMER
    # -----------------------------------
    level_start_time = pygame.time.get_ticks()

    # -----------------------------------
    # GAME LOOP
    # -----------------------------------
    while True:

        elapsed_seconds = (
            pygame.time.get_ticks()
            - level_start_time
        ) / 1000

        # EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                ambient_drone.stop()

                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    ambient_drone.stop()

                    return

                if (
                    event.key == pygame.K_SPACE
                    and ball_attached
                ):
                    launch_ball()

        # INPUT
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            paddle.x -= paddle_speed

        if keys[pygame.K_RIGHT]:
            paddle.x += paddle_speed

        paddle.x = max(
            0,
            min(WIDTH - paddle.width, paddle.x)
        )

        # BALL
        if ball_attached:

            ball.centerx = paddle.centerx
            ball.bottom = paddle.top - 5

        else:

            ball.x += ball_speed[0]
            ball.y += ball_speed[1]

            # SPEED GROWTH
            ball_speed[0] *= (
                1 + speed_growth
            )

            ball_speed[1] *= (
                1 + speed_growth
            )

            # WALL COLLISION
            if (
                ball.left <= 0
                or ball.right >= WIDTH
            ):
                ball_speed[0] *= -1

            if ball.top <= 0:
                ball_speed[1] *= -1

            # BALL LOST
            if ball.top > HEIGHT:

                lives -= 1

                lose_life_sound.play()

                if lives <= 0:

                    ambient_drone.stop()

                    return

                reset_ball()

            # PADDLE COLLISION
            if ball.colliderect(paddle):

                ball.bottom = paddle.top

                ball_speed[1] *= -1

                paddle_sound.play()

                offset = (
                    (
                        ball.centerx
                        - paddle.centerx
                    )
                    / (paddle.width / 2)
                )

                ball_speed[0] = offset * 8

            # BRICK COLLISION
            hit_brick = None

            for brick in bricks:

                if ball.colliderect(brick):

                    hit_brick = brick
                    break

            if hit_brick:

                bricks.remove(hit_brick)

                brick_sound.play()

                ball_speed[1] *= -1

        # WIN CONDITION
        if len(bricks) == 0:

            ambient_drone.stop()

            return

        # SPIRAL INTENSITY
        destroyed_ratio = (
            1 - len(bricks) / total_bricks
        )

        # DRAW
        screen.fill(background_colors[0])

        # SPIRAL
        draw_spiral(
            screen,
            WIDTH,
            HEIGHT,
            ball.center,
            destroyed_ratio,
            spiral_speed,
            spiral_colors,
            level["Spiral_Thickness"]
        )

        # PHRASES
        draw_phrases(
            screen,
            level["Phrases"],
            elapsed_seconds,
            level["Phrase_Appear_Speed"],
            phrase_color,
            level["Phrase_Scroll_Speed"],
            level["Phrase_Max_Count"]
        )

        # BRICKS
        for i, brick in enumerate(bricks):

            color = block_colors[
                i % len(block_colors)
            ]

            pygame.draw.rect(
                screen,
                color,
                brick
            )

        # PADDLE
        pygame.draw.rect(
            screen,
            (100, 180, 255),
            paddle
        )

        # BALL
        pygame.draw.ellipse(
            screen,
            (255, 255, 255),
            ball
        )

        # LAUNCH ARROW
        if ball_attached:

            draw_launch_arrow(
                screen,
                ball.center,
                launch_angle
            )

        # UI
        draw_ui(screen, lives)

        pygame.display.flip()

        clock.tick(60)