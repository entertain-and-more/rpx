"""Koaleszierende, serielle Hintergrundpersistenz fuer RPX.

Die GUI erstellt einen unveraenderlichen Snapshot und uebergibt nur diesen an
den Worker. Dadurch greift der Worker nie auf lebende Qt- oder Model-Objekte zu.
"""

from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Condition, RLock
from typing import Any, Callable, Dict, Tuple


logger = logging.getLogger("RPX")


class AsyncPersistenceQueue:
    """Schreibt jeweils eine aktuelle Version pro Ressource im Hintergrund."""

    def __init__(self, writer: Callable[[str, str, Dict[str, Any]], None]):
        self._writer = writer
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="rpx-persistence",
        )
        self._condition = Condition(RLock())
        self._pending: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._future: Future[None] | None = None
        self._closed = False

    def submit(self, kind: str, object_id: str, payload: Dict[str, Any]) -> bool:
        """Nimmt einen Snapshot an, ohne auf dessen Schreiben zu warten."""
        key = (kind, object_id)
        with self._condition:
            if self._closed:
                return False
            self._pending[key] = payload
            self._start_next_locked()
            return True

    def _start_next_locked(self) -> None:
        if self._closed or self._future is not None or not self._pending:
            return
        batch = self._pending
        self._pending = {}
        self._future = self._executor.submit(self._write_batch, batch)
        self._future.add_done_callback(self._complete)

    def _write_batch(self, batch: Dict[Tuple[str, str], Dict[str, Any]]) -> None:
        for (kind, object_id), payload in batch.items():
            self._writer(kind, object_id, payload)

    def _complete(self, future: Future[None]) -> None:
        try:
            future.result()
        except Exception:
            logger.exception("Hintergrundpersistenz fehlgeschlagen")
        with self._condition:
            if self._future is future:
                self._future = None
            self._condition.notify_all()
            self._start_next_locked()

    def flush(self) -> None:
        """Wartet auf alle bisher angenommenen Snapshots."""
        with self._condition:
            while self._future is not None or self._pending:
                if self._future is None:
                    self._start_next_locked()
                self._condition.wait()

    def close(self) -> None:
        """Leert die Queue und beendet den Worker."""
        with self._condition:
            if self._closed:
                return
            while self._future is not None or self._pending:
                if self._future is None:
                    self._start_next_locked()
                self._condition.wait()
            self._closed = True
        self._executor.shutdown(wait=True)
