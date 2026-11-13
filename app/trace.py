from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from typing import Any

from app.config import settings


DB_PATH = Path(settings.data_dir) / "voice_traces.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            transcript TEXT NOT NULL,
            reply TEXT NOT NULL,
            metadata TEXT DEFAULT '{}'
        )
        """
    )
    conn.commit()
    return conn


def record_trace(source: str, status: str, transcript: str, reply: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = metadata or {}
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    cursor = conn.execute(
        """
        INSERT INTO traces (created_at, source, status, transcript, reply, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (now, source, status, transcript, reply, json.dumps(metadata)),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return {
        "id": row_id,
        "created_at": now,
        "source": source,
        "status": status,
        "transcript": transcript,
        "reply": reply,
        "metadata": metadata,
    }


def list_recent_traces(limit: int = 20) -> list[dict[str, Any]]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM traces ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
