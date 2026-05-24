from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    image_name TEXT NOT NULL,
    image_sha256 TEXT NOT NULL,
    common_name TEXT NOT NULL,
    scientific_name TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence REAL NOT NULL,
    status TEXT NOT NULL,
    model_used TEXT NOT NULL,
    result_json TEXT NOT NULL
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: Path) -> None:
    connection = connect(db_path)
    try:
        connection.execute(SCHEMA)
        connection.commit()
    finally:
        connection.close()


def save_search(db_path: Path, image_bytes: bytes, image_name: str, result: dict[str, Any]) -> int:
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    created_at = datetime.now(timezone.utc).isoformat()
    connection = connect(db_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO searches (
                created_at,
                image_name,
                image_sha256,
                common_name,
                scientific_name,
                category,
                confidence,
                status,
                model_used,
                result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                image_name,
                image_hash,
                result["common_name"],
                result["scientific_name"],
                result["category"],
                float(result["confidence"]),
                result["status"],
                result["model_used"],
                json.dumps(result, ensure_ascii=True),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def fetch_recent_searches(db_path: Path, limit: int = 25) -> list[dict[str, Any]]:
    connection = connect(db_path)
    try:
        rows = connection.execute(
            """
            SELECT *
            FROM searches
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    finally:
        connection.close()
    return [_row_to_dict(row) for row in rows]


def clear_history(db_path: Path) -> None:
    connection = connect(db_path)
    try:
        connection.execute("DELETE FROM searches")
        connection.commit()
    finally:
        connection.close()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["result"] = json.loads(data.pop("result_json"))
    return data
