import tkinter as tk
from tkinter import filedialog
import pygame
from shufflebox.library import Library
from shufflebox.player import Player
from shufflebox.queue import Queue
from shufflebox.shuffler import shuffled_order, resolve_seed, random_seed
from shufflebox.ui import NowPlayingFrame, ControlsFrame, LibraryFrame, _fmt


class App(tk.Tk):
    def __init__(self):
        pygame.mixer.init()  # must happen before Tk window on Windows
        super().__init__()
        self.title("Shufflebox")
        self.geometry("640x480")
        self.minsize(480, 320)
        self._library = Library()
        self._queue   = Queue()
        self._player  = Player()
        self._tracks  = []
        self._active_seed = None
        self._build_ui()
        self._poll()

    def _build_ui(self):
        self._now_playing = NowPlayingFrame(self)
        self._now_playing.pack(fill=tk.X, padx=12, pady=(10, 4))
        self._controls = ControlsFrame(self, self._choose_folder, self._back, self._advance, self._reshuffle, self._pause_resume)
        self._controls.pack(fill=tk.X, padx=12, pady=4)
        self._library_view = LibraryFrame(self)
        self._library_view.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 10))

    def _choose_folder(self):
        folder = filedialog.askdirectory(title="Choose Music Folder")
        if not folder:
            return
        self._library.load(folder)
        self._tracks = self._library.query()
        if self._tracks:
            self._controls.enable_playback()
            self._library_view.populate(self._tracks)
            self._reshuffle()

    def _load_queue(self, seed):
        self._active_seed = seed
        self._controls.seed_var.set(str(seed))
        self._queue.load(shuffled_order(self._tracks, seed))

    def _reshuffle(self):
        self._load_queue(resolve_seed(self._controls.seed_var.get(), current=self._active_seed))
        self._advance()

    def _back(self):
        if pygame.mixer.music.get_pos() >= 3000:
            self._player.restart()
        else:
            track = self._queue.previous()
            if track:
                self._player.play(dict(track))
                self._controls.set_paused(False)
                self._refresh_display()
            else:
                self._player.restart()

    def _pause_resume(self):
        if self._player.paused:
            self._player.resume()
        else:
            self._player.pause()
        self._controls.set_paused(self._player.paused)

    def _advance(self):
        track = self._queue.next()
        if track is None and self._tracks:
            self._load_queue(random_seed())
            track = self._queue.next()
        if track:
            self._player.play(dict(track))
            self._controls.set_paused(False)
            self._refresh_display()

    def _refresh_display(self):
        t = self._player.current
        if not t:
            return
        year = f" ({t['year']})" if t["year"] else ""
        elapsed = pygame.mixer.music.get_pos() // 1000
        self._now_playing.refresh(
            f"{t['artist']} — {t['title']}\n{t['album']}{year}",
            f"{_fmt(elapsed)} / {_fmt(t.get('duration'))}",
        )

    def _poll(self):
        if self._tracks and not self._player.paused and not pygame.mixer.music.get_busy():
            self._advance()
        elif self._player.current:
            self._refresh_display()
        self.after(1000, self._poll)


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
