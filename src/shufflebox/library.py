import sqlite3
from .reader import read_directory


class Library:
    def __init__(self, db_path=":memory:", scanner=read_directory):
        self._scanner = scanner
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                filepath TEXT PRIMARY KEY,
                title    TEXT,
                artist   TEXT,
                album    TEXT,
                year     INTEGER,
                duration INTEGER
            )
        """)
        self.conn.commit()

    def load(self, directory):
        tracks = self._scanner(directory)
        self.conn.executemany(
            "INSERT OR REPLACE INTO tracks (filepath, title, artist, album, year, duration) "
            "VALUES (:filepath, :title, :artist, :album, :year, :duration)",
            tracks,
        )
        self.conn.commit()

    def query(self, artist=None):
        if artist:
            return self.conn.execute(
                "SELECT * FROM tracks WHERE artist = ?", (artist,)
            ).fetchall()
        return self.conn.execute("SELECT * FROM tracks").fetchall()

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
