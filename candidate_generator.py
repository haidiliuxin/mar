import math

from markov_model import END, START


def generate_candidates(model, max_surprisal):
    if max_surprisal < 0:
        return

    initial_history = tuple([START] * model.order)

    for target_length in range(model.min_length, model.max_length + 1):
        fixed_cost = 0.0
        if model.normalization == "distribution":
            length_probability = model.length_probability(target_length)
            if length_probability == 0:
                continue
            fixed_cost = -math.log2(length_probability)
            if fixed_cost > max_surprisal:
                continue

        yield from _generate_one_length(
            model,
            prefix="",
            history=initial_history,
            prefix_cost=fixed_cost,
            target_length=target_length,
            max_surprisal=max_surprisal,
        )


def _generate_one_length(
    model,
    prefix,
    history,
    prefix_cost,
    target_length,
    max_surprisal,
):
    current_length = len(prefix)

    if current_length == target_length:
        final_cost = prefix_cost
        if model.normalization == "end":
            end_probability = model.transition_probability(history, END, current_length)
            if end_probability == 0:
                return
            final_cost -= math.log2(end_probability)
        if final_cost <= max_surprisal:
            yield prefix, final_cost
        return

    for character, character_cost in model.next_character_options(history, current_length):
        child_cost = prefix_cost + character_cost
        if child_cost > max_surprisal:
            break
        child_history = (history + (character,))[-model.order:]
        yield from _generate_one_length(
            model,
            prefix + character,
            child_history,
            child_cost,
            target_length,
            max_surprisal,
        )


def ranked_candidates(model, max_surprisal):
    candidates = list(generate_candidates(model, max_surprisal))
    candidates.sort(key=lambda item: (item[1], item[0]))
    return candidates

