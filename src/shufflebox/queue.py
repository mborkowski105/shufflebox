class Queue:
    def __init__(self):
        self._items = []
        self._pos   = 0

    def load(self, items):
        self._items = list(items)
        self._pos   = 0

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
