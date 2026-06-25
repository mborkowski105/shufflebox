# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
python -m pytest -v

# Run a single test file
python -m pytest tests/test_queue.py -v

# Run a single test
python -m pytest tests/test_shuffler.py::TestSeed::test_random_seed_in_range -v

# Launch the app
python src/shufflebox/app.py

# Install/reinstall package in editable mode (required after pyproject.toml changes)
pip install -e .
```

## Architecture

**scanner → library → app ← queue ← shuffler**

- `scanner.py` — pure filesystem layer. `scan_directory(path)` walks recursively, reads ID3 tags via mutagen, returns a list of dicts with keys `filepath`, `title`, `artist`, `album`, `year`, `duration`. Defaults to `"Unknown ..."` / `None` on missing or corrupt tags.
- `library.py` — SQLite storage (`sqlite3`, in-memory by default). `Library.load(dir)` calls the scanner and upserts via `INSERT OR REPLACE` on `filepath` as primary key. `query(artist=None)` and `count()` are the query surface.
- `shuffler.py` — pure functions only, no state. `shuffled_order(tracks, seed)` returns a deterministically shuffled list. `random_seed()` and `resolve_seed(value, current)` handle seed generation and validation (range 1–999).
- `queue.py` — stateful ordered list. `Queue.load(items)` replaces contents; `Queue.next()` pops and returns the front item, or `None` when empty.
- `player.py` — `Player` wraps `pygame.mixer` for audio playback. Pure audio, no shuffle logic.
- `app.py` — Tkinter GUI. Coordinates all components: loads library, generates shuffled order via `shuffled_order`, feeds it to `Queue`, plays from `Queue` via `Player`. `pygame.mixer.init()` must be called before `tk.Tk()` on Windows. A 1-second `after` poll loop auto-advances when a track ends.

## Project rules

- TDD-first. Every feature starts as a failing test. Never modify a test to make it pass — fix the implementation. The tests and the code should reflect each other - in real implementation, and in intent as well. Avoid tests just for the sake of tests - tests should be valuable, enforce the goals and constraints of the features and functionality, and they should tests the endpoints of components within the application that actually face variable/dynamic stresses. If a test no longer holds its weight or doesn't test what it claims to test, it's a candidate for deletion or a further look. If a test reveals unwanted coupling or scope creep, it's also a flag to look deeper.
- Always think and code like the zen master Sandi Metz (not even necessarily just with respects to OOP — OOP may not always apply. Prefer 5-line methods, 100-line classes, yet without dogma. Good code reads like beautiful language or prose — almost like haikus or sonnets. Brevity is the soul of wit, but never at the cost of readability or taste. Good code is maximally expressive per line. The masterful space lives within these contradictions.).
- No frameworks, no over-abstraction. Fewest dependencies possible.
- Use a class when encapsulating state or a resource (Library, Queue, Player). Otherwise prefer plain functions (shuffler.py).
- Tkinter UI is not unit-tested. The 1-second poll loop auto-advances playback — do not break this.
- Static fixtures in `tests/fixtures/` are real public-domain MP3s used for integration tests and manual app use.
