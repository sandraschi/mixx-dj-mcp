"""SQLite database for track analysis, play history, and set recordings."""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path

_db_lock = threading.Lock()
_db_path: Path | None = None


def get_db() -> sqlite3.Connection:
    global _db_path
    if _db_path is None:
        _db_path = Path(__file__).parent.parent.parent / "data" / "mixx.db"
        _db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with _db_lock:
        conn = get_db()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS track_analysis (
                file_path TEXT PRIMARY KEY,
                bpm REAL,
                key TEXT,
                key_alternative TEXT,
                energy REAL,
                duration REAL,
                analyzed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS play_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck INTEGER,
                track_path TEXT,
                track_title TEXT,
                track_artist TEXT,
                bpm REAL,
                key TEXT,
                started_at TEXT,
                duration_seconds REAL,
                cues_used INTEGER DEFAULT 0,
                loops_used INTEGER DEFAULT 0,
                effects_used TEXT DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS transitions_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_id TEXT,
                from_deck INTEGER,
                to_deck INTEGER,
                transition_type TEXT,
                bpm_a REAL,
                bpm_b REAL,
                key_a TEXT,
                key_b TEXT,
                duration_seconds REAL,
                timestamp TEXT
            );
            CREATE TABLE IF NOT EXISTS set_recordings (
                id TEXT PRIMARY KEY,
                name TEXT,
                started_at TEXT,
                ended_at TEXT,
                duration_seconds REAL,
                track_count INTEGER DEFAULT 0,
                transition_count INTEGER DEFAULT 0,
                osc_events INTEGER DEFAULT 0,
                file_path TEXT
            );
        """)
        conn.commit()


def store_analysis(
    file_path: str,
    bpm: float | None,
    key: str | None,
    key_alt: str | None,
    energy: float | None,
    duration: float | None,
):
    with _db_lock:
        get_db().execute(
            "INSERT OR REPLACE INTO track_analysis VALUES (?,?,?,?,?,?,?)",
            (file_path, bpm, key, key_alt, energy, duration, datetime.utcnow().isoformat()),
        )
        get_db().commit()


def log_play(deck: int, track_path: str, title: str, artist: str, bpm: float, key: str, duration: float):
    with _db_lock:
        get_db().execute(
            "INSERT INTO play_history "
            "(deck, track_path, track_title, track_artist, bpm, key, started_at, duration_seconds) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (deck, track_path, title, artist, bpm, key, datetime.utcnow().isoformat(), duration),
        )
        get_db().commit()


def log_transition(
    set_id: str | None, from_deck: int, to_deck: int, ttype: str, bpm_a: float, bpm_b: float, key_a: str, key_b: str
):
    with _db_lock:
        get_db().execute(
            "INSERT INTO transitions_log "
            "(set_id, from_deck, to_deck, transition_type, bpm_a, bpm_b, key_a, key_b, timestamp) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (set_id, from_deck, to_deck, ttype, bpm_a, bpm_b, key_a, key_b, datetime.utcnow().isoformat()),
        )
        get_db().commit()


def style_profile() -> dict:
    with _db_lock:
        cur = get_db().execute(
            "SELECT COUNT(*) as total, AVG(bpm) as avg_bpm, "
            "COUNT(DISTINCT key) as key_diversity, "
            "AVG(duration_seconds) as avg_play_duration "
            "FROM play_history"
        )
        row = cur.fetchone()
        cur2 = get_db().execute(
            "SELECT transition_type, COUNT(*) as cnt FROM transitions_log "
            "GROUP BY transition_type ORDER BY cnt DESC LIMIT 5"
        )
        top_transitions = [dict(r) for r in cur2.fetchall()]
        cur3 = get_db().execute(
            "SELECT key, COUNT(*) as cnt FROM play_history "
            "WHERE key IS NOT NULL AND key != '' GROUP BY key ORDER BY cnt DESC LIMIT 10"
        )
        top_keys = [dict(r) for r in cur3.fetchall()]
        cur4 = get_db().execute(
            "SELECT track_title, track_artist, COUNT(*) as cnt "
            "FROM play_history GROUP BY track_path ORDER BY cnt DESC LIMIT 10"
        )
        top_tracks = [dict(r) for r in cur4.fetchall()]
        return {
            "total_plays": row["total"] if row else 0,
            "avg_bpm": round(row["avg_bpm"], 1) if row and row["avg_bpm"] else 0,
            "key_diversity": row["key_diversity"] if row else 0,
            "avg_play_duration_seconds": round(row["avg_play_duration"], 1) if row and row["avg_play_duration"] else 0,
            "top_transitions": top_transitions,
            "top_keys": top_keys,
            "most_played": top_tracks,
        }


def suggest_tracks(limit: int = 10) -> list[dict]:
    with _db_lock:
        cur = get_db().execute(
            "SELECT track_path, track_title, track_artist, bpm, key, MAX(started_at) as last_played, "
            "COUNT(*) as play_count FROM play_history "
            "GROUP BY track_path ORDER BY last_played ASC LIMIT ?",
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]


init_db()
