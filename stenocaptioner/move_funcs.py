from typing import Callable


def arrive(screenpos: tuple, i: int, nletters: int) -> Callable:
    d = lambda t: max(0, 3 - 3 * t)
    return lambda t: (screenpos[0] + 400 * d(t - 0.2 * i), screenpos[1])
