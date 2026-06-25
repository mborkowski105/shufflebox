from shufflebox.shuffler import random_seed, resolve_seed, shuffled_order

POOL = [{"title": str(i)} for i in range(10)]


class TestSeed:
    def test_random_seed_in_range(self):
        for _ in range(50):
            assert 1 <= random_seed() <= 999

    def test_resolve_seed_returns_valid_input(self):
        assert resolve_seed("1")   == 1
        assert resolve_seed("42")  == 42
        assert resolve_seed("999") == 999

    def test_resolve_seed_falls_back_on_invalid(self):
        for bad in ("0", "1000", "abc", "", "-5"):
            assert 1 <= resolve_seed(bad) <= 999

    def test_resolve_seed_differs_when_matches_current(self):
        for _ in range(20):
            assert resolve_seed("42", current=42) != 42


class TestShuffledOrder:
    def test_contains_all_tracks(self):
        result = shuffled_order(POOL, seed=1)
        assert sorted(t["title"] for t in result) == sorted(t["title"] for t in POOL)

    def test_same_seed_same_order(self):
        assert shuffled_order(POOL, seed=7) == shuffled_order(POOL, seed=7)

    def test_different_seeds_can_differ(self):
        orders = {tuple(t["title"] for t in shuffled_order(POOL, seed=n)) for n in range(1, 20)}
        assert len(orders) > 1
