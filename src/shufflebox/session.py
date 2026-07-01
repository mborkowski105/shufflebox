from .shuffler import shuffled_order, resolve_seed
from .stats import should_count_play


class Session:
    """A listening session over a library, queue, and player — the journey
    through many tracks, driving the player. Free of any UI."""

    def __init__(self, library, queue, player):
        self._library = library
        self._queue   = queue
        self._player  = player
        self._tracks  = []
        self._active_seed = None

    @property
    def tracks(self):
        return self._tracks

    @property
    def current(self):
        return self._player.current

    @property
    def paused(self):
        return self._player.paused

    @property
    def elapsed(self):
        return self._player.elapsed

    @property
    def seed(self):
        return self._active_seed

    def load(self, directory, seed_text, play):
        self._library.load(directory)
        self._tracks = self._library.query()
        if not self._tracks:
            return False
        if play:
            self.reshuffle(seed_text)
        else:
            self._load_queue(resolve_seed(seed_text, current=self._active_seed))
        return True

    def reshuffle(self, seed_text):
        self._load_queue(resolve_seed(seed_text, current=self._active_seed))
        return self.next()

    def back(self):
        track = None if self._player.elapsed >= 3 else self._queue.previous()
        if track:
            self._player.play(dict(track))
        else:
            self._player.restart()

    def next(self):
        counted = self._record_play()
        track = self._queue.next()
        if track is None and self._tracks:
            self._load_queue(self._active_seed)  # exhausted: loop the same shuffle
            track = self._queue.next()
        if track:
            self._player.play(dict(track))
        return counted

    def enqueue_front(self, filepath):
        track = self._find(filepath)
        if track is None:
            return False
        self._queue.enqueue_front(track)
        if not self._player.current:   # nothing playing yet → start the queued track
            self.next()
        return True

    def play_now(self, filepath):
        track = self._find(filepath)
        if track is None:
            return False
        counted = self._record_play()  # credit the interrupted track
        self._player.play(dict(track))  # play immediately; queue is left intact to resume after
        return counted

    def _find(self, filepath):
        return next((t for t in self._tracks if t["filepath"] == filepath), None)

    def seek(self, seconds):
        self._player.seek(seconds)

    def pause_resume(self):
        if self._player.paused:
            self._player.resume()
        else:
            self._player.pause()

    def tick(self):
        # auto-advance only a track that ended; returns whether a play was counted
        if self._player.current and not self._player.paused and not self._player.playing:
            return self.next()
        return False

    def _load_queue(self, seed):
        self._active_seed = seed
        self._queue.load(shuffled_order(self._tracks, seed))

    def _record_play(self):
        track = self._player.current
        if not track:
            return False
        finished = not self._player.playing and not self._player.paused
        if should_count_play(self._player.elapsed, track.get("duration"), finished):
            self._library.increment_play_count(track["filepath"])
            self._tracks = self._library.query()
            return True
        return False
