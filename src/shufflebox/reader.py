from pathlib import Path
from mutagen import File as MutagenFile

# M4A/AAC omitted deliberately: pygame/SDL playback of it is unreliable across platforms
AUDIO_EXTENSIONS = {".mp3", ".flac", ".ogg", ".wav"}


def read_directory(path):
    return [_read_tags(f) for f in Path(path).rglob("*") if f.suffix.lower() in AUDIO_EXTENSIONS]


def _read_tags(path):
    track = {
        "filepath": str(path),
        "title":    path.stem,          # fall back to the filename, not "Unknown"
        "artist":   "Unknown Artist",
        "album":    "Unknown Album",
        "year":     None,
        "duration": None,
    }
    try:
        audio = MutagenFile(str(path), easy=True)
    except Exception:
        audio = None
    if audio is None:
        return track

    if audio.info is not None:
        track["duration"] = int(audio.info.length)
    tags = audio.tags or {}
    track["title"]  = _first(tags, "title")  or path.stem
    track["artist"] = _first(tags, "artist") or "Unknown Artist"
    track["album"]  = _first(tags, "album")  or "Unknown Album"
    track["year"]   = _year(_first(tags, "date"))
    return track


def _first(tags, key):
    value = tags.get(key)
    return value[0] if value else None


def _year(raw):
    try:
        return int(str(raw)[:4])
    except (ValueError, TypeError):
        return None
