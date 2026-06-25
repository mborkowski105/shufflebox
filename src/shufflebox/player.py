import pygame


class Player:
    def __init__(self):
        self._current = None
        self._paused  = False
        pygame.mixer.init()

    def play(self, track):
        self._current = track
        self._paused  = False
        pygame.mixer.music.load(track["filepath"])
        pygame.mixer.music.play()

    def pause(self):
        self._paused = True
        pygame.mixer.music.pause()

    def resume(self):
        self._paused = False
        pygame.mixer.music.unpause()

    def restart(self):
        self._paused = False
        pygame.mixer.music.play()

    @property
    def current(self):
        return self._current

    @property
    def paused(self):
        return self._paused
