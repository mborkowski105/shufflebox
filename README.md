# shufflebox

A local-first music player with truly random shuffle.

Spotify's shuffle isn't random — it avoids repetition, weights recent plays, and nudges you toward familiar tracks. Shufflebox doesn't do any of that. You get a seeded, deterministic shuffle through your entire library: every song plays exactly once before anything repeats.

## Features

- Truly random shuffle — no weighting, no history bias
- Reproducible seeds (1–999): same seed, same order, every time
- Back / Pause / Next / Reshuffle controls
- Back within 3 seconds → previous track; after 3 seconds → restart current
- iTunes-style library view with Title, Artist, and Duration columns
- Reads MP3, FLAC, M4A, OGG, and WAV files recursively from any folder

## Requirements

- Python 3.10+
- [pygame-ce](https://github.com/pygame-community/pygame-ce)
- [mutagen](https://mutagen.readthedocs.io/)

## Install

```bash
git clone https://github.com/your-username/shufflebox.git
cd shufflebox
pip install -e .
```

## Run

```bash
shufflebox
```

Or directly:

```bash
python src/shufflebox/app.py
```

## Tests

```bash
pip install pytest
python -m pytest -v
```

## Architecture

```
reader.py    — filesystem traversal + ID3/mutagen tag reading
library.py   — SQLite storage (stdlib sqlite3)
shuffler.py  — pure shuffle functions (shuffled_order, resolve_seed, random_seed)
queue.py     — ordered playback queue with next/previous
player.py    — pygame-ce audio playback
ui.py        — Tkinter frame components
app.py       — wiring
```

## License

Public domain. Do whatever you want with it.
