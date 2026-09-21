"""Tests fuer Persistenz, Kaskadierung und Robustheit im DataManager."""

import time
from unittest.mock import patch

from rpx_pro.managers import data_manager as dm_module
from rpx_pro.managers.async_persistence import AsyncPersistenceQueue
from rpx_pro.managers.data_manager import DataManager


def test_delete_world_creates_backups_dir_and_cascades_sessions(tmp_path):
    project_root = tmp_path / "rpx_pro_data"
    worlds_dir = project_root / "worlds"
    sessions_dir = project_root / "sessions"
    backups_dir = project_root / "backups"  # Intentionally not created beforehand
    rulesets_dir = tmp_path / "rulesets"
    config_file = project_root / "config.json"

    worlds_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir.mkdir(parents=True, exist_ok=True)
    rulesets_dir.mkdir(parents=True, exist_ok=True)

    with patch.object(dm_module, "CONFIG_FILE", config_file), \
         patch.object(dm_module, "PROJECT_ROOT", project_root), \
         patch.object(dm_module, "WORLDS_DIR", worlds_dir), \
         patch.object(dm_module, "SESSIONS_DIR", sessions_dir), \
         patch.object(dm_module, "BACKUPS_DIR", backups_dir), \
         patch.object(dm_module, "RULESETS_DIR", rulesets_dir):
        dm = DataManager.__new__(DataManager)
        dm.worlds = {}
        dm.sessions = {}
        dm.current_world = None
        dm.current_session = None
        dm.config = dict(DataManager.DEFAULT_CONFIG)
        dm._async_saves = AsyncPersistenceQueue(dm._write_snapshot)

        try:
            world = dm.create_world("Test Welt", "Fantasy")
            session = dm.create_session(world.id, "Test Session")
            assert session is not None
            dm.current_world = world
            dm.current_session = session

            assert (worlds_dir / f"{world.id}.json").exists()
            assert (sessions_dir / f"{session.id}.json").exists()
            assert not backups_dir.exists()

            # Deleting world must succeed even if backups_dir did not exist yet
            success = dm.delete_world(world.id)
            assert success is True

            # World removed from memory and disk
            assert world.id not in dm.worlds
            assert not (worlds_dir / f"{world.id}.json").exists()
            assert backups_dir.exists()
            assert len(list(backups_dir.glob(f"world_{world.id}_*.json"))) == 1

            # Cascading delete: Associated session must also be removed
            assert session.id not in dm.sessions
            assert not (sessions_dir / f"{session.id}.json").exists()
            assert len(list(backups_dir.glob(f"session_{session.id}_*.json"))) == 1

            # Active pointers must be reset
            assert dm.current_world is None
            assert dm.current_session is None

            # Campaign bundle export must not crash due to orphaned sessions
            bundle_path = tmp_path / "bundle.zip"
            export_result = dm.export_campaign_bundle(bundle_path)
            assert export_result["world_count"] == 0
            assert export_result["session_count"] == 0
        finally:
            dm.close()


def test_delete_world_prevents_async_ghost_resurrection(tmp_path):
    project_root = tmp_path / "rpx_pro_data"
    worlds_dir = project_root / "worlds"
    sessions_dir = project_root / "sessions"
    backups_dir = project_root / "backups"
    config_file = project_root / "config.json"

    worlds_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir.mkdir(parents=True, exist_ok=True)
    backups_dir.mkdir(parents=True, exist_ok=True)

    with patch.object(dm_module, "CONFIG_FILE", config_file), \
         patch.object(dm_module, "PROJECT_ROOT", project_root), \
         patch.object(dm_module, "WORLDS_DIR", worlds_dir), \
         patch.object(dm_module, "SESSIONS_DIR", sessions_dir), \
         patch.object(dm_module, "BACKUPS_DIR", backups_dir):
        dm = DataManager.__new__(DataManager)
        dm.worlds = {}
        dm.sessions = {}
        dm.current_world = None
        dm.current_session = None
        dm.config = dict(DataManager.DEFAULT_CONFIG)
        dm._async_saves = AsyncPersistenceQueue(dm._write_snapshot)

        try:
            world = dm.create_world("Async World", "SciFi")
            # Queue an asynchronous save right before deleting
            world.settings.name = "Async World Modified"
            assert dm.save_world_async(world) is True

            # Delete world immediately
            assert dm.delete_world(world.id) is True

            # Wait to give any background thread a chance to write
            time.sleep(0.3)
            dm.flush_async_saves()

            # The deleted world file must NOT be recreated by async persistence
            assert not (worlds_dir / f"{world.id}.json").exists()
        finally:
            dm.close()


def test_delete_handles_existing_backup_collision(tmp_path):
    project_root = tmp_path / "rpx_pro_data"
    worlds_dir = project_root / "worlds"
    sessions_dir = project_root / "sessions"
    backups_dir = project_root / "backups"
    config_file = project_root / "config.json"

    worlds_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir.mkdir(parents=True, exist_ok=True)
    backups_dir.mkdir(parents=True, exist_ok=True)

    with patch.object(dm_module, "CONFIG_FILE", config_file), \
         patch.object(dm_module, "PROJECT_ROOT", project_root), \
         patch.object(dm_module, "WORLDS_DIR", worlds_dir), \
         patch.object(dm_module, "SESSIONS_DIR", sessions_dir), \
         patch.object(dm_module, "BACKUPS_DIR", backups_dir):
        dm = DataManager.__new__(DataManager)
        dm.worlds = {}
        dm.sessions = {}
        dm.current_world = None
        dm.current_session = None
        dm.config = dict(DataManager.DEFAULT_CONFIG)
        dm._async_saves = AsyncPersistenceQueue(dm._write_snapshot)

        try:
            world = dm.create_world("Collision World", "Cyberpunk")
            # Pre-create a colliding backup file matching timestamp pattern
            ts = int(time.time())
            collision_file = backups_dir / f"world_{world.id}_{ts}.json"
            collision_file.write_text("existing backup", encoding="utf-8")

            # delete_world must handle collision gracefully without failing
            assert dm.delete_world(world.id) is True
            assert not (worlds_dir / f"{world.id}.json").exists()
            backups = list(backups_dir.glob(f"world_{world.id}_*.json"))
            assert len(backups) == 2
        finally:
            dm.close()
