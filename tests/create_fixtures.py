"""
Run once to generate static fixture MP3s in tests/fixtures/.
These are real (silent) MP3 files usable for manual app testing.
"""
from pathlib import Path
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, Encoding

SONGS = [
    {"artist": "Thelonious Monk", "title": "Round Midnight",     "album": "Genius of Modern Music", "year": "1947"},
    {"artist": "Thelonious Monk", "title": "Straight No Chaser", "album": "Straight No Chaser",    "year": "1967"},
    {"artist": "John Coltrane",   "title": "Giant Steps",        "album": "Giant Steps",            "year": "1959"},
]

# Valid MPEG1 Layer3 128kbps 44100Hz stereo frame (417 bytes of silence)
_FRAME = b"\xff\xfb\x90\x00" + b"\x00" * 413

# 10 seconds: ceil(10 * 44100 / 1152) = 383 frames
_SILENT_MP3 = _FRAME * 383


def create(path, *, artist, title, album, year):
    path.write_bytes(_SILENT_MP3)
    tags = ID3()
    tags.add(TPE1(encoding=Encoding.UTF8, text=artist))
    tags.add(TIT2(encoding=Encoding.UTF8, text=title))
    tags.add(TALB(encoding=Encoding.UTF8, text=album))
    tags.add(TDRC(encoding=Encoding.UTF8, text=str(year)))
    tags.save(str(path))
    print(f"  {path.name}")


if __name__ == "__main__":
    out = Path(__file__).parent / "fixtures"
    out.mkdir(exist_ok=True)
    print("Creating fixtures...")
    for song in SONGS:
        create(out / f"{song['title']}.mp3", **song)
    print("Done.")
