STAGE_MULTIPLIERS = {
    "group": 1.0,
    "round_of_32": 1.0,
    "round_of_16": 1.5,
    "quarter": 2.0,
    "semi": 2.5,
    "third_place": 1.5,
    "final": 3.0,
}

BONUS_POINTS = {
    "champion": 50,
    "runner_up": 30,
    "top_scorer": 20,
    "surprise_quarter": 15,
}


def calculate_points(pred_home, pred_away, real_home, real_away, stage):
    pred_diff = pred_home - pred_away
    real_diff = real_home - real_away

    pred_result = 1 if pred_diff > 0 else (-1 if pred_diff < 0 else 0)
    real_result = 1 if real_diff > 0 else (-1 if real_diff < 0 else 0)

    if pred_home == real_home and pred_away == real_away:
        base = 25
    elif pred_result == real_result and (pred_home == real_home or pred_away == real_away):
        base = 18
    elif pred_result == real_result and pred_diff == real_diff:
        base = 15
    elif pred_result == real_result:
        base = 10
    else:
        base = 0

    multiplier = STAGE_MULTIPLIERS.get(stage, 1.0)
    return int(base * multiplier)
