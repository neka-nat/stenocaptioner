from typing import Callable

import numpy as np


def typing(screenpos: tuple, i: int, v_step: float, transition_duration: float) -> Callable:
    d = lambda t: int(1 - t / transition_duration > 0)
    return lambda t: (screenpos[0] + int(1e20) * d(t - v_step * i), screenpos[1])


def arrive(screenpos: tuple, i: int, v_step: float, transition_duration: float) -> Callable:
    d = lambda t: max(0, 3 - 3 * t / transition_duration)
    return lambda t: (screenpos[0] + 400 * d(t - v_step * i), screenpos[1])


def cascade(screenpos: tuple, i: int, v_step: float, transition_duration: float) -> Callable:
    d = lambda t: 1 if t < 0 else abs(np.sinc(t / transition_duration) / (1 + (t / transition_duration) ** 4))
    return lambda t: (screenpos[0], screenpos[1] + 400 * d(t - v_step * i))
