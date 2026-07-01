from unittest.mock import patch
from shufflebox.player import Player

TRACK = {"filepath": "/fake.mp3", "title": "Track A", "artist": "Artist X", "album": "Album 1", "year": 2000, "duration": 180}


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


class TestTransport:
    def test_current_after_play(self):
        with patch("shufflebox.player.pygame"):
            player = Player()
            player.play(TRACK)
        assert player.current == TRACK

    def test_paused_after_pause(self):
        with patch("shufflebox.player.pygame"):
            player = Player()
            player.play(TRACK)
            player.pause()
        assert player.paused

    def test_not_paused_after_resume(self):
        with patch("shufflebox.player.pygame"):
            player = Player()
            player.play(TRACK)
            player.pause()
            player.resume()
        assert not player.paused

    def test_restart_clears_paused(self):
        with patch("shufflebox.player.pygame"):
            player = Player()
            player.play(TRACK)
            player.pause()
            player.restart()
        assert not player.paused

    def test_restart_without_current_is_noop(self):
        with patch("shufflebox.player.pygame") as mock_pygame:
            player = Player()
            player.restart()
            mock_pygame.mixer.music.play.assert_not_called()


class TestClock:
    def test_elapsed_reflects_clock(self):
        with patch("shufflebox.player.pygame"):
            clock = FakeClock()
            player = Player(clock=clock)
            player.play(TRACK)
            clock.advance(45)
            assert player.elapsed == 45

    def test_elapsed_frozen_while_paused(self):
        with patch("shufflebox.player.pygame"):
            clock = FakeClock()
            player = Player(clock=clock)
            player.play(TRACK)
            clock.advance(40)
            player.pause()
            clock.advance(10)  # time passes while paused
            assert player.elapsed == 40

    def test_elapsed_resumes_after_pause(self):
        with patch("shufflebox.player.pygame"):
            clock = FakeClock()
            player = Player(clock=clock)
            player.play(TRACK)
            clock.advance(40)
            player.pause()
            clock.advance(10)
            player.resume()
            clock.advance(5)
            assert player.elapsed == 45

    def test_elapsed_clamps_to_duration(self):
        with patch("shufflebox.player.pygame"):
            clock = FakeClock()
            player = Player(clock=clock)
            player.play(TRACK)  # 180s
            clock.advance(200)
            assert player.elapsed == 180

    def test_elapsed_zero_without_track(self):
        with patch("shufflebox.player.pygame"):
            player = Player(clock=FakeClock())
            assert player.elapsed == 0.0


class TestSeek:
    def test_seek_forward_replays_from_target(self):
        with patch("shufflebox.player.pygame") as mock_pygame:
            clock = FakeClock()
            player = Player(clock=clock)
            player.play(TRACK)
            clock.advance(30)
            player.seek(15)  # 30s + 15s = 45s
            mock_pygame.mixer.music.play.assert_called_with(start=45)

    def test_seek_backward_clamps_to_zero(self):
        with patch("shufflebox.player.pygame") as mock_pygame:
            clock = FakeClock()
            player = Player(clock=clock)
            player.play(TRACK)
            clock.advance(5)
            player.seek(-15)  # 5s - 15s = -10s, clamped to 0
            mock_pygame.mixer.music.play.assert_called_with(start=0)

    def test_seek_clamps_to_duration(self):
        with patch("shufflebox.player.pygame") as mock_pygame:
            clock = FakeClock()
            player = Player(clock=clock)
            player.play(TRACK)  # 180s
            clock.advance(170)
            player.seek(15)  # 185s, clamped to 180s
            mock_pygame.mixer.music.play.assert_called_with(start=180)

    def test_elapsed_after_seek_advances_from_target(self):
        with patch("shufflebox.player.pygame"):
            clock = FakeClock()
            player = Player(clock=clock)
            player.play(TRACK)
            clock.advance(30)
            player.seek(15)   # now at 45s
            clock.advance(5)  # play 5 more seconds
            assert player.elapsed == 50
