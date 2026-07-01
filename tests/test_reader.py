import wave
from shufflebox.reader import read_directory


def _make_wav(path, seconds=1):
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x00\x00" * 8000 * seconds)


class TestFileDiscovery:
    def test_ignores_non_audio(self, tmp_path):
        audio = ("a.mp3", "b.mp3", "c.mp3")
        for name in audio:
            (tmp_path / name).write_bytes(b"")
        (tmp_path / "readme.txt").write_text("hello")
        (tmp_path / "song.m4a").write_bytes(b"")  # M4A/AAC unsupported: playback is unreliable
        assert len(read_directory(tmp_path)) == len(audio)

    def test_recurses(self, tmp_path):
        sub = tmp_path / "artist" / "album"
        sub.mkdir(parents=True)
        files = [tmp_path / "a.mp3", sub / "b.mp3", sub / "c.mp3"]
        for f in files:
            f.write_bytes(b"")
        assert len(read_directory(tmp_path)) == len(files)

    def test_empty(self, tmp_path):
        assert read_directory(tmp_path) == []


class TestTagReading:
    def test_reads_all_fields(self, music_dir):
        tracks = read_directory(music_dir)
        assert any(t["title"] and t["artist"] != "Unknown Artist" for t in tracks)
        assert any(t["album"] != "Unknown Album" for t in tracks)
        assert any(t["year"] for t in tracks)

    def test_reads_duration(self, music_dir):
        tracks = read_directory(music_dir)
        assert any(t["duration"] and t["duration"] > 0 for t in tracks)

    def test_untagged_falls_back_to_filename(self, tmp_path):
        (tmp_path / "untagged.mp3").write_bytes(b"")
        track = read_directory(tmp_path)[0]
        assert track["title"] == "untagged"      # filename stem, not "Unknown Title"
        assert track["artist"] == "Unknown Artist"
        assert track["album"] == "Unknown Album"
        assert track["year"] is None
        assert track["duration"] is None

    def test_reads_non_mp3_format(self, tmp_path):
        _make_wav(tmp_path / "beep.wav", seconds=1)
        track = read_directory(tmp_path)[0]
        assert track["duration"] == 1
        assert track["title"] == "beep"          # bare WAV has no tags → filename
