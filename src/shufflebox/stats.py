PLAY_THRESHOLD = 0.30
_UNKNOWN_DURATION_FLOOR = 30  # seconds


def should_count_play(elapsed, duration, finished):
    if finished:
        return True
    if not duration:
        return elapsed >= _UNKNOWN_DURATION_FLOOR
    return elapsed >= duration * PLAY_THRESHOLD
