import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from mixx_dj_mcp.library_search import search_library_smart
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
    result = search_library(query="tech house", db_path=sample_db)
    assert result["total"] == 1
    assert result["results"][0]["title"] == "Around the World"


@pytest.mark.asyncio
async def test_search_library_smart_uses_plex_when_available():
    plex_payload = {
        "results": [
            {
                "id": "plex:123",
                "title": "Plex Track",
                "artist": "Artist",
                "bpm": 0,
                "key": "Unknown",
                "length": "3:30",
                "source": "plex",
                "rating_key": "123",
                "thumb": "/library/metadata/1/thumb/abc",
                "type": "track",
            }
        ],
        "total": 1,
        "message": "Plex keyword search: 1 result(s)",
        "engine": "plex_keyword",
    }
    with (
        patch("mixx_dj_mcp.library_search.plex_client.plex_available", AsyncMock(return_value=True)),
        patch(
            "mixx_dj_mcp.library_search.plex_client.keyword_search",
            AsyncMock(return_value=plex_payload),
        ),
    ):
        result = await search_library_smart("daft", mode="plex", include_mixxx=False)
    assert result["total"] == 1
    assert result["engine"] == "plex_keyword"
    assert result["results"][0]["source"] == "plex"
    assert (
        result["results"][0]["cover_url"]
        == "/api/library/artwork/plex?path=library/metadata/1/thumb/abc&width=128&height=128"
    )


def test_map_plex_item_movie_poster():
    from mixx_dj_mcp.plex_client import map_plex_item

    mapped = map_plex_item(
        {
            "rating_key": "999",
            "title": "Blade Runner",
            "type": "movie",
            "thumb": "/library/metadata/2/thumb/1",
            "art": "/library/metadata/2/art/1",
        }
    )
    assert mapped["poster_url"] == "/api/library/artwork/plex?path=library/metadata/2/art/1&width=200&height=300"
    assert mapped["artwork_url"] == mapped["poster_url"]


@pytest.mark.asyncio
async def test_search_library_smart_falls_back_to_mixxx(sample_db: Path):
    with (
        patch("mixx_dj_mcp.library_search.plex_client.plex_available", AsyncMock(return_value=False)),
        patch(
            "mixx_dj_mcp.library_search.search_mixxx_db",
            lambda q, limit=50: search_library(q, limit=limit, db_path=sample_db),
        ),
    ):
        result = await search_library_smart("daft", mode="auto")
    assert result["total"] == 1
    assert result["engine"] == "mixxx"


@pytest.mark.asyncio
async def test_mixx_library_search_returns_rows(sample_db: Path, monkeypatch):
    from mixx_dj_mcp.tools import library as library_tool

    async def fake_smart(query, **kwargs):
        payload = search_library(query, db_path=sample_db)
        return {
            "results": payload["results"],
            "total": payload["total"],
            "message": payload["message"],
            "engine": "mixxx",
            "plex_available": False,
            "database": payload.get("database"),
        }

    monkeypatch.setattr(library_tool, "search_library_smart", fake_smart)
    result = await library_tool.mixx_library(operation="search", query="daft")
    assert result["success"] is True
    assert result["data"]["total"] == 1


def test_library_search_api(monkeypatch):
    from mixx_dj_mcp import server

    async def fake_smart(*args, **kwargs):
        return {
            "results": [
                {
                    "id": "plex:1",
                    "title": "T",
                    "artist": "A",
                    "bpm": 0,
                    "key": "?",
                    "length": "0:00",
                    "source": "plex",
                }
            ],
            "total": 1,
            "message": "ok",
            "engine": "plex_keyword",
            "plex_available": True,
        }

    monkeypatch.setattr(server, "search_library_smart", fake_smart)
    bridge = server.get_osc_bridge()
    bridge.send = lambda *args, **kwargs: None  # type: ignore[method-assign]

    client = TestClient(server.fastapi_app)
    response = client.post(
        "/api/library/search",
        json={"query": "house", "mode": "plex", "genre": "Electronic"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["engine"] == "plex_keyword"


def test_effects_api(monkeypatch):
    from mixx_dj_mcp import server

    async def fake_dispatch(_dispatch, name, arguments=None):
        assert name == "mixx_effects"
        return {"success": True, "message": "ok", "data": arguments}

    monkeypatch.setattr(server, "dispatch_tool", fake_dispatch)
    client = TestClient(server.fastapi_app)
    response = client.post(
        "/api/v1/effects",
        json={"operation": "chain_load", "rack": 1, "unit": 1, "effect": "Reverb"},
    )
    assert response.status_code == 200


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
