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

    def test_next_returns_none_when_exhausted(self):
        q = Queue()
        q.load(ITEMS)
        for _ in ITEMS:
            q.next()
        assert q.next() is None

    def test_enqueue_front_plays_before_the_rest(self):
        q = Queue()
        q.load(ITEMS)
        q.enqueue_front({"title": "Z"})
        assert q.next() == {"title": "Z"}
        assert q.next() == ITEMS[0]

    def test_retain_drops_removed_track_from_upcoming(self):
        q = Queue()
        q.load([{"filepath": "a"}, {"filepath": "b"}, {"filepath": "c"}, {"filepath": "d"}])
        q.next()                       # play a
        q.retain({"a", "c", "d"})      # b deleted from the library
        assert q.next() == {"filepath": "c"}  # b is skipped, not played

    def test_retain_removes_track_from_the_whole_queue(self):
        q = Queue()
        q.load([{"filepath": "a"}, {"filepath": "b"}, {"filepath": "c"}])
        q.retain({"a", "c"})           # b deleted
        drained = [q.next() for _ in range(3)]
        assert {"filepath": "b"} not in drained

    def test_enqueue_front_preserves_insertion_order(self):
        q = Queue()
        q.load([{"title": "X"}, {"title": "Y"}])
        q.enqueue_front({"title": "A"})
        q.enqueue_front({"title": "B"})
        # queue reads A, B, X, Y — consecutive adds keep their order
        assert [q.next() for _ in range(4)] == [{"title": "A"}, {"title": "B"}, {"title": "X"}, {"title": "Y"}]
