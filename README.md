# shufflebox

A local-first music player with truly random shuffle.

Spotify's shuffle isn't random — it avoids repetition, weights recent plays, and nudges you toward familiar tracks. Shufflebox doesn't do any of that. You get a seeded, deterministic shuffle through your entire library: every song plays exactly once before anything repeats.

## Features

- **Truly random shuffle** — no weighting, no history bias
- **Reproducible seeds** (1–999): same seed, same order, every time; reshuffle for a fresh order whenever you like
- **Play counts** — tracked per track and persisted across sessions; a play counts once you've heard ~30% of it (or it finishes). Shown in the library's Plays column
- **Library view** (Title / Artist / Duration / Plays):
  - double-click a track to play it now
  - right-click to add tracks to the front of the queue (in order)
- **Transport**: Back (previous track within 3s, restart after), −15s / +15s seek, Next, Pause/Play
- Reads **MP3, FLAC, OGG, and WAV** recursively from any folder, falling back to the filename when a track has no tags

## Requirements

- Python 3.10+ (Tkinter ships with the standard library)
- [pygame-ce](https://github.com/pygame-community/pygame-ce)
- [mutagen](https://mutagen.readthedocs.io/)

## Install

```bash
git clone https://github.com/mborkowski105/shufflebox.git
cd shufflebox
pip install -e .
```

## Run

```bash
shufflebox
```

Or as a module:

```bash
python -m shufflebox.app
```

Click the 📁 button to choose a music folder, then 🔀 to start a shuffle. Your library and play counts are stored in `~/.shufflebox/library.db`.

## Tests

```bash
pip install pytest
python -m pytest -v
```

The pure-logic and storage tests need no audio. A few integration tests read real audio files from `tests/fixtures/`; those are local-only (not committed) and skip automatically when the folder is empty.

## Architecture

```
reader.py    — filesystem traversal + format-agnostic tag/duration reading (mutagen)
library.py   — SQLite storage; tracks + persisted play counts
stats.py     — play-count policy (pure functions): the 30% listen threshold
shuffler.py  — pure shuffle functions (shuffled_order, resolve_seed, random_seed)
queue.py     — ordered queue with next/previous and front-insert
player.py    — pygame-ce audio + a self-owned monotonic playback clock
session.py   — playback coordination over library/queue/player (UI-free, unit-tested)
ui.py        — Tkinter frame components
app.py       — thin Tkinter shell: wires the UI to a Session and reflects its state
```

The key seam: `player` owns everything about the *current track* (transport + elapsed clock), while `session` owns the *journey through many tracks* (what plays next, the seed, when a play counts). `app` is only construction and reflection — no decisions — which is why `session` can be tested without any UI.

## License

Public domain. Do whatever you want with it.
