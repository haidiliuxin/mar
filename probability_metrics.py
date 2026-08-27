import math


def score_test_set(model, testing_counts, theta=0.8, thresholds=None):
    if not 0 < theta <= 1:
        raise ValueError("theta 应在 0 和 1 之间")
    if not testing_counts:
        raise ValueError("测试集为空")
    if thresholds is None:
        thresholds = [20, 30, 40, 50, 60, 70, 80]

    total = sum(testing_counts.values())
    ranked = []
    for password, count in testing_counts.items():
        ranked.append((model.surprisal(password), count))
    ranked.sort(key=lambda item: item[0])

    curve = []
    covered = 0
    index = 0
    while index < len(ranked):
        value = ranked[index][0]
        while index < len(ranked) and ranked[index][0] == value:
            covered += ranked[index][1]
            index += 1
        curve.append((value, covered / total))

    zero_count = 0
    zero_types = 0
    for value, count in ranked:
        if not math.isfinite(value):
            zero_count += count
            zero_types += 1

    if zero_count:
        full_anll = None
    else:
        full_anll = sum(value * count for value, count in ranked) / total

    remaining = theta * total
    partial_sum = 0.0
    for value, count in ranked:
        take = min(float(count), remaining)
        partial_sum += value * take
        remaining -= take
        if remaining <= 0:
            break
    anll_theta = None if not math.isfinite(partial_sum) else partial_sum / total

    threshold_result = {}
    for threshold in thresholds:
        threshold_result[str(threshold)] = (
            sum(count for value, count in ranked if value <= threshold) / total
        )

    return {
        "ANLL": full_anll,
        "ANLL_theta": anll_theta,
        "theta": theta,
        "threshold_coverages": threshold_result,
        "zero_probability_occurrences": zero_count,
        "zero_probability_types": zero_types,
        "curve": curve,
    }

