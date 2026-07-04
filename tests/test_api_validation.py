import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rpx_pro.api import MAX_API_DICE_COUNT, RPXProAPI
from rpx_pro.managers import data_manager as dm_module
from rpx_pro.managers.data_manager import DataManager


class APIValidationTests(unittest.TestCase):
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

    def _api_with_session(self):
        dm = DataManager()
        world = dm.create_world("World", "Fantasy")
        session = dm.create_session(world.id, "Session")
        self.assertIsNotNone(session)
        dm.current_session = session
        return RPXProAPI(dm), session

    def test_create_character_ignores_unknown_kwargs(self):
        api, session = self._api_with_session()

        result = api.create_character(
            "Mira",
            profession="Magierin",
            health=80,
            unknown_cli_field="ignored",
        )

        self.assertNotIn("error", result)
        char = session.characters[result["id"]]
        self.assertEqual(char.name, "Mira")
        self.assertEqual(char.profession, "Magierin")
        self.assertEqual(char.health, 80)
        self.assertFalse(hasattr(char, "unknown_cli_field"))

    def test_roll_dice_accepts_numeric_strings(self):
        api, _ = self._api_with_session()

        result = api.roll_dice(count="2", sides="6")

        self.assertEqual(result["dice"], "2W6")
        self.assertEqual(len(result["rolls"]), 2)
        self.assertTrue(all(1 <= value <= 6 for value in result["rolls"]))
        self.assertEqual(result["total"], sum(result["rolls"]))

    def test_roll_dice_rejects_invalid_ranges(self):
        api, _ = self._api_with_session()

        self.assertIn("error", api.roll_dice(count=0, sides=6))
        self.assertIn("error", api.roll_dice(count=1, sides=0))
        self.assertIn("error", api.roll_dice(count=MAX_API_DICE_COUNT + 1, sides=6))

    def test_roll_dice_rejects_non_integer_values(self):
        api, _ = self._api_with_session()

        self.assertIn("error", api.roll_dice(count="many", sides=6))
        self.assertIn("error", api.roll_dice(count=1, sides="wide"))


if __name__ == "__main__":
    unittest.main()
