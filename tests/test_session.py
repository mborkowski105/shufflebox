from unittest.mock import MagicMock
from shufflebox.library import Library
from shufflebox.queue import Queue
from shufflebox.session import Session

TRACKS = [
    {"filepath": "/a.mp3", "title": "A", "artist": "X", "album": "1", "year": 2000, "duration": 180},
    {"filepath": "/b.mp3", "title": "B", "artist": "X", "album": "1", "year": 2001, "duration": 200},
]


def fake_scanner(_directory):
    return TRACKS


def make_player(*, current, elapsed, playing, paused):
    player = MagicMock()
    player.current = current
    player.elapsed = elapsed
    player.playing = playing
    player.paused  = paused
    return player


def make_session(player):
    library = Library(scanner=fake_scanner)
    session = Session(library, Queue(), player)
    session.load("/any", "", play=False)  # prime the library + queue, no playback
    return session, library


def test_next_counts_play_when_position_past_threshold():
    # the seek-forward bug: true position is 160s of 180s, still playing
    player = make_player(current=dict(TRACKS[0]), elapsed=160, playing=True, paused=False)
    session, library = make_session(player)
    assert session.next() is True
    assert library.play_count("/a.mp3") == 1


def test_next_does_not_count_when_skipped_early():
    player = make_player(current=dict(TRACKS[0]), elapsed=5, playing=True, paused=False)
    session, library = make_session(player)
    assert session.next() is False
    assert library.play_count("/a.mp3") == 0


def test_tick_counts_finished_track_even_if_short():
    # track ended on its own (not playing, not paused) — counts regardless of position
    player = make_player(current=dict(TRACKS[0]), elapsed=2, playing=False, paused=False)
    session, library = make_session(player)
    assert session.tick() is True
    assert library.play_count("/a.mp3") == 1


def test_paused_skip_is_not_treated_as_finished():
    # paused then Next: not "finished"; position is early, so no count
    player = make_player(current=dict(TRACKS[0]), elapsed=5, playing=False, paused=True)
    session, library = make_session(player)
    assert session.next() is False
    assert library.play_count("/a.mp3") == 0


def test_enqueue_front_does_not_interrupt_current():
    player = make_player(current=dict(TRACKS[0]), elapsed=100, playing=True, paused=False)
    session, library = make_session(player)
    session.enqueue_front("/b.mp3")
    player.play.assert_not_called()               # current track keeps playing
    session.next()                                # advancing now reaches the queued track
    assert player.play.call_args.args[0]["filepath"] == "/b.mp3"


def test_enqueue_front_starts_playback_when_idle():
    player = make_player(current=None, elapsed=0, playing=False, paused=False)
    session, library = make_session(player)
    session.enqueue_front("/b.mp3")
    assert player.play.call_args.args[0]["filepath"] == "/b.mp3"


def test_enqueue_front_unknown_filepath_is_noop():
    player = make_player(current=dict(TRACKS[0]), elapsed=100, playing=True, paused=False)
    session, library = make_session(player)
    assert session.enqueue_front("/nope.mp3") is False
    player.play.assert_not_called()


def test_play_now_plays_immediately_and_counts_outgoing():
    player = make_player(current=dict(TRACKS[0]), elapsed=160, playing=True, paused=False)
    session, library = make_session(player)
    assert session.play_now("/b.mp3") is True      # interrupted track a was past threshold
    assert player.play.call_args.args[0]["filepath"] == "/b.mp3"
    assert library.play_count("/a.mp3") == 1


def test_play_now_unknown_filepath_is_noop():
    player = make_player(current=dict(TRACKS[0]), elapsed=160, playing=True, paused=False)
    session, library = make_session(player)
    assert session.play_now("/nope.mp3") is False
    player.play.assert_not_called()
