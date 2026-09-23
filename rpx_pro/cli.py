"""CLI-Interface: JSON-RPC-aehnliches Protokoll fuer LLM-Steuerung via stdin/stdout."""

import argparse
import json
import logging
import sys
import threading
from typing import Any, Callable, Optional

from PySide6.QtCore import QObject, Signal

from rpx_pro.api import RPXProAPI
from rpx_pro.managers.data_manager import DataManager
from rpx_pro.managers.audio_manager import AudioManager
from rpx_pro.managers.dice_roller import DiceRoller

logger = logging.getLogger("RPX")


class CLIWorker(QObject):
    """Liest JSON-Zeilen von stdin in eigenem Thread."""

    request_received = Signal(dict)

    def __init__(self, callback: Optional[Callable[[dict], None]] = None):
        super().__init__()
        self._running = False
        self._thread = None
        self._callback = callback

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
                    if self._callback:
                        self._callback(request)
                    else:
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
        self.worker = CLIWorker(callback=self._handle_request)
        self.worker.request_received.connect(self._handle_request)

    def start(self):
        """Startet das CLI-Interface."""
        self.worker.start()
        logger.info("CLI-Interface gestartet")

    def stop(self):
        self.worker.stop()

    def execute_command(self, request: dict) -> dict:
        """Fuehrt ein JSON-RPC-Kommando synchron aus und gibt das Antwort-Dict zurueck."""
        request_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        try:
            result = self._dispatch(method, params)
            return {"id": request_id, "result": result}
        except Exception as e:
            return {"id": request_id, "error": str(e)}

    def _handle_request(self, request: dict):
        """Verarbeitet eine eingehende JSON-RPC-Anfrage und schreibt auf stdout."""
        response = self.execute_command(request)
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def _dispatch(self, method: str, params: dict) -> Any:
        """Routet eine Methode an die API."""
        method_map = {
            # Welt
            "create_world": self.api.create_world,
            "list_worlds": lambda **_: self.api.list_worlds(),
            "load_world": self.api.load_world,
            "get_world": self.api.get_world,
            # Orte & Umgebung
            "create_location": self.api.create_location,
            "list_locations": lambda **_: self.api.list_locations(),
            "set_location": self.api.set_location,
            "set_environment": self.api.set_environment,
            # Session & Status
            "create_session": self.api.create_session,
            "list_sessions": lambda **_: self.api.list_sessions(),
            "load_session": self.api.load_session,
            "get_session_state": lambda **_: self.api.get_session_state(),
            # Charaktere & Inventar
            "create_character": self.api.create_character,
            "get_character": self.api.get_character,
            "heal_character": self.api.heal_character,
            "damage_character": self.api.damage_character,
            "get_inventory": self.api.get_inventory,
            "give_item": self.api.give_item,
            # Kampf & Runden
            "get_combat_state": lambda **_: self.api.get_combat_state(),
            "start_combat": self.api.start_combat,
            "next_turn": lambda **_: self.api.next_turn(),
            "end_combat": lambda **_: self.api.end_combat(),
            "execute_attack": self.api.execute_attack,
            # Soundboard & Audio
            "list_sounds": lambda **_: self.api.list_sounds(),
            "play_sound": self.api.play_sound,
            "list_music": lambda **_: self.api.list_music(),
            "play_music": self.api.play_music,
            "stop_music": lambda **_: self.api.stop_music(),
            "set_volume": self.api.set_volume,
            # Chat
            "send_chat_message": self.api.send_chat_message,
            "get_chat_history": self.api.get_chat_history,
            # Wuerfel
            "roll_dice": self.api.roll_dice,
            # Missionen
            "create_mission": self.api.create_mission,
            "complete_mission": self.api.complete_mission,
            # Prompts
            "generate_start_prompt": lambda **_: self.api.generate_start_prompt(),
            "generate_context_update": lambda **_: self.api.generate_context_update(),
            # Bundles
            "export_campaign_bundle": self.api.export_campaign_bundle,
            "import_campaign_bundle": self.api.import_campaign_bundle,
        }

        if method not in method_map:
            raise ValueError(f"Unknown method: {method}")

        func = method_map[method]
        return func(**params)


def main():
    """CLI-Haupteinstiegspunkt fuer Kommandozeilen- oder Headless-LLM-Steuerung."""
    parser = argparse.ArgumentParser(description="RPX Pro CLI/LLM-Schnittstelle")
    parser.add_argument(
        "--command",
        type=str,
        help="Fuehrt ein einzelnes JSON-RPC-Kommando aus und gibt das Ergebnis aus.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Liest JSON-RPC-Zeilen interaktiv von stdin.",
    )
    args = parser.parse_args()

    # Initialisiere Headless-API
    dm = DataManager()
    audio = AudioManager()
    dice = DiceRoller()
    api = RPXProAPI(data_manager=dm, audio_manager=audio, dice_roller=dice)
    cli = CLIInterface(api)

    if args.command:
        try:
            raw = args.command.strip()
            try:
                req = json.loads(raw)
            except json.JSONDecodeError:
                import ast
                req = ast.literal_eval(raw)
            resp = cli.execute_command(req)
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"error": str(e)}, ensure_ascii=False) + "\n")
            sys.stdout.flush()
            sys.exit(1)
        return

    if args.interactive:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = cli.execute_command(req)
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(json.dumps({"error": str(e)}, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
