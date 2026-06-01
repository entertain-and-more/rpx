import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from rpx_pro.api import RPXProAPI
from rpx_pro.managers import data_manager as dm_module
from rpx_pro.managers.data_manager import DataManager
from rpx_pro.models.entities import Character, GameMap
from rpx_pro.models.world import Location


class CampaignBundleExportTests(unittest.TestCase):
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

        self._write_fixture_files()
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

    def _write_fixture_files(self):
        (self.media_dir / "maps" / "world-map.png").write_bytes(b"map")
        (self.media_dir / "images" / "tavern.png").write_bytes(b"img")
        (self.media_dir / "images" / "hero.png").write_bytes(b"hero")
        (self.media_dir / "music" / "theme.ogg").write_bytes(b"music")
        (self.rulesets_dir / "basic.json").write_text(
            json.dumps(
                {
                    "ruleset_name": "Basisregeln",
                    "weapons": [{"name": "Kurzschwert"}],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _build_sample_state(self):
        dm = DataManager()
        world = dm.create_world("Bundle World", "Fantasy")
        world.map_image = "maps/world-map.png"
        world.locations["loc-1"] = Location(
            id="loc-1",
            name="Taverne",
            exterior_image="images/tavern.png",
            background_music="music/theme.ogg",
        )
        world.maps["map-1"] = GameMap(
            id="map-1",
            name="Weltkarte",
            background_image="maps/world-map.png",
        )
        dm.save_world(world)

        session = dm.create_session(world.id, "Session One")
        self.assertIsNotNone(session)
        session.characters["char-1"] = Character(
            id="char-1",
            name="Ayla",
            image_path="images/hero.png",
        )
        dm.save_session(session)
        return dm, world, session

    def _write_bundle(
        self,
        bundle_path: Path,
        manifest: dict,
        world_payloads: dict[str, dict],
        session_payloads: dict[str, dict],
        rulesets: dict[str, dict],
        media_files: dict[str, bytes],
    ) -> None:
        with ZipFile(bundle_path, "w") as archive:
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.writestr(
                "media/manifest.json",
                json.dumps(manifest.get("media", []), ensure_ascii=False, indent=2),
            )
            for world_id, payload in world_payloads.items():
                archive.writestr(
                    f"worlds/{world_id}.json",
                    json.dumps(payload, ensure_ascii=False, indent=2),
                )
            for session_id, payload in session_payloads.items():
                archive.writestr(
                    f"sessions/{session_id}.json",
                    json.dumps(payload, ensure_ascii=False, indent=2),
                )
            for ruleset_name, payload in rulesets.items():
                archive.writestr(
                    f"rulesets/{ruleset_name}.json",
                    json.dumps(payload, ensure_ascii=False, indent=2),
                )
            for archive_path, content in media_files.items():
                archive.writestr(archive_path, content)

    def test_export_campaign_bundle_rewrites_paths_and_writes_manifest(self):
        dm, world, session = self._build_sample_state()
        bundle_path = self.exports_dir / "campaign-manifest.zip"

        result = dm.export_campaign_bundle(bundle_path, include_media="manifest")

        self.assertEqual(result["format"], "rpx-campaign-bundle-v1")
        self.assertEqual(result["world_count"], 1)
        self.assertEqual(result["session_count"], 1)
        self.assertEqual(result["ruleset_count"], 1)
        self.assertEqual(result["media_mode"], "manifest")

        with ZipFile(bundle_path) as archive:
            names = set(archive.namelist())
            self.assertIn("manifest.json", names)
            self.assertIn("media/manifest.json", names)
            self.assertIn(f"worlds/{world.id}.json", names)
            self.assertIn(f"sessions/{session.id}.json", names)
            self.assertIn("rulesets/basic.json", names)
            self.assertNotIn("media/maps/world-map.png", names)
            self.assertNotIn("media/images/hero.png", names)

            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            world_payload = json.loads(archive.read(f"worlds/{world.id}.json").decode("utf-8"))
            session_payload = json.loads(archive.read(f"sessions/{session.id}.json").decode("utf-8"))

        self.assertEqual(manifest["media_mode"], "manifest")
        self.assertEqual(world_payload["map_image"], "media/maps/world-map.png")
        self.assertEqual(
            world_payload["locations"]["loc-1"]["exterior_image"],
            "media/images/tavern.png",
        )
        self.assertEqual(
            world_payload["locations"]["loc-1"]["background_music"],
            "media/music/theme.ogg",
        )
        self.assertEqual(
            session_payload["characters"]["char-1"]["image_path"],
            "media/images/hero.png",
        )
        self.assertTrue(
            any(
                entry["bundle_path"] == "media/maps/world-map.png"
                and entry["exists"]
                and not entry["included"]
                for entry in manifest["media"]
            )
        )

    def test_api_export_campaign_bundle_can_embed_media_files(self):
        dm, world, session = self._build_sample_state()
        api = RPXProAPI(dm)
        bundle_path = self.exports_dir / "campaign-files.zip"

        result = api.export_campaign_bundle(
            str(bundle_path),
            session_ids=[session.id],
            include_media="files",
        )

        self.assertEqual(result["world_count"], 1)
        self.assertEqual(result["session_count"], 1)
        self.assertEqual(result["media_mode"], "files")

        with ZipFile(bundle_path) as archive:
            names = set(archive.namelist())
            self.assertIn(f"worlds/{world.id}.json", names)
            self.assertIn(f"sessions/{session.id}.json", names)
            self.assertIn("media/maps/world-map.png", names)
            self.assertIn("media/images/tavern.png", names)
            self.assertIn("media/images/hero.png", names)
            self.assertIn("media/music/theme.ogg", names)

            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))

        self.assertTrue(
            any(
                entry["bundle_path"] == "media/images/hero.png"
                and entry["included"]
                for entry in manifest["media"]
            )
        )

    def test_import_campaign_bundle_renames_conflicts_and_extracts_media(self):
        dm, world, session = self._build_sample_state()
        bundle_path = self.exports_dir / "campaign-import.zip"
        result = dm.export_campaign_bundle(bundle_path, include_media="files")
        self.assertEqual(result["media_mode"], "files")

        import_result = dm.import_campaign_bundle(bundle_path, conflict_strategy="rename")

        imported_world = next(item for item in import_result["worlds"] if item["action"] == "renamed")
        imported_session = next(item for item in import_result["sessions"] if item["action"] == "renamed")
        imported_ruleset = next(item for item in import_result["rulesets"] if item["action"] == "renamed")

        self.assertNotEqual(imported_world["id"], world.id)
        self.assertNotEqual(imported_session["id"], session.id)
        self.assertTrue((self.rulesets_dir / imported_ruleset["file"]).exists())

        world_copy = dm.worlds[imported_world["id"]]
        session_copy = dm.sessions[imported_session["id"]]
        self.assertEqual(session_copy.world_id, world_copy.id)
        self.assertEqual(Path(world_copy.map_image), self.media_dir / "maps" / "world-map-2.png")
        self.assertEqual(
            Path(world_copy.locations["loc-1"].exterior_image),
            self.media_dir / "images" / "tavern-2.png",
        )
        self.assertEqual(
            Path(session_copy.characters["char-1"].image_path),
            self.media_dir / "images" / "hero-2.png",
        )
        self.assertEqual((self.media_dir / "music" / "theme-2.ogg").read_bytes(), b"music")

    def test_import_campaign_bundle_replace_overwrites_existing_entities(self):
        dm, world, session = self._build_sample_state()
        bundle_path = self.exports_dir / "campaign-replace.zip"
        manifest = {
            "format": "rpx-campaign-bundle-v1",
            "media_mode": "files",
            "worlds": [{"id": world.id, "name": "Importwelt", "genre": "Sci-Fi", "file": f"worlds/{world.id}.json"}],
            "sessions": [{"id": session.id, "world_id": world.id, "name": "Importsession", "file": f"sessions/{session.id}.json"}],
            "rulesets": [{"id": "basic", "name": "Basisregeln", "file": "rulesets/basic.json"}],
            "media": [],
        }
        world_payload = dm.worlds[world.id].to_dict()
        world_payload["settings"]["name"] = "Importwelt"
        world_payload["settings"]["genre"] = "Sci-Fi"
        world_payload["map_image"] = "media/maps/world-map.png"
        session_payload = dm.sessions[session.id].to_dict()
        session_payload["name"] = "Importsession"
        session_payload["characters"]["char-1"]["image_path"] = "media/images/hero.png"
        self._write_bundle(
            bundle_path,
            manifest,
            {world.id: world_payload},
            {session.id: session_payload},
            {"basic": {"ruleset_name": "Basisregeln", "weapons": [{"name": "Langschwert"}]}},
            {
                "media/maps/world-map.png": b"map-new",
                "media/images/hero.png": b"hero-new",
            },
        )

        import_result = dm.import_campaign_bundle(bundle_path, conflict_strategy="replace")

        self.assertEqual(import_result["worlds"][0]["action"], "replaced")
        self.assertEqual(import_result["sessions"][0]["action"], "replaced")
        self.assertEqual(dm.worlds[world.id].settings.name, "Importwelt")
        self.assertEqual(dm.worlds[world.id].settings.genre, "Sci-Fi")
        self.assertEqual(dm.sessions[session.id].name, "Importsession")
        self.assertEqual((self.media_dir / "maps" / "world-map.png").read_bytes(), b"map-new")
        self.assertEqual((self.media_dir / "images" / "hero.png").read_bytes(), b"hero-new")
        ruleset_payload = json.loads((self.rulesets_dir / "basic.json").read_text(encoding="utf-8"))
        self.assertEqual(ruleset_payload["weapons"][0]["name"], "Langschwert")

    def test_import_campaign_bundle_accepts_legacy_relative_media_paths(self):
        dm = DataManager()
        bundle_path = self.exports_dir / "campaign-legacy.zip"
        world_id = "legacy-world"
        session_id = "legacy-session"
        manifest = {
            "format": "rpx-campaign-bundle-v1",
            "media_mode": "files",
            "worlds": [{"id": world_id, "name": "Altwelt", "genre": "Fantasy", "file": f"worlds/{world_id}.json"}],
            "sessions": [{"id": session_id, "world_id": world_id, "name": "Alt-Session", "file": f"sessions/{session_id}.json"}],
            "rulesets": [{"id": "legacy", "name": "Altregeln", "file": "rulesets/legacy.json"}],
            "media": [],
        }
        world_payload = {
            "id": world_id,
            "settings": {"name": "Altwelt", "genre": "Fantasy"},
            "locations": {
                "loc-1": {
                    "id": "loc-1",
                    "name": "Archiv",
                    "exterior_image": "images/legacy-tavern.png",
                    "background_music": "music/legacy-theme.ogg",
                }
            },
            "maps": {
                "map-1": {
                    "id": "map-1",
                    "name": "Altkarte",
                    "background_image": "maps/legacy-map.png",
                }
            },
            "map_image": "maps/legacy-map.png",
        }
        session_payload = {
            "id": session_id,
            "world_id": world_id,
            "name": "Alt-Session",
            "characters": {
                "char-1": {
                    "id": "char-1",
                    "name": "Bran",
                    "image_path": "images/legacy-hero.png",
                }
            },
        }
        self._write_bundle(
            bundle_path,
            manifest,
            {world_id: world_payload},
            {session_id: session_payload},
            {"legacy": {"ruleset_name": "Altregeln", "weapons": []}},
            {
                "maps/legacy-map.png": b"legacy-map",
                "images/legacy-tavern.png": b"legacy-img",
                "images/legacy-hero.png": b"legacy-hero",
                "music/legacy-theme.ogg": b"legacy-music",
            },
        )

        import_result = dm.import_campaign_bundle(bundle_path, conflict_strategy="rename")

        self.assertEqual(import_result["world_count"], 1)
        self.assertEqual(import_result["session_count"], 1)
        imported_world = dm.worlds[world_id]
        imported_session = dm.sessions[session_id]
        self.assertEqual(Path(imported_world.map_image), self.media_dir / "maps" / "legacy-map.png")
        self.assertEqual(
            Path(imported_world.locations["loc-1"].exterior_image),
            self.media_dir / "images" / "legacy-tavern.png",
        )
        self.assertEqual(
            Path(imported_session.characters["char-1"].image_path),
            self.media_dir / "images" / "legacy-hero.png",
        )
        self.assertEqual((self.media_dir / "music" / "legacy-theme.ogg").read_bytes(), b"legacy-music")


if __name__ == "__main__":
    unittest.main()
