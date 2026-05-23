import pygame
import math


def get_font(size=36):

    return pygame.font.SysFont(None, size)


def draw_ui(screen, lives):

    font = get_font()

    text = font.render(
        f"Lives: {lives}",
        True,
        (255, 255, 255)
    )

    screen.blit(text, (20, 20))


def draw_launch_arrow(
    screen,
    start,
    angle_degrees
):

    angle = math.radians(angle_degrees)

    length = 60

    end = (
        start[0] + math.cos(angle) * length,
        start[1] + math.sin(angle) * length
    )

    pygame.draw.line(
        screen,
        (255, 255, 255),
        start,
        end,
        3
    )

    head_size = 10

    left = (
        end[0]
        - math.cos(angle - 0.5) * head_size,

        end[1]
        - math.sin(angle - 0.5) * head_size
    )

    right = (
        end[0]
        - math.cos(angle + 0.5) * head_size,

        end[1]
        - math.sin(angle + 0.5) * head_size
    )

    pygame.draw.polygon(
        screen,
        (255, 255, 255),
        [end, left, right]
    )


def draw_spiral(
    screen,
    width,
    height,
    center,
    intensity,
    spiral_speed,
    colors,
    thickness
):

    if intensity <= 0:
        return

    max_radius = int(
        math.sqrt(width**2 + height**2)
    )

    center_x, center_y = center

    rotation = (
        pygame.time.get_ticks()
        * 0.001
        * spiral_speed
    )

    points = []

    detail = 3500
    turns = 60

    for i in range(detail):

        t = (
            (i / detail)
            * turns
            * math.pi
            * 2
        ) + rotation

        radius = (
            i / detail
        ) * max_radius

        wave = math.sin(
            t * 0.4
            + pygame.time.get_ticks() * 0.002
        )

        radius += (
            wave
            * 12
            * intensity
        )

        x = center_x + math.cos(t) * radius
        y = center_y + math.sin(t) * radius

        points.append((x, y))

    surf = pygame.Surface(
        (width, height),
        pygame.SRCALPHA
    )

    for i in range(len(points) - 1):

        color = colors[
            i % len(colors)
        ]

        alpha = int(180 * intensity)

        pygame.draw.line(
            surf,
            (
                color[0],
                color[1],
                color[2],
                alpha
            ),
            points[i],
            points[i + 1],
            max(1, int(thickness))
        )

    screen.blit(surf, (0, 0))


def draw_phrases(
    screen,
    phrases,
    elapsed_seconds,
    appear_speed,
    color,
    scroll_speed,
    max_count
):

    if not phrases:
        return

    font = get_font()

    alpha = min(
        255,
        int(
            (
                elapsed_seconds
                / appear_speed
            ) * 255
        )
    )

    # MORE PHRASES OVER TIME
    phrase_count = min(
        max_count,
        1 + int(elapsed_seconds / 10)
    )

    for i in range(phrase_count):

        phrase = phrases[
            (i + int(elapsed_seconds / 5))
            % len(phrases)
        ]

        text = font.render(
            phrase,
            True,
            color
        )

        text.set_alpha(alpha)

        # SCROLL ACROSS SCREEN
        x = (
            width_offset(elapsed_seconds, i, scroll_speed)
        )

        y = (
            120
            + (i * 80)
            + math.sin(elapsed_seconds + i) * 20
        )

        screen.blit(text, (x, y))


def width_offset(
    elapsed_seconds,
    index,
    scroll_speed
):

    width = 1000

    offset = (
        elapsed_seconds
        * scroll_speed
        + index * 250
    )

    return width - (offset % (width + 400))