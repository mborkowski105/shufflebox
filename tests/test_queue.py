from shufflebox.queue import Queue

ITEMS = [{"title": "A"}, {"title": "B"}, {"title": "C"}]


class TestQueue:
    def test_next_returns_items_in_order(self):
        q = Queue()
        q.load(ITEMS)
        assert q.next() == ITEMS[0]
        assert q.next() == ITEMS[1]
        assert q.next() == ITEMS[2]

    def test_load_replaces_existing_contents(self):
        q = Queue()
        q.load(ITEMS)
        q.load([{"title": "X"}])
        assert q.next() == {"title": "X"}

    def test_previous_returns_prior_track(self):
        q = Queue()
        q.load(ITEMS)
        q.next()
        q.next()
        assert q.previous() == ITEMS[0]

    def test_previous_at_start_returns_none(self):
        q = Queue()
        q.load(ITEMS)
        q.next()
        assert q.previous() is None
