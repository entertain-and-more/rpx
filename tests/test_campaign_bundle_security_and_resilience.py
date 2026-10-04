"""Regressionstests fuer Kampagnen-Bundle Pfadsicherheit, Zip-Slip Schutz und Daten-Persistenz."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from rpx_pro.managers import data_manager as dm_module
from rpx_pro.managers.async_persistence import AsyncPersistenceQueue
from rpx_pro.managers.data_manager import DataManager


class CampaignBundleSecurityAndResilienceTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        base = Path(self.tmpdir.name)
        self.project_root = base / "rpx_pro_data"
        self.media_dir = self.project_root / "media"
        self.worlds_dir = self.project_root / "worlds"
        self.sessions_dir = self.project_root / "sessions"
        self.backups_dir = self.project_root / "backups"
        self.rulesets_dir = base / "rulesets"
        self.exports_dir = base / "exports"
        self.config_file = self.project_root / "config.json"

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

        self.patches = [
            patch.object(dm_module, "CONFIG_FILE", self.config_file),
            patch.object(dm_module, "PROJECT_ROOT", self.project_root),
            patch.object(dm_module, "MEDIA_DIR", self.media_dir),
            patch.object(dm_module, "WORLDS_DIR", self.worlds_dir),
            patch.object(dm_module, "SESSIONS_DIR", self.sessions_dir),
            patch.object(dm_module, "BACKUPS_DIR", self.backups_dir),
            patch.object(dm_module, "RULESETS_DIR", self.rulesets_dir),
        ]
        for patcher in self.patches:
            patcher.start()
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.tmpdir.cleanup()

    def _init_dm(self) -> DataManager:
        dm = DataManager.__new__(DataManager)
        dm.worlds = {}
        dm.sessions = {}
        dm.current_world = None
        dm.current_session = None
        dm.config = dict(DataManager.DEFAULT_CONFIG)
        dm._async_saves = AsyncPersistenceQueue(dm._write_snapshot)
        return dm

    def test_import_campaign_bundle_rejects_zip_slip_in_media_member(self):
        dm = self._init_dm()
        bundle_path = self.exports_dir / "malicious-zip-slip.zip"
        escape_file = self.tmpdir.name + "/escaped_target.txt"

        manifest = {
            "format": "rpx-campaign-bundle-v1",
            "media_mode": "files",
            "worlds": [
                {
                    "id": "w1",
                    "name": "Evil World",
                    "genre": "Fantasy",
                    "file": "worlds/w1.json",
                }
            ],
            "sessions": [],
            "rulesets": [],
            "media": [],
        }
        world_payload = {
            "id": "w1",
            "settings": {"name": "Evil World"},
            "map_image": "media/../../escaped_target.txt",
        }

        with ZipFile(bundle_path, "w") as archive:
            archive.writestr("manifest.json", json.dumps(manifest))
            archive.writestr("worlds/w1.json", json.dumps(world_payload))
            archive.writestr("media/../../escaped_target.txt", b"MALICIOUS")

        try:
            with self.assertRaises(ValueError) as ctx:
                dm.import_campaign_bundle(bundle_path)
            self.assertIn("Pfad-Traversal im Bundle erkannt", str(ctx.exception))
            self.assertFalse(Path(escape_file).exists())
        finally:
            dm.close()

    def test_import_campaign_bundle_rejects_malicious_entity_ids(self):
        dm = self._init_dm()
        bundle_path = self.exports_dir / "malicious-id.zip"

        manifest = {
            "format": "rpx-campaign-bundle-v1",
            "media_mode": "none",
            "worlds": [
                {
                    "id": "../../escape_world",
                    "name": "Escape World",
                    "genre": "Fantasy",
                    "file": "worlds/escape.json",
                }
            ],
            "sessions": [],
            "rulesets": [],
            "media": [],
        }
        world_payload = {
            "id": "../../escape_world",
            "settings": {"name": "Escape World"},
        }

        with ZipFile(bundle_path, "w") as archive:
            archive.writestr("manifest.json", json.dumps(manifest))
            archive.writestr("worlds/escape.json", json.dumps(world_payload))

        try:
            with self.assertRaises(ValueError) as ctx:
                dm.import_campaign_bundle(bundle_path)
            self.assertIn("unsicherer ID", str(ctx.exception))
            self.assertFalse((self.worlds_dir.parent / "escape_world.json").exists())
        finally:
            dm.close()

    def test_import_campaign_bundle_handles_missing_file_in_archive_with_value_error(self):
        dm = self._init_dm()
        bundle_path = self.exports_dir / "missing-file.zip"

        manifest = {
            "format": "rpx-campaign-bundle-v1",
            "media_mode": "none",
            "worlds": [
                {
                    "id": "w1",
                    "name": "Missing World",
                    "genre": "Fantasy",
                    "file": "worlds/does_not_exist.json",
                }
            ],
            "sessions": [],
            "rulesets": [],
            "media": [],
        }

        with ZipFile(bundle_path, "w") as archive:
            archive.writestr("manifest.json", json.dumps(manifest))

        try:
            with self.assertRaises(ValueError) as ctx:
                dm.import_campaign_bundle(bundle_path)
            self.assertIn("nicht im Bundle-Archiv gefunden", str(ctx.exception))
        finally:
            dm.close()

    def test_import_campaign_bundle_handles_corrupt_json_in_archive(self):
        dm = self._init_dm()
        bundle_path = self.exports_dir / "corrupt-json.zip"

        manifest = {
            "format": "rpx-campaign-bundle-v1",
            "media_mode": "none",
            "worlds": [
                {
                    "id": "w1",
                    "name": "Corrupt World",
                    "genre": "Fantasy",
                    "file": "worlds/w1.json",
                }
            ],
            "sessions": [],
            "rulesets": [],
            "media": [],
        }

        with ZipFile(bundle_path, "w") as archive:
            archive.writestr("manifest.json", json.dumps(manifest))
            archive.writestr("worlds/w1.json", b"{not valid json")

        try:
            with self.assertRaises(ValueError) as ctx:
                dm.import_campaign_bundle(bundle_path)
            self.assertIn("kein valides JSON", str(ctx.exception))
        finally:
            dm.close()

    def test_write_snapshot_and_backup_reject_path_traversal(self):
        dm = self._init_dm()
        try:
            with self.assertRaises(ValueError) as ctx:
                dm._write_snapshot("world", "../../evil", {"name": "test"})
            self.assertIn("Ungueltige Objekt-ID", str(ctx.exception))

            test_file = self.worlds_dir / "valid.json"
            test_file.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx2:
                dm._create_unique_backup(test_file, "world", "../evil")
            self.assertIn("Ungueltige Objekt-ID", str(ctx2.exception))
        finally:
            dm.close()

    def test_save_config_atomic_and_delete_persists_config(self):
        dm = self._init_dm()
        try:
            world = dm.create_world("Persist World", "Fantasy")
            session = dm.create_session(world.id, "Persist Session")
            self.assertIsNotNone(session)
            dm.current_world = world
            dm.current_session = session
            dm.save_config()

            # Config file exists and contains valid JSON with correct IDs
            self.assertTrue(self.config_file.exists())
            loaded = json.loads(self.config_file.read_text(encoding="utf-8"))
            self.assertEqual(loaded["last_world_id"], world.id)
            self.assertEqual(loaded["last_session_id"], session.id)

            # Deleting world cascades session and updates persisted config file
            self.assertTrue(dm.delete_world(world.id))
            loaded_after_delete = json.loads(self.config_file.read_text(encoding="utf-8"))
            self.assertIsNone(loaded_after_delete["last_world_id"])
            self.assertIsNone(loaded_after_delete["last_session_id"])
        finally:
            dm.close()

    def test_ruleset_target_validation(self):
        dm = self._init_dm()
        try:
            # Traversal rejected
            with self.assertRaises(ValueError):
                dm._resolve_ruleset_target("../../escape.json", "replace")
            # Non-json rejected
            with self.assertRaises(ValueError):
                dm._resolve_ruleset_target("rulesets/malicious.bat", "replace")
            # Empty filename rejected
            with self.assertRaises(ValueError):
                dm._resolve_ruleset_target("rulesets/", "replace")
        finally:
            dm.close()


if __name__ == "__main__":
    unittest.main()
