def low_kick(weight: float) -> int:
    if weight >= 200.0:
        power = 120
    elif weight >= 100.0:
        power = 100
    elif weight >= 50.0:
        power = 80
    elif weight >= 25.0:
        power = 60
    elif weight >= 10.0:
        power = 40
    else:
        power = 20
    return power

def electro_ball(attacker_speed: int, target_speed: int) -> int:
    relative_speed = target_speed / attacker_speed
    if relative_speed > 0.5:
        power = 40
    elif relative_speed > 0.3335:
        power = 60
    elif relative_speed > 0.2501:
        power = 80
    elif relative_speed > 0.2001:
        power = 100
    else:
        power = 120
    return power


def heavy_slam(user_weightkg: float, target_weightkg: float) -> int:
    relative_weight = target_weightkg / user_weightkg
    if relative_weight > 0.5:
        power = 40
    elif relative_weight > 0.3335:
        power = 60
    elif relative_weight > 0.2501:
        power = 80
    elif relative_weight > 0.2001:
        power = 100
    else:
        power = 120
    return power
