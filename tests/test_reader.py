from shufflebox.reader import read_directory


class TestFileDiscovery:
    def test_ignores_non_audio(self, tmp_path):
        audio = ("a.mp3", "b.mp3", "c.mp3")
        for name in audio:
            (tmp_path / name).write_bytes(b"")
        (tmp_path / "readme.txt").write_text("hello")
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
        tagged = [t for t in tracks if t["artist"] != "Unknown Artist"]
        assert len(tagged) > 0
        track = tagged[0]
        assert track["title"] != "Unknown Title"
        assert track["album"] != "Unknown Album"
        assert track["year"]  is not None

    def test_defaults_on_missing(self, tmp_path):
        (tmp_path / "untagged.mp3").write_bytes(b"")
        track = read_directory(tmp_path)[0]
        assert track["artist"] == "Unknown Artist"
        assert track["title"]  == "Unknown Title"
        assert track["album"]  == "Unknown Album"
        assert track["year"]   is None

    def test_reads_duration(self, music_dir):
        tracks = read_directory(music_dir)
        assert any(t["duration"] is not None and t["duration"] > 0 for t in tracks)

    def test_missing_duration(self, tmp_path):
        (tmp_path / "untagged.mp3").write_bytes(b"")
        assert read_directory(tmp_path)[0]["duration"] is None
