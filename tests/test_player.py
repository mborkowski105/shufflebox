from unittest.mock import patch
from shufflebox.player import Player

TRACK = {"filepath": "/fake.mp3", "title": "Track A", "artist": "Artist X", "album": "Album 1", "year": 2000}


class TestPlayer:
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
