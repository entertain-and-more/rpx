"""CLI-Interface: JSON-RPC-aehnliches Protokoll fuer LLM-Steuerung via stdin/stdout."""

import sys
import json
import logging
import threading
from typing import Any

from PySide6.QtCore import QObject, Signal

from rpx_pro.api import RPXProAPI

logger = logging.getLogger("RPX")


class CLIWorker(QObject):
    """Liest JSON-Zeilen von stdin in eigenem Thread."""

    request_received = Signal(dict)

    def __init__(self):
        super().__init__()
        self._running = False
        self._thread = None

    def start(self):
        """Startet den stdin-Leser in einem eigenen Thread."""
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _read_loop(self):
        """Liest zeilenweise JSON von stdin."""
        while self._running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    request = json.loads(line)
                    self.request_received.emit(request)
                except json.JSONDecodeError as e:
                    self._send_error(None, f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"CLI stdin error: {e}")
                break

    @staticmethod
    def _send_error(request_id: Any, message: str):
        response = {"id": request_id, "error": message}
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


class CLIInterface:
    """Verbindet CLIWorker mit RPXProAPI."""

    def __init__(self, api: RPXProAPI):
        self.api = api
        self.worker = CLIWorker()
        self.worker.request_received.connect(self._handle_request)

    def start(self):
        """Startet das CLI-Interface."""
        self.worker.start()
        logger.info("CLI-Interface gestartet")

    def stop(self):
        self.worker.stop()

    def _handle_request(self, request: dict):
        """Verarbeitet eine eingehende JSON-RPC-Anfrage."""
        request_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        try:
            result = self._dispatch(method, params)
            response = {"id": request_id, "result": result}
        except Exception as e:
            response = {"id": request_id, "error": str(e)}

        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def _dispatch(self, method: str, params: dict) -> Any:
        """Routet eine Methode an die API."""
        method_map = {
            "create_world": self.api.create_world,
            "list_worlds": lambda **_: self.api.list_worlds(),
            "load_world": self.api.load_world,
            "create_session": self.api.create_session,
            "list_sessions": lambda **_: self.api.list_sessions(),
            "load_session": self.api.load_session,
            "create_character": self.api.create_character,
            "get_character": self.api.get_character,
            "heal_character": self.api.heal_character,
            "damage_character": self.api.damage_character,
            "get_inventory": self.api.get_inventory,
            "give_item": self.api.give_item,
            "send_chat_message": self.api.send_chat_message,
            "get_chat_history": self.api.get_chat_history,
            "roll_dice": self.api.roll_dice,
            "create_mission": self.api.create_mission,
            "complete_mission": self.api.complete_mission,
            "generate_start_prompt": lambda **_: self.api.generate_start_prompt(),
            "generate_context_update": lambda **_: self.api.generate_context_update(),
        }

        if method not in method_map:
            raise ValueError(f"Unknown method: {method}")

        func = method_map[method]
        return func(**params)
