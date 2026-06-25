import tkinter as tk
from tkinter import ttk


def _fmt(seconds):
    if seconds is None or seconds < 0:
        return "--:--"
    return f"{seconds // 60}:{seconds % 60:02d}"


class NowPlayingFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._track_var = tk.StringVar(value="Choose a folder to start.")
        self._time_var  = tk.StringVar(value="")
        tk.Label(self, textvariable=self._track_var, wraplength=580,
                 justify="center", font=("System", 11)).pack()
        tk.Label(self, textvariable=self._time_var, font=("System", 10)).pack()

    def refresh(self, track_text, time_text):
        self._track_var.set(track_text)
        self._time_var.set(time_text)


class ControlsFrame(tk.Frame):
    def __init__(self, parent, on_choose_folder, on_back, on_next, on_reshuffle, on_pause_resume):
        super().__init__(parent)

        top = tk.Frame(self)
        top.pack(fill=tk.X, pady=(0, 4))
        tk.Button(top, text="Choose Folder", command=on_choose_folder).pack(side=tk.LEFT, padx=4)
        self.seed_var = tk.StringVar(value="")
        vcmd = (self.register(lambda s: s == "" or (s.isdigit() and len(s) <= 3)), "%P")
        tk.Label(top, text="Seed:").pack(side=tk.RIGHT, padx=(4, 2))
        tk.Entry(top, textvariable=self.seed_var, width=5,
                 validate="key", validatecommand=vcmd).pack(side=tk.RIGHT)

        playback = tk.Frame(self)
        playback.pack()
        self._back_btn = tk.Button(playback, text="Back", command=on_back, state=tk.DISABLED)
        self._back_btn.pack(side=tk.LEFT, padx=4)
        self._next_btn = tk.Button(playback, text="Next", command=on_next, state=tk.DISABLED)
        self._next_btn.pack(side=tk.LEFT, padx=4)
        self._pause_btn = tk.Button(playback, text="Pause", command=on_pause_resume, state=tk.DISABLED)
        self._pause_btn.pack(side=tk.LEFT, padx=4)
        self._reshuffle_btn = tk.Button(playback, text="Reshuffle", command=on_reshuffle, state=tk.DISABLED)
        self._reshuffle_btn.pack(side=tk.LEFT, padx=4)

    def enable_playback(self):
        self._back_btn.config(state=tk.NORMAL)
        self._next_btn.config(state=tk.NORMAL)
        self._pause_btn.config(state=tk.NORMAL)
        self._reshuffle_btn.config(state=tk.NORMAL)

    def set_paused(self, paused):
        self._pause_btn.config(text="Resume" if paused else "Pause")


class LibraryFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        cols = ("title", "artist", "duration")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        self._tree.heading("title",    text="Title")
        self._tree.heading("artist",   text="Artist")
        self._tree.heading("duration", text="Duration")
        self._tree.column("title",    stretch=True,  minwidth=120, width=280)
        self._tree.column("artist",   stretch=True,  minwidth=80,  width=180)
        self._tree.column("duration", stretch=False, minwidth=60,  width=70,  anchor="e")
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def populate(self, tracks):
        self._tree.delete(*self._tree.get_children())
        for t in tracks:
            self._tree.insert("", tk.END, values=(t["title"], t["artist"], _fmt(t["duration"])))
