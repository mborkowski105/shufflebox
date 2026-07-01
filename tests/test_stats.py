from shufflebox.stats import should_count_play


def test_finished_always_counts():
    assert should_count_play(elapsed=0, duration=180, finished=True) is True


def test_above_threshold_counts():
    assert should_count_play(elapsed=60, duration=180, finished=False) is True  # 33% of 180s


def test_below_threshold_does_not_count():
    assert should_count_play(elapsed=30, duration=180, finished=False) is False  # 17% of 180s


def test_at_exact_threshold_counts():
    assert should_count_play(elapsed=54, duration=180, finished=False) is True  # exactly 30%


def test_unknown_duration_uses_floor():
    assert should_count_play(elapsed=30, duration=None, finished=False) is True


def test_unknown_duration_too_short_does_not_count():
    assert should_count_play(elapsed=10, duration=None, finished=False) is False
