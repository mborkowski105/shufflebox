import time
import pygame


class Player:
    def __init__(self, clock=time.monotonic):
        self._clock    = clock
        self._current  = None
        self._paused   = False
        self._position = 0.0   # track seconds as of the last anchor
        self._anchor   = 0.0   # clock timestamp when the clock last (re)started
        self._running  = False
        pygame.mixer.init()

    def play(self, track):
        self._current = track
        self._start_clock(0.0)
        pygame.mixer.music.load(track["filepath"])
        pygame.mixer.music.play()

    def pause(self):
        if self._running:
            self._position += self._clock() - self._anchor
            self._running = False
        self._paused = True
        pygame.mixer.music.pause()

    def resume(self):
        self._anchor  = self._clock()
        self._running = True
        self._paused  = False
        pygame.mixer.music.unpause()

    def restart(self):
        if not self._current:
            return
        self._start_clock(0.0)
        pygame.mixer.music.play()

    def seek(self, seconds):
        if not self._current:
            return
        self._start_clock(self._clamp(self.elapsed + seconds))
        pygame.mixer.music.play(start=self._position)

    def _start_clock(self, position):
        self._position = position
        self._anchor   = self._clock()
        self._running  = True
        self._paused   = False

    def _clamp(self, position):
        duration = self._current.get("duration")
        position = max(0, position)
        return min(position, duration) if duration else position

    @property
    def elapsed(self):
        if not self._current:
            return 0.0
        running = self._clock() - self._anchor if self._running else 0
        return self._clamp(self._position + running)

    @property
    def current(self):
        return self._current

    @property
    def paused(self):
        return self._paused

    @property
    def playing(self):
        return pygame.mixer.music.get_busy()
