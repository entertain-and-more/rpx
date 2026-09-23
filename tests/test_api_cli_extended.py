"""Tests fuer die erweiterte RPXProAPI und das CLIInterface (TW-RPG-08)."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from rpx_pro.api import RPXProAPI
from rpx_pro.cli import CLIInterface
from rpx_pro.managers import data_manager as dm_module
from rpx_pro.managers.data_manager import DataManager
from rpx_pro.models.entities import Armor, Character, Weapon
from rpx_pro.models.enums import TimeOfDay, WeatherType


class APICLIExtendedTests(unittest.TestCase):
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

        # Basis-Setup
        self.dm = DataManager()
        self.mock_audio = MagicMock()
        self.mock_dice = MagicMock()
        self.mock_dice.roll.return_value = {"dice": "2W6", "rolls": [3, 4], "total": 7}
        self.api = RPXProAPI(
            data_manager=self.dm,
            audio_manager=self.mock_audio,
            dice_roller=self.mock_dice,
        )
        self.cli = CLIInterface(self.api)

        # Testwelt und Session anlegen
        self.world = self.dm.create_world("Drachenfels", genre="High Fantasy")
        self.session = self.dm.create_session(self.world.id, "Kampagnenstart")
        self.dm.current_world = self.world
        self.dm.current_session = self.session

        # Charaktere anlegen
        self.char1 = Character(
            id="hero-1",
            name="Valeros",
            strength=16,
            dexterity=14,
            health=30,
            max_health=30,
        )
        self.char2 = Character(
            id="goblin-1",
            name="Snark",
            strength=10,
            dexterity=12,
            health=12,
            max_health=12,
        )
        self.session.characters[self.char1.id] = self.char1
        self.session.characters[self.char2.id] = self.char2
        self.dm.save_session(self.session)

    def _cleanup(self):
        for p in reversed(self.patches):
            p.stop()
        self.tmpdir.cleanup()

    # --- Soundboard & Audio Tests ---

    def test_soundboard_list_and_playback(self):
        # Lege Test-Dateien an
        (self.sounds_dir / "tada.wav").write_text("dummy sound")
        (self.sounds_dir / "slash.mp3").write_text("dummy sound")
        (self.sounds_dir / "note.txt").write_text("ignore me")

        sounds = self.api.list_sounds()
        sound_names = [s["name"] for s in sounds]
        self.assertIn("tada.wav", sound_names)
        self.assertIn("slash.mp3", sound_names)
        self.assertNotIn("note.txt", sound_names)

        # Abspielen ueber Name
        res = self.api.play_sound("tada", volume=0.8)
        self.assertTrue(res["played"])
        self.mock_audio.play_sound.assert_called_once()

    def test_music_list_and_playback(self):
        (self.music_dir / "intro.mp3").write_text("dummy music")

        music_files = self.api.list_music()
        self.assertEqual(len(music_files), 1)
        self.assertEqual(music_files[0]["id"], "intro")

        res = self.api.play_music("intro", loop=True)
        self.assertTrue(res["playing"])
        self.mock_audio.play_music.assert_called_once()

        stop_res = self.api.stop_music()
        self.assertTrue(stop_res["stopped"])
        self.mock_audio.stop_music.assert_called_once()

        vol_res = self.api.set_volume(music=0.4, sound=0.6)
        self.assertTrue(vol_res["updated"])
        self.mock_audio.set_music_volume.assert_called_with(0.4)
        self.mock_audio.set_sound_volume.assert_called_with(0.6)

    # --- Welten, Orte & Umgebung Tests ---

    def test_world_details_and_location_lifecycle(self):
        world_info = self.api.get_world()
        self.assertEqual(world_info["name"], "Drachenfels")
        self.assertEqual(world_info["genre"], "High Fantasy")

        # Ort erstellen
        loc = self.api.create_location(
            name="Goldene Taverne",
            description="Gemütlicher Treffpunkt für Abenteurer",
            location_type="tavern",
        )
        self.assertIn("id", loc)
        self.assertEqual(loc["name"], "Goldene Taverne")

        # Orte auflisten
        locs = self.api.list_locations()
        self.assertEqual(len(locs), 1)
        self.assertEqual(locs[0]["name"], "Goldene Taverne")
        self.assertFalse(locs[0]["visited"])

        # Ort in Session setzen
        set_res = self.api.set_location(loc["id"])
        self.assertEqual(set_res["current_location_id"], loc["id"])
        self.assertEqual(self.session.current_location_id, loc["id"])
        self.assertTrue(self.world.locations[loc["id"]].visited)

    def test_environment_updates(self):
        res = self.api.set_environment(weather="rain", time_of_day="night")
        self.assertEqual(res["current_weather"], "rain")
        self.assertEqual(res["current_time_of_day"], "night")
        self.assertEqual(self.session.current_weather, WeatherType.RAIN)
        self.assertEqual(self.session.current_time_of_day, TimeOfDay.NIGHT)

        # Ungueltiger Wert
        err = self.api.set_environment(weather="tornado_of_fire")
        self.assertIn("error", err)

    def test_get_session_state(self):
        self.api.set_environment(weather="storm", time_of_day="evening")
        state = self.api.get_session_state()
        self.assertEqual(state["session_name"], "Kampagnenstart")
        self.assertEqual(state["world_name"], "Drachenfels")
        self.assertEqual(state["current_weather"], "storm")
        self.assertEqual(state["current_time_of_day"], "evening")
        self.assertEqual(len(state["characters"]), 2)

    # --- Kampf & Runden Tests ---

    def test_combat_turn_order_and_rounds(self):
        # Kampf starten
        state = self.api.start_combat(["hero-1", "goblin-1"])
        self.assertTrue(state["in_combat"])
        self.assertEqual(state["current_round"], 1)
        self.assertEqual(state["current_turn_index"], 0)
        self.assertEqual(state["current_actor"]["id"], "hero-1")

        # Nächster Zug
        state2 = self.api.next_turn()
        self.assertEqual(state2["current_turn_index"], 1)
        self.assertEqual(state2["current_round"], 1)
        self.assertFalse(state2["round_advanced"])
        self.assertEqual(state2["current_actor"]["id"], "goblin-1")

        # Rundenübergang (wrap around)
        state3 = self.api.next_turn()
        self.assertEqual(state3["current_turn_index"], 0)
        self.assertEqual(state3["current_round"], 2)
        self.assertTrue(state3["round_advanced"])
        self.assertEqual(state3["current_actor"]["id"], "hero-1")

        # Kampf beenden
        end_res = self.api.end_combat()
        self.assertFalse(end_res["in_combat"])
        self.assertFalse(self.session.is_round_based)

    def test_execute_attack_with_weapon_and_armor(self):
        # Waffe und Rüstung in Welt anlegen
        sword = Weapon(
            id="sword-1",
            name="Langschwert",
            damage_min=6,
            damage_max=10,
            accuracy=0.8,  # Hit threshold: max(1, 20 - 16) = 4
            critical_threshold=19,
            critical_multiplier=2.0,
        )
        armor = Armor(
            id="armor-1",
            name="Lederruestung",
            protection_avg=2,
        )
        self.world.weapons[sword.id] = sword
        self.world.armors[armor.id] = armor
        self.dm.save_world(self.world)

        self.char1.equipped_weapon = sword.id
        self.char2.equipped_armor = armor.id
        self.dm.save_session(self.session)

        # Angriff ausführen (mit seed für deterministische Prüfung)
        with patch("random.randint") as mock_rand:
            # mock_rand aufgerufen für:
            # 1. hit_roll: 19 (Crit!)
            # 2. base_dmg: 8 -> crit = 16
            mock_rand.side_effect = [19, 8]
            res = self.api.execute_attack("hero-1", "goblin-1")

        self.assertTrue(res["is_hit"])
        self.assertTrue(res["is_critical"])
        # Base (16) + Str bonus ((16-10)//2 = 3) - Armor (2) = 17 dmg
        self.assertEqual(res["damage"], 17)
        self.assertEqual(res["defender_health"], 0)
        self.assertTrue(res["defeated"])

        # Prüfe, dass Systemnachricht im Chat geloggt wurde
        chat = self.api.get_chat_history()
        self.assertTrue(any("Langschwert" in m["content"] for m in chat))

    def test_execute_attack_miss(self):
        with patch("random.randint", return_value=1):
            res = self.api.execute_attack("hero-1", "goblin-1")
            self.assertFalse(res["is_hit"])
            self.assertEqual(res["damage"], 0)

    # --- CLI Interface Dispatch Tests ---

    def test_cli_execute_command_dispatch(self):
        # 1. Roll Dice
        req = {"id": 1, "method": "roll_dice", "params": {"count": 2, "sides": 6}}
        resp = self.cli.execute_command(req)
        self.assertEqual(resp["id"], 1)
        self.assertIn("total", resp["result"])

        # 2. Set Environment
        req2 = {
            "id": 2,
            "method": "set_environment",
            "params": {"weather": "fog", "time_of_day": "morning"},
        }
        resp2 = self.cli.execute_command(req2)
        self.assertEqual(resp2["result"]["current_weather"], "fog")

        # 3. Create Location
        req3 = {
            "id": 3,
            "method": "create_location",
            "params": {"name": "Hafenviertel", "location_type": "district"},
        }
        resp3 = self.cli.execute_command(req3)
        self.assertEqual(resp3["result"]["name"], "Hafenviertel")

        # 4. Start Combat
        req4 = {
            "id": 4,
            "method": "start_combat",
            "params": {"character_ids": ["hero-1", "goblin-1"]},
        }
        resp4 = self.cli.execute_command(req4)
        self.assertTrue(resp4["result"]["in_combat"])

        # 5. Invalid Method Error
        req_err = {"id": 99, "method": "nonexistent_action", "params": {}}
        resp_err = self.cli.execute_command(req_err)
        self.assertIn("error", resp_err)


if __name__ == "__main__":
    unittest.main()
