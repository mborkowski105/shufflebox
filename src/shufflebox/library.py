import sqlite3
from .reader import read_directory

class Library:
    def __init__(self, db_path=":memory:", scanner=read_directory):
        self._scanner = scanner
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                filepath   TEXT PRIMARY KEY,
                title      TEXT,
                artist     TEXT,
                album      TEXT,
                year       INTEGER,
                duration   INTEGER,
                play_count INTEGER DEFAULT 0
            )
        """)
        try:
            self.conn.execute("ALTER TABLE tracks ADD COLUMN play_count INTEGER DEFAULT 0")
        except Exception:
            pass
        self.conn.commit()

    def load(self, directory):
        tracks = self._scanner(directory)
        self.conn.executemany(
            "INSERT INTO tracks (filepath, title, artist, album, year, duration, play_count) "
            "VALUES (:filepath, :title, :artist, :album, :year, :duration, 0) "
            "ON CONFLICT(filepath) DO UPDATE SET "
            "title=excluded.title, artist=excluded.artist, album=excluded.album, "
            "year=excluded.year, duration=excluded.duration",
            tracks,
        )
        self.conn.commit()

    def query(self):
        return self.conn.execute("SELECT * FROM tracks").fetchall()

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]

    def play_count(self, filepath):
        return self.conn.execute(
            "SELECT play_count FROM tracks WHERE filepath = ?", (filepath,)
        ).fetchone()[0]

    def increment_play_count(self, filepath):
        self.conn.execute(
            "UPDATE tracks SET play_count = play_count + 1 WHERE filepath = ?", (filepath,)
        )
        self.conn.commit()
