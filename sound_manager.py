import pygame
import numpy as np


SAMPLE_RATE = 44100


def generate_tone(
    frequency=440,
    duration=0.1,
    volume=0.1,
    wave_type="square"
):

    t = np.linspace(
        0,
        duration,
        int(SAMPLE_RATE * duration),
        False
    )

    if wave_type == "square":

        wave = np.sign(
            np.sin(2 * np.pi * frequency * t)
        )

    elif wave_type == "sine":

        wave = np.sin(
            2 * np.pi * frequency * t
        )

    else:

        wave = np.sin(
            2 * np.pi * frequency * t
        )

    audio = wave * (
        32767 * volume
    )

    audio = audio.astype(np.int16)

    stereo_audio = np.column_stack(
        (audio, audio)
    )

    return pygame.sndarray.make_sound(
        stereo_audio
    )


# -----------------------------------
# HYPNOTIC DRONE
# -----------------------------------

def generate_drone():

    duration = 4.0

    t = np.linspace(
        0,
        duration,
        int(SAMPLE_RATE * duration),
        False
    )

    # MULTIPLE SOFT SINE WAVES
    wave1 = np.sin(
        2 * np.pi * 110 * t
    )

    wave2 = np.sin(
        2 * np.pi * 111.5 * t
    )

    wave3 = np.sin(
        2 * np.pi * 55 * t
    )

    combined = (
        wave1 * 0.4
        + wave2 * 0.35
        + wave3 * 0.2
    )

    # VERY SOFT
    combined *= 0.12

    audio = combined * 32767

    audio = audio.astype(np.int16)

    stereo_audio = np.column_stack(
        (audio, audio)
    )

    return pygame.sndarray.make_sound(
        stereo_audio
    )


# -----------------------------------
# GAME SOUNDS
# -----------------------------------

paddle_sound = generate_tone(
    frequency=220,
    duration=0.05,
    volume=0.1,
    wave_type="square"
)

brick_sound = generate_tone(
    frequency=440,
    duration=0.04,
    volume=0.1,
    wave_type="square"
)

launch_sound = generate_tone(
    frequency=660,
    duration=0.08,
    volume=0.1,
    wave_type="square"
)

lose_life_sound = generate_tone(
    frequency=120,
    duration=0.2,
    volume=0.1,
    wave_type="square"
)

menu_move_sound = generate_tone(
    frequency=500,
    duration=0.03,
    volume=0.1,
    wave_type="square"
)

menu_select_sound = generate_tone(
    frequency=800,
    duration=0.06,
    volume=0.1,
    wave_type="square"
)

# -----------------------------------
# AMBIENT DRONE
# -----------------------------------

ambient_drone = generate_drone()