from shufflebox.library import Library

FAKE_TRACKS = [
    {"filepath": "/a.mp3", "title": "Track A", "artist": "Artist X", "album": "Album 1", "year": 2000, "duration": 180},
    {"filepath": "/b.mp3", "title": "Track B", "artist": "Artist X", "album": "Album 1", "year": 2001, "duration": 214},
    {"filepath": "/c.mp3", "title": "Track C", "artist": "Artist Y", "album": "Album 2", "year": 2002, "duration": 220},
]


def fake_scanner(_directory):
    return FAKE_TRACKS


class _Folder:
    """A scanner whose returned tracks can be changed, to simulate a folder mutating."""

    def __init__(self, tracks):
        self.tracks = list(tracks)

    def __call__(self, _directory):
        return self.tracks


class TestStorage:
    def test_stores_tracks(self):
        lib = Library(scanner=fake_scanner)
        lib.load("/any")
        assert lib.count() == len(FAKE_TRACKS)

    def test_integration(self, music_dir):
        lib = Library()
        lib.load(music_dir)
        expected = len(list(music_dir.glob("*.mp3")))
        assert lib.count() == expected

    def test_load_prunes_tracks_no_longer_in_folder(self):
        folder = _Folder(FAKE_TRACKS)
        lib = Library(scanner=folder)
        lib.load("/any")
        folder.tracks = FAKE_TRACKS[:2]  # /c.mp3 removed from the folder
        lib.load("/any")
        assert lib.count() == 2


class TestPlayCounts:
    def test_increment_play_count(self):
        lib = Library(scanner=fake_scanner)
        lib.load("/any")
        lib.increment_play_count("/a.mp3")
        lib.increment_play_count("/a.mp3")
        assert lib.play_count("/a.mp3") == 2

    def test_increment_is_per_track(self):
        lib = Library(scanner=fake_scanner)
        lib.load("/any")
        lib.increment_play_count("/a.mp3")
        assert lib.play_count("/b.mp3") == 0

    def test_pruning_keeps_counts_for_surviving_tracks(self):
        folder = _Folder(FAKE_TRACKS)
        lib = Library(scanner=folder)
        lib.load("/any")
        lib.increment_play_count("/a.mp3")
        folder.tracks = FAKE_TRACKS[:2]  # /c.mp3 gone; /a.mp3 survives
        lib.load("/any")
        assert lib.play_count("/a.mp3") == 1

    def test_load_preserves_play_count_on_rescan(self):
        lib = Library(scanner=fake_scanner)
        lib.load("/any")
        lib.increment_play_count("/a.mp3")
        lib.increment_play_count("/a.mp3")
        lib.load("/any")
        assert lib.play_count("/a.mp3") == 2

    def test_persists_across_sessions(self, tmp_path):
        db = str(tmp_path / "library.db")
        lib = Library(db_path=db, scanner=fake_scanner)
        lib.load("/any")
        lib.increment_play_count("/a.mp3")
        lib.increment_play_count("/a.mp3")

        reopened = Library(db_path=db, scanner=fake_scanner)
        assert reopened.play_count("/a.mp3") == 2
