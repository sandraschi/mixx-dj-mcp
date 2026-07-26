import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mixx_dj_mcp.mixxx_library import format_duration, search_library


@pytest.fixture
def sample_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "mixxxdb.sqlite"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE track_locations (
            id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            directory TEXT,
            fs_deleted INTEGER DEFAULT 0
        );
        CREATE TABLE library (
            id INTEGER PRIMARY KEY,
            artist TEXT,
            title TEXT,
            album TEXT,
            genre TEXT,
            bpm REAL,
            key TEXT,
            duration REAL,
            location INTEGER,
            mixxx_deleted INTEGER DEFAULT 0
        );
        """
    )
    conn.execute(
        "INSERT INTO track_locations (id, location, directory) VALUES (1, ?, ?)",
        (r"D:\music\artist - tech house.mp3", r"D:\music"),
    )
    conn.execute(
        """
        INSERT INTO library (artist, title, album, genre, bpm, key, duration, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("Daft Punk", "Around the World", "Homework", "Tech House", 121.0, "8A", 420, 1),
    )
    conn.commit()
    conn.close()
    return db_path


def test_format_duration():
    assert format_duration(65) == "1:05"
    assert format_duration(None) == "0:00"


def test_search_library_by_genre(sample_db: Path):
    result = search_library("tech house", db_path=sample_db)
    assert result["total"] == 1
    assert result["results"][0]["title"] == "Around the World"
    assert result["results"][0]["id"].endswith(".mp3")


def test_search_library_by_bpm(sample_db: Path):
    result = search_library("121 bpm", db_path=sample_db)
    assert result["total"] == 1


def test_search_library_empty_query():
    result = search_library("")
    assert result["total"] == 0
    assert "required" in result["message"].lower()


@pytest.mark.asyncio
async def test_mixx_library_search_returns_db_rows(sample_db: Path, monkeypatch):
    from mixx_dj_mcp.tools import library as library_tool

    monkeypatch.setattr(library_tool, "search_library", lambda q: search_library(q, db_path=sample_db))
    result = await library_tool.mixx_library(operation="search", query="daft")
    assert result["success"] is True
    assert result["data"]["total"] == 1


def test_library_search_api(sample_db: Path, monkeypatch):
    from mixx_dj_mcp import server

    monkeypatch.setattr(server, "search_library", lambda q, limit=50: search_library(q, limit=limit, db_path=sample_db))

    bridge = server.get_osc_bridge()
    bridge.send = lambda *args, **kwargs: None  # type: ignore[method-assign]

    client = TestClient(server.fastapi_app)
    response = client.post("/api/library/search", json={"query": "daft"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["results"][0]["artist"] == "Daft Punk"


def test_effects_api(monkeypatch):
    from mixx_dj_mcp import server

    async def fake_dispatch(_dispatch, name, arguments=None):
        assert name == "mixx_effects"
        assert arguments["operation"] == "chain_load"
        return {"success": True, "message": "ok", "data": arguments}

    monkeypatch.setattr(server, "dispatch_tool", fake_dispatch)

    client = TestClient(server.fastapi_app)
    response = client.post(
        "/api/v1/effects",
        json={"operation": "chain_load", "rack": 1, "unit": 1, "effect": "Reverb"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_tools_call_api(monkeypatch):
    from mixx_dj_mcp import server

    async def fake_dispatch(_dispatch, name, arguments=None):
        return {"success": True, "message": name, "data": arguments or {}}

    monkeypatch.setattr(server, "dispatch_tool", fake_dispatch)

    client = TestClient(server.fastapi_app)
    response = client.post(
        "/api/v1/tools/call",
        json={"name": "mixx_daw", "arguments": {"operation": "resolume_sync", "deck": 1}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tool"] == "mixx_daw"
    assert body["result"]["success"] is True
