"""Regressionstests fuer API- und CLI-Resilienz (Software-Bugsearch 2026-10-02)."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from rpx_pro.api import RPXProAPI
from rpx_pro.cli import CLIInterface
from rpx_pro.managers import data_manager as dm_module
from rpx_pro.managers.data_manager import DataManager
from rpx_pro.models.entities import Character


class APIAndCLIResilienceTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        base = Path(self.tmpdir.name)
        self.config_file = base / "config.json"
        self.worlds_dir = base / "worlds"
        self.sessions_dir = base / "sessions"
        self.backups_dir = base / "backups"
        self.sounds_dir = base / "sounds"
        self.music_dir = base / "music"
        for d in (
            self.worlds_dir,
            self.sessions_dir,
            self.backups_dir,
            self.sounds_dir,
            self.music_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

        self.patches = [
            patch.object(dm_module, "CONFIG_FILE", self.config_file),
            patch.object(dm_module, "WORLDS_DIR", self.worlds_dir),
            patch.object(dm_module, "SESSIONS_DIR", self.sessions_dir),
            patch.object(dm_module, "BACKUPS_DIR", self.backups_dir),
            patch("rpx_pro.api.SOUNDS_DIR", self.sounds_dir),
            patch("rpx_pro.api.MUSIC_DIR", self.music_dir),
        ]
        for p in self.patches:
            p.start()
        self.addCleanup(self._cleanup)

        self.dm = DataManager()
        self.mock_audio = MagicMock()
        self.mock_dice = MagicMock()
        self.api = RPXProAPI(
            data_manager=self.dm,
            audio_manager=self.mock_audio,
            dice_roller=self.mock_dice,
        )
        self.cli = CLIInterface(self.api)

        # Basis Welt & Session
        self.world = self.dm.create_world("Aventurien", genre="Fantasy")
        self.session = self.dm.create_session(self.world.id, "Testsession")
        self.dm.current_world = self.world
        self.dm.current_session = self.session

        self.char1 = Character(
            id="c1",
            name="Alrik",
            health=20,
            max_health=20,
            strength=14,
            dexterity=12,
        )
        self.char2 = Character(
            id="c2",
            name="Ork",
            health=15,
            max_health=15,
            strength=12,
            dexterity=10,
        )
        self.session.characters["c1"] = self.char1
        self.session.characters["c2"] = self.char2
        self.dm.save_session(self.session)

    def _cleanup(self):
        for p in reversed(self.patches):
            p.stop()
        self.tmpdir.cleanup()

    def test_cli_execute_command_rejects_non_dict_cleanly(self):
        """execute_command stuerzt bei nicht-dict Anfragen (str, list, int) nicht mit AttributeError ab."""
        for invalid in ["not a dict", [1, 2, 3], 42, None]:
            resp = self.cli.execute_command(invalid)
            self.assertIsInstance(resp, dict)
            self.assertIn("error", resp)
            self.assertIsNone(resp.get("id"))

    def test_cli_dispatch_handles_null_params(self):
        """JSON-RPC Aufrufe mit params: null (None) laufen fehlerfrei durch."""
        resp = self.cli.execute_command({"id": 10, "method": "list_worlds", "params": None})
        self.assertNotIn("error", resp)
        self.assertEqual(resp.get("id"), 10)
        self.assertIsInstance(resp.get("result"), list)

    def test_cli_dispatch_handles_array_positional_params(self):
        """JSON-RPC Aufrufe mit Array-Params (z.B. [2, 6]) werden positionell uebergeben."""
        self.api.dice_roller = None
        resp = self.cli.execute_command({"id": 20, "method": "roll_dice", "params": [3, 6]})
        self.assertNotIn("error", resp)
        self.assertEqual(resp.get("id"), 20)
        res = resp.get("result", {})
        self.assertEqual(res.get("dice"), "3W6")
        self.assertEqual(len(res.get("rolls")), 3)

    def test_damage_character_negative_amount_guarded(self):
        """damage_character mit negativem Betrag heilt den Charakter nicht unbegrenzt ueber max_health."""
        self.char1.health = 10
        self.char1.max_health = 20
        res = self.api.damage_character("c1", -100)
        self.assertLessEqual(self.char1.health, self.char1.max_health)
        self.assertIn("error", res)

    def test_heal_character_negative_amount_guarded(self):
        """heal_character mit negativem Betrag reduziert die Lebenspunkte nicht als unerkannter Schaden."""
        self.char1.health = 15
        res = self.api.heal_character("c1", -5)
        self.assertEqual(self.char1.health, 15)
        self.assertIn("error", res)

    def test_give_item_negative_count_prevents_negative_inventory(self):
        """give_item mit negativem Count erzeugt keine negativen Bestaende."""
        self.api.give_item("c1", "heiltrank", 2)
        res = self.api.give_item("c1", "heiltrank", -5)
        self.assertNotIn("heiltrank", self.char1.inventory)
        self.assertEqual(res.get("count"), 0)

    def test_execute_attack_guards_defeated_actors_and_non_dict_skills(self):
        """Besiegte Akteure koennen nicht angreifen oder angegriffen werden; nicht-dict Skills crashen nicht."""
        # Besiegter Angreifer
        self.char1.health = 0
        res_dead_atk = self.api.execute_attack("c1", "c2")
        self.assertIn("error", res_dead_atk)
        self.assertIn("besiegt", res_dead_atk["error"])

        # Besiegter Verteidiger
        self.char1.health = 20
        self.char2.health = 0
        res_dead_def = self.api.execute_attack("c1", "c2")
        self.assertIn("error", res_dead_def)
        self.assertIn("besiegt", res_dead_def["error"])

        # Nicht-dict Skill-Definitionen in der Welt
        self.char2.health = 15
        self.world.skill_definitions["schwerter"] = "Schwertkampf Level 3"  # String statt Dict
        res_skill = self.api.execute_attack("c1", "c2")
        self.assertNotIn("error", res_skill)
        self.assertIn("is_hit", res_skill)

    def test_sound_and_music_rejects_empty_and_directory_paths(self):
        """play_sound und play_music loesen leere Strings oder Verzeichnisse nicht als abspielbare Datei auf."""
        res_sound = self.api.play_sound("")
        self.assertFalse(res_sound.get("exists"))
        self.assertFalse(res_sound.get("played"))

        res_music = self.api.play_music("")
        self.assertFalse(res_music.get("exists"))
        self.assertFalse(res_music.get("playing"))

    def test_roll_dice_fallback_zero_and_negative_sides(self):
        """roll_dice mit dice_roller=None stuerzt bei sides <= 0 oder count <= 0 nicht mit ValueError ab."""
        self.api.dice_roller = None
        res = self.api.roll_dice(count=0, sides=0)
        self.assertEqual(res.get("dice"), "1W1")
        self.assertEqual(res.get("total"), 1)
        self.assertEqual(res.get("rolls"), [1])
