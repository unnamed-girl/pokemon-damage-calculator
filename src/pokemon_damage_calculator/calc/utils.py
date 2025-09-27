import math


def floored_multiply(damage_range: list[int], multiplier: float) -> list[int]:
    return [math.floor(d * multiplier) for d in damage_range]


EPSILON = 0.0001


def pokemon_round(n: float) -> int:
    return round(n - EPSILON)


def pokerounded_multiply(damage_range: list[int], multiplier: float) -> list[int]:
    return [pokemon_round(d * multiplier) for d in damage_range]
