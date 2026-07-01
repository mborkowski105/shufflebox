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

# Launch the app (requires editable install; package imports need the module context)
python -m shufflebox.app

# Install/reinstall package in editable mode (required after pyproject.toml changes)
pip install -e .
```

## Architecture

**app (UI shell) → session → { library → reader, queue, player }**
**session draws on shuffler (order) and stats (play-count policy)**

The load-bearing distinction: `player` owns everything about *the current track* (transport + the position clock); `session` owns *the journey through many tracks* (what plays next, the seed, when a play counts). Litmus: does it need to know there's more than one track? → `session`; true of a single track alone? → `player`.

- `reader.py` — pure filesystem layer. `read_directory(path)` walks recursively and returns dicts with `filepath`, `title`, `artist`, `album`, `year`, `duration`. Tags/duration are read format-agnostically via `mutagen.File(..., easy=True)` (mp3/flac/ogg/wav — M4A/AAC deliberately excluded, unreliable playback); missing title falls back to the filename stem, other fields to `"Unknown ..."` / `None`.
- `library.py` — SQLite storage. `Library.load(dir)` scans and upserts tracks (preserving play counts on rescan). `query()`, `count()`, `play_count(filepath)`, `increment_play_count(filepath)`.
- `stats.py` — play-count policy as pure functions. `should_count_play(elapsed, duration, finished)`: a finished track always counts, otherwise the 30% threshold applies. Future: `weights(tracks)` for shuffle weighting.
- `shuffler.py` — pure functions. `shuffled_order(tracks, seed)`, `resolve_seed()`, `random_seed()`.
- `queue.py` — index-based ordered list. `next()` and `previous()` without destructive pop.
- `player.py` — `Player`: everything about the current track — `play`/`pause`/`resume`/`seek`/`restart` over `pygame.mixer`, plus the `elapsed` position clock. The clock is self-owned (an injectable monotonic `clock`, not pygame's `get_pos()`); `get_busy()` is used only for end detection.
- `session.py` — `Session`: the listening session. Owns the queue, seed, and play-count tallies, and drives the `Player`. `next`/`back`/`reshuffle`/`seek`/`tick`. UI-free and pygame-free, so it's unit-tested with a mocked `Player`.
- `ui.py` — Tkinter Frame subclasses: `NowPlayingFrame`, `ControlsFrame`, `LibraryFrame`.
- `app.py` — UI shell: builds widgets, wires them to `Session`, reflects `Session` state back into the widgets. No decisions of its own. `pygame.mixer.init()` must precede `tk.Tk()` on Windows.

## Project rules

- No git commits or pushes unless I ask for it.
- TDD-first. Every feature starts as a failing test. Never modify a test to make it pass — fix the implementation. The tests and the code should reflect each other - in real implementation, and in intent as well. Avoid tests just for the sake of tests - tests should be valuable, enforce the goals and constraints of the features and functionality, and they should tests the endpoints of components within the application that actually face variable/dynamic stresses. If a test no longer holds its weight or doesn't test what it claims to test, it's a candidate for deletion or a further look. If a test reveals unwanted coupling or scope creep, it's also a flag to look deeper.
- Two modes of test-writing, plus one guard question:
  - **Feature work:** spec-first. Imagine the intended behavior, write it as a red test, then implement. Imagination leading the test is correct here — that's TDD working as designed.
  - **Bug work:** evidence-first. Reproduce the failure as a test, then *evaluate whether the test's spec or the implementation is wrong* before fixing. Don't skip the evaluation — a green test can encode a wrong spec (see: the seek bug, green for days against a false assumption about pygame).
  - **Before any defensive test/guard, ask: is this state actually reachable?** Unreachable → it's speculation; drop it (YAGNI). Reachable → it's not an edge case you imagined, it's spec; test and handle it. When a change expands the set of reachable states, walk that new state space and confirm each state is sound — that audit, not free-associating failure modes, is what surfaces real defects.
- Always think and code like the zen master Sandi Metz (not even necessarily just with respects to OOP — OOP may not always apply. Prefer 5-line methods, 100-line classes, yet without dogma. Good code reads like beautiful language or prose — almost like haikus or sonnets. Brevity is the soul of wit, but never at the cost of readability or taste. Good code is maximally expressive per line. The masterful space lives within these contradictions.).
- No frameworks, no over-abstraction with things like ORM's or middleware. Fewest external dependencies possible.
- Lean functional. Pure functions are the noble ideal — stateless, composable, trivially testable. State may be necessary sometimes, but a function that takes data and returns data often beats an object that holds data and mutates it. Classes earn their place only when genuinely encapsulating state or a resource: Library holds a DB connection, Queue holds position, Player holds pygame. If you're reaching for a class out of habit rather than necessity, maybe reach for a function instead.
- Tkinter UI is not unit-tested. The 1-second poll loop auto-advances playback — do not break this.
- Static fixtures in `tests/fixtures/` are real public-domain MP3s used for integration tests and manual app use.
