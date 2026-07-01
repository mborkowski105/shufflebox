import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont


def _fmt(seconds):
    if seconds is None or seconds < 0:
        return "--:--"
    return f"{seconds // 60}:{seconds % 60:02d}"


def _emphasize(button):
    font = tkfont.Font(font=button["font"])
    font.configure(size=font.actual("size") + 1)
    button.configure(font=font)


# The proper pause glyph (U+23F8) won't render in Tk's fonts, so we draw the
# pause/play icons pixel-exact into in-memory images — no font, no asset files.
def _pause_icon():
    img = tk.PhotoImage(width=14, height=14)
    img.put("black", to=(3, 2, 6, 12))    # left bar  (cols 3-5)
    img.put("black", to=(8, 2, 11, 12))   # right bar (cols 8-10), 2px gap
    return img


def _play_icon():
    img = tk.PhotoImage(width=14, height=14)
    for y in range(2, 13):                 # right-pointing triangle, widest at the middle row
        x_right = 3 + round(8 * (1 - abs(y - 7) / 5))
        if x_right > 3:
            img.put("black", to=(3, y, x_right + 1, y + 1))
    return img


class NowPlayingFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._track_var = tk.StringVar(value="Choose a folder, then shuffle to begin.")
        self._time_var  = tk.StringVar(value="")
        tk.Label(self, textvariable=self._track_var, wraplength=360,
                 justify="center", font=("System", 11)).pack()
        tk.Label(self, textvariable=self._time_var, font=("System", 10)).pack()

    def refresh(self, track_text, time_text):
        self._track_var.set(track_text)
        self._time_var.set(time_text)


class TopBar(tk.Frame):
    """Top-left folder button."""

    def __init__(self, parent, on_choose_folder):
        super().__init__(parent)
        folder_btn = tk.Button(self, text="📁", command=on_choose_folder)
        _emphasize(folder_btn)
        folder_btn.pack(side=tk.LEFT, padx=4)


class SeedControls(tk.Frame):
    """Seed field stacked over the shuffle button, right-aligned."""

    def __init__(self, parent, on_reshuffle):
        super().__init__(parent)
        seed_row = tk.Frame(self)
        seed_row.pack(anchor="e")
        self._seed_var = tk.StringVar(value="")
        vcmd = (self.register(lambda s: s == "" or (s.isdigit() and len(s) <= 3)), "%P")
        tk.Entry(seed_row, textvariable=self._seed_var, width=5,
                 validate="key", validatecommand=vcmd).pack(side=tk.RIGHT)  # field flush right
        tk.Label(seed_row, text="Seed:").pack(side=tk.RIGHT, padx=(0, 2))   # label to its left

        self._reshuffle_btn = tk.Button(self, text="🔀", command=on_reshuffle, state=tk.DISABLED)
        _emphasize(self._reshuffle_btn)
        self._reshuffle_btn.pack(anchor="e", pady=(6, 0))  # gap between seed field and shuffle button

    def enable(self):
        self._reshuffle_btn.config(state=tk.NORMAL)

    def seed(self):
        return self._seed_var.get()

    def set_seed(self, value):
        self._seed_var.set(str(value))


class TransportControls(tk.Frame):
    """Playback buttons: Back, -15s, +15s, Next, Pause."""

    def __init__(self, parent, on_back, on_seek_back, on_seek_forward, on_next, on_pause_resume):
        super().__init__(parent)
        self._pause_img = _pause_icon()  # kept as attributes so they aren't garbage-collected
        self._play_img  = _play_icon()
        self._back_btn      = tk.Button(self, text="Back", command=on_back,         state=tk.DISABLED)
        self._seek_back_btn = tk.Button(self, text="-15s", command=on_seek_back,    state=tk.DISABLED)
        self._seek_fwd_btn  = tk.Button(self, text="+15s", command=on_seek_forward, state=tk.DISABLED)
        self._next_btn      = tk.Button(self, text="Next", command=on_next,         state=tk.DISABLED)
        self._pause_btn     = tk.Button(self, image=self._pause_img, command=on_pause_resume, state=tk.DISABLED)
        # equal-weight uniform columns give every button the same width; nsew stretches
        # each button to fill its cell, so widths and heights all match
        for i, btn in enumerate(self._buttons()):
            _emphasize(btn)
            self.columnconfigure(i, weight=1, uniform="transport")
            btn.grid(row=0, column=i, sticky="nsew", padx=4)

    def _buttons(self):
        return (self._back_btn, self._seek_back_btn, self._seek_fwd_btn, self._next_btn, self._pause_btn)

    def enable(self):
        for btn in self._buttons():
            btn.config(state=tk.NORMAL)

    def set_paused(self, paused):
        self._pause_btn.config(image=self._play_img if paused else self._pause_img)


class LibraryFrame(tk.Frame):
    def __init__(self, parent, on_play_now, on_enqueue):
        super().__init__(parent)
        self._on_play_now = on_play_now
        self._on_enqueue  = on_enqueue
        self._menu_target = None
        cols = ("title", "artist", "duration", "plays")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        self._tree.heading("title",    text="Title")
        self._tree.heading("artist",   text="Artist")
        self._tree.heading("duration", text="Duration")
        self._tree.heading("plays",    text="Plays")
        self._tree.column("title",    stretch=True,  minwidth=120, width=260)
        self._tree.column("artist",   stretch=True,  minwidth=80,  width=160)
        self._tree.column("duration", stretch=False, minwidth=60,  width=70,  anchor="e")
        self._tree.column("plays",    stretch=False, minwidth=40,  width=50,  anchor="e")
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._menu = tk.Menu(self, tearoff=0)
        self._menu.add_command(label="Play now", command=lambda: self._fire(self._on_play_now))
        self._menu.add_command(label="Add to queue", command=lambda: self._fire(self._on_enqueue))
        self._tree.bind("<Double-1>", self._on_double_click)
        self._tree.bind("<Button-3>", self._on_right_click)

    def populate(self, tracks):
        self._tree.delete(*self._tree.get_children())
        for t in tracks:
            self._tree.insert("", tk.END, iid=t["filepath"], values=(
                t["title"], t["artist"], _fmt(t["duration"]), t["play_count"] or 0
            ))

    def _on_double_click(self, event):
        filepath = self._tree.identify_row(event.y)  # row iid is the track's filepath
        if filepath:
            self._on_play_now(filepath)

    def _on_right_click(self, event):
        filepath = self._tree.identify_row(event.y)
        if not filepath:
            return
        self._tree.selection_set(filepath)
        self._menu_target = filepath
        try:
            self._menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._menu.grab_release()

    def _fire(self, callback):
        if self._menu_target:
            callback(self._menu_target)
