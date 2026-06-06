import pygame
import math
import sys
import os
import random

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
    ambient_drone,
    voice_relax,
    voice_focus,
    voice_breathe
)

WIDTH = 1000
HEIGHT = 700


def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def load_scaled_sprite(path, max_size=None, exact_size=None):

    if not os.path.exists(path):
        return None

    image = pygame.image.load(path).convert_alpha()

    width = image.get_width()
    height = image.get_height()

    # EXACT SIZE
    if exact_size is not None:

        image = pygame.transform.scale(
            image,
            exact_size
        )

        return image

    # MAX SIZE
    if max_size is not None:

        scale = min(
            max_size[0] / width,
            max_size[1] / height,
            1
        )

        if scale != 1:

            image = pygame.transform.scale(
                image,
                (
                    int(width * scale),
                    int(height * scale)
                )
            )

    return image


def draw_center_text(
    screen,
    text,
    size=72,
    alpha=255
):

    font = pygame.font.SysFont(
        None,
        size,
        bold=True
    )

    lines = text.split("\n")

    total_height = len(lines) * size

    for i, line in enumerate(lines):

        surf = font.render(
            line,
            True,
            (255, 255, 255)
        )

        surf.set_alpha(alpha)

        rect = surf.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2
                - total_height // 2
                + i * size
            )
        )

        screen.blit(surf, rect)


class Block:

    def __init__(
        self,
        x,
        y,
        surface=None,
        color=(255, 0, 0),
        size=(80, 25)
    ):

        self.surface = surface

        if self.surface:

            self.rect = self.surface.get_rect(
                topleft=(x, y)
            )

            self.mask = pygame.mask.from_surface(
                self.surface
            )

        else:

            self.rect = pygame.Rect(
                x,
                y,
                size[0],
                size[1]
            )

            self.mask = None

            self.color = color

    def draw(self, screen):

        if self.surface:

            screen.blit(
                self.surface,
                self.rect
            )

        else:

            pygame.draw.rect(
                screen,
                self.color,
                self.rect
            )

    def collides_with_ball(
        self,
        ball_surface,
        ball_rect
    ):

        if self.surface:

            ball_mask = pygame.mask.from_surface(
                ball_surface
            )

            offset = (
                ball_rect.x - self.rect.x,
                ball_rect.y - self.rect.y
            )

            return self.mask.overlap(
                ball_mask,
                offset
            )

        return self.rect.colliderect(ball_rect)


def run_game(screen, clock, level_path):

    # -----------------------------------
    # LOAD LEVEL
    # -----------------------------------
    level = load_level(level_path)

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

    mode = level["Mode"]

    # -----------------------------------
    # BACKGROUND
    # -----------------------------------
    background_surface = None

    if level["Background_Sprite"]:

        path = os.path.join(
            "assets",
            "backgrounds",
            level["Background_Sprite"]
        )

        background_surface = load_scaled_sprite(
            path,
            exact_size=(WIDTH, HEIGHT)
        )

    # -----------------------------------
    # PADDLE
    # -----------------------------------
    paddle_surface = None

    if level["Paddle_Sprite"]:

        path = os.path.join(
            "assets",
            "paddles",
            level["Paddle_Sprite"]
        )

        paddle_surface = load_scaled_sprite(
            path,
            exact_size=(100, 50)
        )

    # -----------------------------------
    # BLOCK SPRITES
    # -----------------------------------
    block_surfaces = []

    for sprite_name in level["Block_Sprites"]:

        path = os.path.join(
            "assets",
            "blocks",
            sprite_name
        )

        sprite = load_scaled_sprite(
            path,
            max_size=(100, 100)
        )

        if sprite:
            block_surfaces.append(sprite)

    # -----------------------------------
    # MODE B
    # -----------------------------------
    overground_surface = None
    overground_mask = None

    if (
        mode == "B"
        and level["Overground_Sprite"]
    ):

        path = os.path.join(
            "assets",
            "overgrounds",
            level["Overground_Sprite"]
        )

        overground_surface = load_scaled_sprite(
            path,
            exact_size=(WIDTH, HEIGHT)
        )

        overground_mask = pygame.mask.from_surface(
            overground_surface
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
        WIDTH // 2 - 50,
        HEIGHT - 60,
        100,
        50
    )

    paddle_speed = 8

    # -----------------------------------
    # BALL
    # -----------------------------------
    ball_surface = pygame.Surface(
        (20, 20),
        pygame.SRCALPHA
    )

    pygame.draw.ellipse(
        ball_surface,
        (255, 255, 255),
        (0, 0, 20, 20)
    )

    ball = ball_surface.get_rect()

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

    if mode == "A":

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

                sprite = None

                if block_surfaces:

                    sprite = random.choice(
                        block_surfaces
                    )

                if sprite:

                    block = Block(
                        x,
                        y,
                        surface=sprite
                    )

                else:

                    color = block_colors[
                        (
                            row * cols + col
                        ) % len(block_colors)
                    ]

                    block = Block(
                        x,
                        y,
                        color=color
                    )

                bricks.append(block)

    total_bricks = max(
        1,
        len(bricks)
    )

    # -----------------------------------
    # TIMER
    # -----------------------------------
    level_start_time = pygame.time.get_ticks()

    game_over = False

    # -----------------------------------
    # MAIN GAME LOOP
    # -----------------------------------
    while not game_over:

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

        # -----------------------------------
        # BALL MOVEMENT
        # -----------------------------------
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

            # -----------------------------------
            # BALL LOST
            # -----------------------------------
            if ball.top > HEIGHT:

                lives -= 1

                lose_life_sound.play()

                hypnosis_messages = [

                    (
                        "RELAX",
                        voice_relax
                    ),

                    (
                        "FOCUS",
                        voice_focus
                    ),

                    (
                        "BREATHE SLOWLY",
                        voice_breathe
                    )
                ]

                message, voice = random.choice(
                    hypnosis_messages
                )

                voice.play()

                start = pygame.time.get_ticks()

                while (
                    pygame.time.get_ticks()
                    - start
                ) < 2000:

                    for e in pygame.event.get():

                        if e.type == pygame.QUIT:

                            pygame.quit()
                            sys.exit()

                    screen.fill((0, 0, 0))

                    draw_spiral(
                        screen,
                        WIDTH,
                        HEIGHT,
                        ball.center,
                        1.0,
                        spiral_speed,
                        spiral_colors,
                        level["Spiral_Thickness"]
                    )

                    elapsed = (
                        pygame.time.get_ticks()
                        - start
                    ) / 2000

                    alpha = int(
                        math.sin(
                            elapsed * math.pi
                        ) * 255
                    )

                    draw_center_text(
                        screen,
                        message,
                        80,
                        alpha
                    )

                    pygame.display.flip()

                    clock.tick(60)

                if lives <= 0:

                    game_over = True
                    break

                reset_ball()

            # -----------------------------------
            # PADDLE COLLISION
            # -----------------------------------
            if ball.colliderect(paddle):

                ball.bottom = paddle.top

                ball_speed[1] *= -1

                paddle_sound.play()

            # -----------------------------------
            # MODE A COLLISION
            # -----------------------------------
            if mode == "A":

                hit_brick = None

                for brick in bricks:

                    if brick.collides_with_ball(
                        ball_surface,
                        ball
                    ):

                        hit_brick = brick
                        break

                if hit_brick:

                    bricks.remove(hit_brick)

                    brick_sound.play()

                    ball_speed[1] *= -1

            # -----------------------------------
            # MODE B COLLISION
            # -----------------------------------
            elif (
                mode == "B"
                and overground_mask
            ):

                ball_mask = pygame.mask.from_surface(
                    ball_surface
                )

                overlap = overground_mask.overlap(
                    ball_mask,
                    (ball.x, ball.y)
                )

                if overlap:

                    brick_sound.play()

                    ball_speed[1] *= -1

                    pygame.draw.circle(
                        overground_surface,
                        (0, 0, 0, 0),
                        ball.center,
                        16
                    )

                    overground_mask = pygame.mask.from_surface(
                        overground_surface
                    )

        # -----------------------------------
        # SPIRAL INTENSITY
        # -----------------------------------
        if mode == "A":

            destroyed_ratio = (
                1 - len(bricks)
                / total_bricks
            )

        else:

            destroyed_ratio = 0.8

        # -----------------------------------
        # DRAW
        # -----------------------------------
        if background_surface:

            screen.blit(
                background_surface,
                (0, 0)
            )

        else:

            screen.fill(
                background_colors[0]
            )

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

        # BLOCKS
        if mode == "A":

            for brick in bricks:

                brick.draw(screen)

        elif overground_surface:

            screen.blit(
                overground_surface,
                (0, 0)
            )

        # PADDLE
        if paddle_surface:

            screen.blit(
                paddle_surface,
                paddle
            )

        else:

            pygame.draw.rect(
                screen,
                (100, 180, 255),
                paddle
            )

        # BALL
        screen.blit(
            ball_surface,
            ball
        )

        # ARROW
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

    # -----------------------------------
    # GAME OVER SEQUENCE
    # -----------------------------------
    spiral_focus = list(ball.center)

    start = pygame.time.get_ticks()

    while True:

        elapsed = (
            pygame.time.get_ticks()
            - start
        ) / 1000

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):

                wake_start = pygame.time.get_ticks()

                while (
                    pygame.time.get_ticks()
                    - wake_start
                ) < 3000:

                    screen.fill((0, 0, 0))

                    fade = max(
                        0,
                        1 - (
                            (
                                pygame.time.get_ticks()
                                - wake_start
                            )
                            / 3000
                        )
                    )

                    draw_spiral(
                        screen,
                        WIDTH,
                        HEIGHT,
                        (
                            WIDTH // 2,
                            HEIGHT // 2
                        ),
                        fade,
                        spiral_speed,
                        spiral_colors,
                        level["Spiral_Thickness"]
                    )

                    draw_center_text(
                        screen,
                        "WAKE UP",
                        90,
                        int(fade * 255)
                    )

                    pygame.display.flip()

                    clock.tick(60)

                ambient_drone.stop()

                return

        screen.fill((0, 0, 0))

        # MOVE SPIRAL CENTER
        spiral_focus[0] += (
            (
                WIDTH // 2
                - spiral_focus[0]
            ) * 0.01
        )

        spiral_focus[1] += (
            (
                HEIGHT // 2
                - spiral_focus[1]
            ) * 0.01
        )

        draw_spiral(
            screen,
            WIDTH,
            HEIGHT,
            spiral_focus,
            1.0,
            spiral_speed,
            spiral_colors,
            level["Spiral_Thickness"]
        )

        # TEXT PHASES
        if elapsed < 5:

            draw_center_text(
                screen,
                "Resistance Failed:\nTime to sleep.",
                64
            )

        elif elapsed < 9:

            count = 3 - int(
                elapsed - 5
            )

            draw_center_text(
                screen,
                str(max(0, count)),
                120
            )

        elif elapsed < 11:

            draw_center_text(
                screen,
                "SLEEP",
                140
            )

        pygame.display.flip()

        clock.tick(60)