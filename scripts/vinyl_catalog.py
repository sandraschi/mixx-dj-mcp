#!/usr/bin/env python3
"""Vinyl catalog script -- OCR + AI categorization.

Scans a directory for *_sleeve.jpg and *_label.jpg pairs, OCRs them with
Tesseract, sends text to Ollama for structured extraction, and stores in
SQLite. Moves processed files to a processed/ subdirectory.
"""

import asyncio
import json
import os
import sqlite3
import sys
from pathlib import Path

import httpx
import pytesseract
from PIL import Image

DB_PATH = os.environ.get("VINYL_DB", str(Path.home() / "Vinyl" / "vinyl.db"))
PROCESSED_DIR = os.environ.get("VINYL_PROCESSED", "")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vinyl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sequential INTEGER UNIQUE,
            artist TEXT,
            album_title TEXT,
            catalog_number TEXT,
            year INTEGER,
            side TEXT,
            speed INTEGER,
            genre TEXT,
            era TEXT,
            mood TEXT,
            energy INTEGER,
            raw_ocr_sleeve TEXT,
            raw_ocr_label TEXT,
            sleeve_path TEXT,
            label_path TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vinyl_embeddings (
            vinyl_id INTEGER PRIMARY KEY,
            embedding BLOB,
            FOREIGN KEY (vinyl_id) REFERENCES vinyl(id)
        )
    """)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.commit()
    return conn


def ocr_image(path: str) -> str:
    """Run Tesseract OCR on an image."""
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"[OCR error: {e}]"


async def categorize_with_ollama(
    sleeve_text: str,
    label_text: str,
    ollama_base: str = "http://localhost:11434",
) -> dict:
    """Send OCR text to Ollama for structured extraction."""
    genres = (
        "techno, house, tech_house, deep_house, minimal, trance, "
        "drum_and_bass, dubstep, rock, pop, jazz, classical, "
        "electronic, ambient, experimental, or other"
    )
    prompt = f"""From these OCR texts of a vinyl record, extract structured data.
Return ONLY valid JSON with these fields:
- artist (string)
- album_title (string)
- catalog_number (string, or null)
- year (integer, estimate if not found, or null)
- side (string: "A", "B", or null)
- speed (integer: 33, 45, 78, or null)
- genre (string: {genres})
- era (string: "1950s" through "2020s")
- mood (string: energetic, dark, uplifting, chill, aggressive, euphoric, deep, groovy, weird)
- energy (integer 1-10)

Sleeve OCR: {sleeve_text[:2000]}
Label OCR: {label_text[:1000]}
"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{ollama_base}/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False,
                },
            )
            if r.status_code == 200:
                text = r.json().get("response", "")
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])
    except Exception as e:
        return {"artist": "Unknown", "album_title": "Unknown", "year": None, "error": str(e)}
    return {"artist": "Unknown", "album_title": "Unknown", "year": None}


def process_directory(inbox_dir: str) -> dict:
    """Process all unprocessed vinyl photo pairs in a directory.

    Args:
        inbox_dir: Directory containing *_sleeve.jpg and *_label.jpg files.

    Returns:
        Dict with summary of what was processed.
    """
    inbox = Path(inbox_dir)
    if not inbox.is_dir():
        return {
            "success": False,
            "error": f"Directory not found: {inbox_dir}",
            "processed": 0,
            "total": 0,
        }

    processed = Path(PROCESSED_DIR or str(inbox / ".." / "processed"))
    processed.mkdir(parents=True, exist_ok=True)

    conn = init_db()
    cursor = conn.cursor()

    sleeves = sorted(inbox.glob("*_sleeve.jpg"))
    total = len(sleeves)
    results = []

    if total == 0:
        conn.close()
        return {
            "success": True,
            "message": "No vinyl photos found.",
            "processed": 0,
            "total": 0,
            "records": [],
        }

    for _i, sleeve_path in enumerate(sleeves, 1):
        seq = sleeve_path.stem.replace("_sleeve", "")
        label_path = inbox / f"{seq}_label.jpg"
        label_b_path = inbox / f"{seq}_label_b.jpg"

        cursor.execute("SELECT id FROM vinyl WHERE sequential = ?", (int(seq),))
        if cursor.fetchone():
            results.append(
                {
                    "sequential": int(seq),
                    "status": "skipped",
                    "reason": "already cataloged",
                }
            )
            continue

        sleeve_text = ocr_image(str(sleeve_path))
        label_text = ocr_image(str(label_path)) if label_path.exists() else ""

        result = asyncio.run(categorize_with_ollama(sleeve_text, label_text))

        cursor.execute(
            """
            INSERT INTO vinyl (sequential, artist, album_title, catalog_number,
                year, side, speed, genre, era, mood, energy,
                raw_ocr_sleeve, raw_ocr_label, sleeve_path, label_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                int(seq),
                result.get("artist", "Unknown"),
                result.get("album_title", "Unknown"),
                result.get("catalog_number"),
                result.get("year"),
                result.get("side"),
                result.get("speed"),
                result.get("genre", "Unknown"),
                result.get("era"),
                result.get("mood"),
                result.get("energy"),
                sleeve_text[:5000],
                label_text[:5000],
                str(sleeve_path),
                str(label_path) if label_path.exists() else None,
            ),
        )
        conn.commit()

        sleeve_path.rename(processed / sleeve_path.name)
        if label_path.exists():
            label_path.rename(processed / label_path.name)
        if label_b_path.exists():
            label_b_path.rename(processed / label_b_path.name)

        results.append(
            {
                "sequential": int(seq),
                "status": "cataloged",
                "artist": result.get("artist", "Unknown"),
                "album_title": result.get("album_title", "Unknown"),
                "genre": result.get("genre", "Unknown"),
            }
        )

    conn.close()
    return {
        "success": True,
        "message": f"Processed {len(results)} records.",
        "processed": len(results),
        "total": total,
        "records": results,
    }


if __name__ == "__main__":
    inbox = sys.argv[1] if len(sys.argv) > 1 else input("Inbox directory: ")
    result = process_directory(inbox)
    print(json.dumps(result, indent=2))
