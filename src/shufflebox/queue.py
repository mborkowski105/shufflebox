class Queue:
    def __init__(self):
        self._items = []
        self._pos   = 0
        self._insert_at = 0   # where the next front-insert lands

    def load(self, items):
        self._items = list(items)
        self._pos   = 0
        self._insert_at = 0

    def enqueue_front(self, item):
        # insert just after the current position; consecutive adds keep their order
        idx = max(self._pos, self._insert_at)
        self._items.insert(idx, item)
        self._insert_at = idx + 1

    def next(self):
        if self._pos >= len(self._items):
            return None
        track = self._items[self._pos]
        self._pos += 1
        return track

    def previous(self):
        if self._pos < 2:
            return None
        self._pos -= 2
        track = self._items[self._pos]
        self._pos += 1
        return track
