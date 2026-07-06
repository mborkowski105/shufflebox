import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import pygame
from shufflebox.library import Library
from shufflebox.player import Player
from shufflebox.queue import Queue
from shufflebox.session import Session
from shufflebox.ui import NowPlayingFrame, TopBar, SeedControls, TransportControls, LibraryFrame, _fmt


class App(tk.Tk):
    def __init__(self):
        pygame.mixer.init()  # must happen before Tk window on Windows
        super().__init__()
        self.title("Shufflebox")
        self.geometry("640x480")
        self.minsize(480, 320)
        self.option_add("*foreground", "black")  # enforce black text on all classic widgets
        _style = ttk.Style(self)
        _style.configure("Treeview", foreground="black")
        _style.configure("Treeview.Heading", foreground="black")
        db_path = Path.home() / ".shufflebox" / "library.db"
        db_path.parent.mkdir(exist_ok=True)
        self._session = Session(Library(db_path=str(db_path)), Queue(), Player())
        self._build_ui()
        self._load_default_folder()
        self.bind("<FocusIn>", self._on_focus)  # refresh the library when returning to the app
        self._poll()

    def _build_ui(self):
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)  # uniform window margin
        self._topbar = TopBar(container, self._choose_folder)
        self._topbar.pack(fill=tk.X)

        row = tk.Frame(container)
        row.pack(fill=tk.X, pady=(10, 4))

        # now-playing text stacked over the buttons, centered absolutely in the window
        center = tk.Frame(row)
        center.pack()  # no fill/side → centered in the full-width row
        self._now_playing = NowPlayingFrame(center)
        self._now_playing.pack()
        self._transport = TransportControls(center, self._back, self._seek_back, self._seek_forward, self._next, self._pause_resume)
        self._transport.pack(pady=(20, 0))  # gap between now-playing text and the buttons

        # seed overlaid on the right — placed, so it doesn't affect the centering above
        self._seed = SeedControls(row, self._reshuffle)
        self._seed.place(relx=1.0, rely=1.0, anchor="se", x=-14)  # 14px right margin, matching the border

        self._library_view = LibraryFrame(container, self._play_selected, self._enqueue_selected)
        self._library_view.pack(fill=tk.BOTH, expand=True, padx=6, pady=(10, 6))

    def _load_default_folder(self):
        default = Path(__file__).resolve().parents[2] / "tests" / "fixtures"
        if default.exists() and self._session.load(str(default), self._seed.seed(), play=False):
            self._on_loaded()

    def _choose_folder(self):
        folder = filedialog.askdirectory(title="Choose Music Folder")
        if folder and self._session.load(folder, self._seed.seed(), play=True):
            self._on_loaded()

    def _on_loaded(self):
        self._seed.enable()
        self._transport.enable()
        self._seed.set_seed(self._session.seed)
        self._library_view.populate(self._session.tracks)
        self._reflect()

    def _on_focus(self, event):
        # only the toplevel regaining focus (returning to the app), not internal widget focus
        if event.widget is self and self._session.rescan():
            self._library_view.populate(self._session.tracks)

    def _play_selected(self, filepath):
        if self._session.play_now(filepath):
            self._library_view.populate(self._session.tracks)
        self._reflect()

    def _enqueue_selected(self, filepath):
        self._session.enqueue_front(filepath)
        self._reflect()

    def _back(self):
        self._session.back()
        self._reflect()

    def _next(self):
        if self._session.next():
            self._library_view.populate(self._session.tracks)
        self._reflect()

    def _seek_back(self):
        self._session.seek(-15)
        self._reflect()

    def _seek_forward(self):
        self._session.seek(15)
        self._reflect()

    def _pause_resume(self):
        self._session.pause_resume()
        self._reflect()

    def _reshuffle(self):
        if self._session.reshuffle(self._seed.seed()):
            self._library_view.populate(self._session.tracks)
        self._seed.set_seed(self._session.seed)  # reshuffle picks a new seed
        self._reflect()

    def _reflect(self):
        self._transport.set_paused(self._session.paused)
        self._refresh_display()

    def _refresh_display(self):
        t = self._session.current
        if not t:
            return
        year = f" ({t['year']})" if t["year"] else ""
        elapsed = int(self._session.elapsed)
        self._now_playing.refresh(
            f"{t['artist']} — {t['title']}\n{t['album']}{year}",
            f"{_fmt(elapsed)} / {_fmt(t.get('duration'))}",
        )

    def _poll(self):
        if self._session.tick():
            self._library_view.populate(self._session.tracks)
        self._refresh_display()
        self.after(1000, self._poll)


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
