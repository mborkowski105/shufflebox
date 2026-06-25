from shufflebox.library import Library

FAKE_TRACKS = [
    {"filepath": "/a.mp3", "title": "Track A", "artist": "Artist X", "album": "Album 1", "year": 2000, "duration": 180},
    {"filepath": "/b.mp3", "title": "Track B", "artist": "Artist X", "album": "Album 1", "year": 2001, "duration": 214},
    {"filepath": "/c.mp3", "title": "Track C", "artist": "Artist Y", "album": "Album 2", "year": 2002, "duration": 220},
]

def fake_scanner(_directory):
    return FAKE_TRACKS


def test_stores_tracks():
    lib = Library(scanner=fake_scanner)
    lib.load("/any")
    assert lib.count() == len(FAKE_TRACKS)


def test_query_by_artist():
    lib = Library(scanner=fake_scanner)
    lib.load("/any")
    expected = sum(1 for t in FAKE_TRACKS if t["artist"] == "Artist X")
    assert len(lib.query(artist="Artist X")) == expected


def test_count():
    lib = Library(scanner=fake_scanner)
    lib.load("/any")
    assert lib.count() == len(FAKE_TRACKS)


def test_integration(music_dir):
    lib = Library()
    lib.load(music_dir)
    expected = len(list(music_dir.glob("*.mp3")))
    assert lib.count() == expected
