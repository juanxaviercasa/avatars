"""Almacén de documentos JSON sobre SQLite (thread-safe, sin dependencias)."""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from typing import Any, Iterable, Type, TypeVar

from pydantic import BaseModel

from .config import settings

T = TypeVar("T", bound=BaseModel)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS docs (
    collection TEXT NOT NULL,
    id TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    PRIMARY KEY (collection, id)
);
CREATE INDEX IF NOT EXISTS idx_docs_coll_created ON docs(collection, created_at);
"""


class Store:
    def __init__(self, path: str | None = None):
        self._path = str(path or settings.db_path)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # -- genérico -----------------------------------------------------------
    def put(self, collection: str, obj: BaseModel) -> None:
        data = obj.model_dump_json()
        now = time.time()
        created = getattr(obj, "created_at", now)
        with self._lock:
            self._conn.execute(
                "INSERT INTO docs(collection,id,data,created_at,updated_at) VALUES(?,?,?,?,?) "
                "ON CONFLICT(collection,id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
                (collection, obj.id, data, created, now),  # type: ignore[attr-defined]
            )
            self._conn.commit()

    def get(self, collection: str, id_: str, model: Type[T]) -> T | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT data FROM docs WHERE collection=? AND id=?", (collection, id_)
            ).fetchone()
        return model.model_validate_json(row[0]) if row else None

    def list(self, collection: str, model: Type[T], limit: int = 1000) -> list[T]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT data FROM docs WHERE collection=? ORDER BY created_at DESC LIMIT ?",
                (collection, limit),
            ).fetchall()
        out: list[T] = []
        for (data,) in rows:
            try:
                out.append(model.model_validate_json(data))
            except Exception:  # documento antiguo/incompatible: se ignora
                continue
        return out

    def delete(self, collection: str, id_: str) -> bool:
        with self._lock:
            cur = self._conn.execute("DELETE FROM docs WHERE collection=? AND id=?", (collection, id_))
            self._conn.commit()
            return cur.rowcount > 0

    def raw_put(self, collection: str, id_: str, data: dict[str, Any]) -> None:
        now = time.time()
        with self._lock:
            self._conn.execute(
                "INSERT INTO docs(collection,id,data,created_at,updated_at) VALUES(?,?,?,?,?) "
                "ON CONFLICT(collection,id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
                (collection, id_, json.dumps(data), now, now),
            )
            self._conn.commit()

    def raw_list(self, collection: str) -> Iterable[dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT data FROM docs WHERE collection=? ORDER BY created_at DESC", (collection,)
            ).fetchall()
        return [json.loads(r[0]) for r in rows]


_store: Store | None = None
_store_lock = threading.Lock()


def store() -> Store:
    global _store
    with _store_lock:
        if _store is None:
            _store = Store()
        return _store
