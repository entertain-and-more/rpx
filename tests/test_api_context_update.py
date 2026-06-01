import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rpx_pro.api import RPXProAPI
from rpx_pro.managers import data_manager as dm_module
from rpx_pro.managers.data_manager import DataManager
from rpx_pro.models.enums import MessageRole
from rpx_pro.models.session import ChatMessage, Session


class GenerateContextUpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        base = Path(self.tmpdir.name)
        self.config_file = base / "config.json"
        self.worlds_dir = base / "worlds"
        self.sessions_dir = base / "sessions"
        self.backups_dir = base / "backups"
        for directory in (self.worlds_dir, self.sessions_dir, self.backups_dir):
            directory.mkdir(parents=True, exist_ok=True)

        self.patches = [
            patch.object(dm_module, "CONFIG_FILE", self.config_file),
            patch.object(dm_module, "WORLDS_DIR", self.worlds_dir),
            patch.object(dm_module, "SESSIONS_DIR", self.sessions_dir),
            patch.object(dm_module, "BACKUPS_DIR", self.backups_dir),
        ]
        for patcher in self.patches:
            patcher.start()
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.tmpdir.cleanup()

    def test_generate_context_update_advances_clipboard_index(self):
        dm = DataManager()
        session = Session(
            id="session-1",
            world_id="world-1",
            name="Test Session",
        )
        session.chat_history.extend(
            [
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    author="System",
                    content="First entry",
                    timestamp=1700000000.0,
                ),
                ChatMessage(
                    role=MessageRole.PLAYER,
                    author="Alice",
                    content="Second entry",
                    timestamp=1700000060.0,
                ),
            ]
        )
        dm.sessions[session.id] = session
        dm.current_session = session

        api = RPXProAPI(dm)

        first_prompt = api.generate_context_update()
        self.assertIn("First entry", first_prompt)
        self.assertIn("Second entry", first_prompt)
        self.assertEqual(session.last_clipboard_index, 2)

        saved = json.loads((self.sessions_dir / "session-1.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["last_clipboard_index"], 2)

        session.chat_history.append(
            ChatMessage(
                role=MessageRole.GM,
                author="GM",
                content="Third entry",
                timestamp=1700000120.0,
            )
        )

        second_prompt = api.generate_context_update()
        self.assertNotIn("First entry", second_prompt)
        self.assertNotIn("Second entry", second_prompt)
        self.assertIn("Third entry", second_prompt)
        self.assertEqual(session.last_clipboard_index, 3)

        saved = json.loads((self.sessions_dir / "session-1.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["last_clipboard_index"], 3)

    def test_load_session_syncs_current_world_for_prompt_generation(self):
        dm = DataManager()
        world_a = dm.create_world("World A", "Fantasy")
        session = dm.create_session(world_a.id, "Test Session")
        self.assertIsNotNone(session)
        world_b = dm.create_world("World B", "Sci-Fi")
        dm.current_world = world_b

        api = RPXProAPI(dm)

        response = api.load_session(session.id)

        self.assertEqual(response["id"], session.id)
        self.assertIs(dm.current_session, session)
        self.assertIs(dm.current_world, world_a)

        prompt = api.generate_start_prompt()
        self.assertIn("World A", prompt)
        self.assertNotIn("World B", prompt)

    def test_send_chat_message_normalizes_invalid_roles(self):
        dm = DataManager()
        world = dm.create_world("World", "Fantasy")
        session = dm.create_session(world.id, "Chat Session")
        self.assertIsNotNone(session)
        dm.current_session = session

        api = RPXProAPI(dm)

        result = api.send_chat_message("wizard", "GM", "Hello there")

        self.assertEqual(result["role"], MessageRole.SYSTEM.value)
        self.assertEqual(session.chat_history[-1].role, MessageRole.SYSTEM)
        self.assertEqual(session.chat_history[-1].author, "GM")
        self.assertEqual(session.chat_history[-1].content, "Hello there")


if __name__ == "__main__":
    unittest.main()
