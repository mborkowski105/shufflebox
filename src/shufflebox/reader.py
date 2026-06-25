from pathlib import Path
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

AUDIO_EXTENSIONS = {".mp3", ".flac", ".m4a", ".ogg", ".wav"}


def read_directory(path):
    return [_read_tags(f) for f in Path(path).rglob("*") if f.suffix.lower() in AUDIO_EXTENSIONS]


def _read_tags(path):
    track = {
        "filepath": str(path),
        "title":    "Unknown Title",
        "artist":   "Unknown Artist",
        "album":    "Unknown Album",
        "year":     None,
        "duration": None,
    }
    try:
        tags = ID3(str(path))
        if "TIT2" in tags: track["title"]  = str(tags["TIT2"])
        if "TPE1" in tags: track["artist"] = str(tags["TPE1"])
        if "TALB" in tags: track["album"]  = str(tags["TALB"])
        if "TDRC" in tags: track["year"]   = int(str(tags["TDRC"])[:4])
    except Exception:
        pass
    try:
        track["duration"] = int(MP3(str(path)).info.length)
    except Exception:
        pass
    return track
