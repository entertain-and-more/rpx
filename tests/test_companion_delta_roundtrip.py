"""Hermetic tests for rpx-companion-delta-v1 roundtrip (Web/PWA Companion <-> Desktop API/CLI) and sdist packaging."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rpx_pro.api import RPXProAPI
from rpx_pro.cli import CLIInterface
from rpx_pro.managers import data_manager as dm_module
from rpx_pro.managers.data_manager import MAX_COMPANION_DELTA_BYTES, DataManager
from rpx_pro.models.entities import Character
from rpx_pro.models.world import Location

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CompanionDeltaRoundtripTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory(prefix="rpx-delta-test-")
        base = Path(self.tmpdir.name).resolve()
        self.data_root = base / "rpx_pro_data"
        self.media_dir = self.data_root / "media"
        self.worlds_dir = self.data_root / "worlds"
        self.sessions_dir = self.data_root / "sessions"
        self.backups_dir = self.data_root / "backups"
        self.rulesets_dir = base / "rulesets"
        self.exports_dir = base / "exports"
        self.config_file = self.data_root / "config.json"

        for directory in (
            self.worlds_dir,
            self.sessions_dir,
            self.backups_dir,
            self.media_dir / "images",
            self.media_dir / "sounds",
            self.media_dir / "music",
            self.media_dir / "maps",
            self.rulesets_dir,
            self.exports_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        (self.rulesets_dir / "basic.json").write_text(
            json.dumps({"ruleset_name": "Basisregeln", "weapons": [{"name": "Dolch"}], "spells": []}),
            encoding="utf-8",
        )

        self.patches = [
            patch.object(dm_module, "CONFIG_FILE", self.config_file),
            patch.object(dm_module, "PROJECT_ROOT", self.data_root),
            patch.object(dm_module, "MEDIA_DIR", self.media_dir),
            patch.object(dm_module, "WORLDS_DIR", self.worlds_dir),
            patch.object(dm_module, "SESSIONS_DIR", self.sessions_dir),
            patch.object(dm_module, "BACKUPS_DIR", self.backups_dir),
            patch.object(dm_module, "RULESETS_DIR", self.rulesets_dir),
        ]
        for p in self.patches:
            p.start()

        self.dm = DataManager()
        self.world = self.dm.create_world("Nordmark", "Fantasy")
        self.world.locations["loc1"] = Location(id="loc1", name="Taverne", description="Sicherer Hafen")
        self.dm.save_world(self.world)

        self.session = self.dm.create_session(self.world.id, "Abendrunde 1")
        assert self.session is not None
        self.hero = Character(
            id="ayla",
            name="Ayla",
            health=19,
            max_health=24,
            mana=7,
            max_mana=11,
            gold=42,
        )
        self.session.characters["ayla"] = self.hero
        self.dm.save_session(self.session)
        self.api = RPXProAPI(data_manager=self.dm)
        self.cli = CLIInterface(api=self.api)

    def tearDown(self):
        self.dm.close()
        for p in reversed(self.patches):
            p.stop()
        self.tmpdir.cleanup()

    def test_end_to_end_js_companion_to_python_cli_roundtrip(self):
        bundle_path = self.exports_dir / "campaign.zip"
        delta_path = self.exports_dir / "campaign-companion-delta.json"

        exported = self.api.export_campaign_bundle(str(bundle_path))
        self.assertEqual(exported["format"], "rpx-campaign-bundle-v1")
        self.assertTrue(bundle_path.exists())

        js_driver = self.exports_dir / "generate_delta.mjs"
        js_driver.write_text(
            f"""
import fs from "node:fs";
import {{
  loadBundleFromArrayBuffer,
  createEmptyCompanionDelta,
  recordCharacterPatch,
  addPlayerNote,
  buildCompanionDeltaPayload,
}} from {(PROJECT_ROOT / "web_companion" / "library.js").as_uri()!r};

const raw = fs.readFileSync({str(bundle_path)!r});
const bundle = await loadBundleFromArrayBuffer(raw, "campaign.zip");
let delta = createEmptyCompanionDelta(bundle);
delta = recordCharacterPatch(delta, bundle, {self.session.id!r}, "ayla", {{
  health: 14,
  mana: 99,
  gold: 60,
}}, 1779647000);
delta = addPlayerNote(delta, bundle, {{
  sessionId: {self.session.id!r},
  characterId: "ayla",
  content: "Geheimtuer im Weinkeller markiert.",
}}, 1779647010);
const payload = buildCompanionDeltaPayload(bundle, delta, 1779647020);
fs.writeFileSync({str(delta_path)!r}, JSON.stringify(payload, null, 2), "utf8");
""",
            encoding="utf-8",
        )

        proc = subprocess.run(
            ["node", str(js_driver)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(delta_path.exists())

        rpc_resp = self.cli.execute_command(
            {
                "id": 101,
                "method": "import_companion_delta",
                "params": {"source": str(delta_path)},
            }
        )
        self.assertNotIn("error", rpc_resp)
        result = rpc_resp["result"]
        self.assertEqual(result["format"], "rpx-companion-delta-v1")
        self.assertEqual(result["patch_count"], 1)
        self.assertEqual(result["note_count"], 1)

        updated_char = self.session.characters["ayla"]
        self.assertEqual(updated_char.health, 14)
        self.assertEqual(updated_char.mana, 11)  # clamped to max_mana=11
        self.assertEqual(updated_char.gold, 60)

        self.assertEqual(len(self.session.chat_history), 1)
        msg = self.session.chat_history[0]
        self.assertEqual(msg.author, "Ayla")
        self.assertEqual(msg.content, "[Companion] Geheimtuer im Weinkeller markiert.")
        self.assertEqual(msg.metadata.get("source"), "rpx-companion-delta-v1")

        # World and ruleset structures remain 100% untouched
        self.assertEqual(len(self.world.locations), 1)
        self.assertEqual(self.world.locations["loc1"].name, "Taverne")

        # Second import of the identical file is idempotent (no duplicate chat note)
        second = self.api.import_companion_delta(str(delta_path))
        self.assertEqual(second["note_count"], 0)
        self.assertEqual(len(second["skipped_notes"]), 1)
        self.assertEqual(second["skipped_notes"][0]["reason"], "duplicate_note_id")
        self.assertEqual(len(self.session.chat_history), 1)

    def test_unknown_sessions_and_characters_are_reported_non_destructively(self):
        res = self.api.import_companion_delta(
            {
                "format": "rpx-companion-delta-v1",
                "character_patches": [
                    {"session_id": "missing-session", "character_id": "ayla", "health": 10},
                    {"session_id": self.session.id, "character_id": "ghost", "health": 10},
                ],
                "player_notes": [
                    {"id": "n1", "session_id": "missing-session", "content": "Hallo"},
                    {"id": "n2", "session_id": self.session.id, "content": "   "},
                ],
            }
        )
        self.assertEqual(res["patch_count"], 0)
        self.assertEqual(res["note_count"], 0)
        self.assertEqual(len(res["skipped_patches"]), 2)
        self.assertEqual(len(res["skipped_notes"]), 2)
        self.assertEqual(self.session.characters["ayla"].health, 19)

    def test_invalid_format_path_traversal_boolean_and_oversized_files_rejected(self):
        with self.assertRaises(ValueError):
            self.api.import_companion_delta({"format": "wrong-format"})

        with self.assertRaises(ValueError):
            self.api.import_companion_delta(
                {
                    "format": "rpx-companion-delta-v1",
                    "character_patches": [
                        {"session_id": "../evil", "character_id": "ayla", "health": 10}
                    ],
                }
            )

        with self.assertRaises(ValueError):
            self.api.import_companion_delta(
                {
                    "format": "rpx-companion-delta-v1",
                    "character_patches": [
                        {"session_id": self.session.id, "character_id": "ayla", "health": True}
                    ],
                }
            )

        oversized = self.exports_dir / "huge.json"
        oversized.write_bytes(b"x" * (MAX_COMPANION_DELTA_BYTES + 10))
        with self.assertRaises(ValueError):
            self.api.import_companion_delta(str(oversized))

    def test_atomic_rollback_on_later_validation_error_and_zero_max_bound(self):
        # Character with max_mana == 0 must clamp mana to 0
        self.hero.max_mana = 0
        self.hero.mana = 0

        # Valid patch followed by invalid note character_id must NOT mutate self.hero in memory
        with self.assertRaises(ValueError):
            self.api.import_companion_delta(
                {
                    "format": "rpx-companion-delta-v1",
                    "character_patches": [
                        {"session_id": self.session.id, "character_id": "ayla", "health": 10, "gold": 99}
                    ],
                    "player_notes": [
                        {
                            "session_id": self.session.id,
                            "character_id": "../traversal",
                            "content": "Darf nicht halb angewendet werden",
                        }
                    ],
                }
            )
        self.assertEqual(self.session.characters["ayla"].health, 19)
        self.assertEqual(self.session.characters["ayla"].gold, 42)
        self.assertEqual(len(self.session.chat_history), 0)

        # Valid patch with mana=25 when max_mana==0 clamps mana to 0
        res = self.api.import_companion_delta(
            {
                "format": "rpx-companion-delta-v1",
                "character_patches": [
                    {"session_id": self.session.id, "character_id": "ayla", "mana": 25}
                ],
                "player_notes": [
                    {"session_id": self.session.id, "author": "Ayla", "content": "Ohne explizite ID"}
                ],
            }
        )
        self.assertEqual(res["patch_count"], 1)
        self.assertEqual(self.session.characters["ayla"].mana, 0)
        # Re-importing note without id or created_at is still idempotent
        res2 = self.api.import_companion_delta(
            {
                "format": "rpx-companion-delta-v1",
                "player_notes": [
                    {"session_id": self.session.id, "author": "Ayla", "content": "Ohne explizite ID"}
                ],
            }
        )
        self.assertEqual(res2["note_count"], 0)

    def test_manifest_in_includes_pwa_webmanifest_icons_and_skill_md(self):
        manifest_in = (PROJECT_ROOT / "MANIFEST.in").read_text(encoding="utf-8")
        self.assertIn("SKILL.md", manifest_in)
        self.assertIn("llm.txt", manifest_in)
        self.assertIn("EXPORTFORMAT.md", manifest_in)
        self.assertIn("conftest.py", manifest_in)
        self.assertIn("*.webmanifest", manifest_in)
        self.assertIn("*.svg", manifest_in)
        self.assertIn("*.png", manifest_in)
        self.assertTrue((PROJECT_ROOT / "SKILL.md").exists())
        self.assertTrue((PROJECT_ROOT / "llm.txt").exists())


if __name__ == "__main__":
    unittest.main()
