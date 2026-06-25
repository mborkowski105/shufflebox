import random


def random_seed():
    return random.randint(1, 999)


def resolve_seed(value, current=None):
    try:
        n = int(value)
        seed = n if 1 <= n <= 999 else random_seed()
    except (ValueError, TypeError):
        seed = random_seed()
    while seed == current:
        seed = random_seed()
    return seed


def shuffled_order(tracks, seed):
    rng = random.Random(seed * (2**32 // 1000))
    order = list(tracks)
    rng.shuffle(order)
    return order
