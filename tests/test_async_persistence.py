import threading
import time
import json
import inspect
from unittest.mock import patch

from rpx_pro.managers.async_persistence import AsyncPersistenceQueue
from rpx_pro.managers.data_manager import DataManager
from rpx_pro.models.world import World, WorldSettings


def test_queue_coalesces_pending_snapshots_per_resource():
    started = threading.Event()
    release = threading.Event()
    writes = []

    def writer(kind, object_id, payload):
        if not writes:
            started.set()
            assert release.wait(timeout=2)
        writes.append((kind, object_id, payload["version"]))

    queue = AsyncPersistenceQueue(writer)
    try:
        assert queue.submit("session", "s1", {"version": 1}) is True
        assert started.wait(timeout=2)
        assert queue.submit("session", "s1", {"version": 2}) is True
        assert queue.submit("world", "w1", {"version": 3}) is True
        release.set()
        queue.flush()
    finally:
        queue.close()

    assert writes == [
        ("session", "s1", 1),
        ("session", "s1", 2),
        ("world", "w1", 3),
    ]


def test_queue_discard_removes_pending_item():
    started = threading.Event()
    release = threading.Event()
    writes = []

    def writer(kind, object_id, payload):
        started.set()
        assert release.wait(timeout=2)
        writes.append((kind, object_id, payload["version"]))

    queue = AsyncPersistenceQueue(writer)
    try:
        assert queue.submit("world", "w1", {"version": 1}) is True
        assert started.wait(timeout=2)
        assert queue.submit("session", "s1", {"version": 2}) is True
        assert queue.discard("session", "s1") is True
        assert queue.discard("session", "s1") is False
        release.set()
        queue.flush()
    finally:
        queue.close()

    assert writes == [
        ("world", "w1", 1),
    ]


def test_queue_submit_does_not_wait_for_writer():
    release = threading.Event()

    def writer(kind, object_id, payload):
        assert release.wait(timeout=2)

    queue = AsyncPersistenceQueue(writer)
    try:
        started = time.perf_counter()
        assert queue.submit("session", "s1", {"version": 1}) is True
        assert time.perf_counter() - started < 0.5
    finally:
        release.set()
        queue.close()


def test_data_manager_writes_an_isolated_world_snapshot(tmp_path):
    manager = DataManager.__new__(DataManager)
    manager._async_saves = AsyncPersistenceQueue(manager._write_snapshot)
    world = World(id="w1", settings=WorldSettings(name="Vorher"))

    try:
        with patch("rpx_pro.managers.data_manager.WORLDS_DIR", tmp_path):
            assert manager.save_world_async(world) is True
            world.settings.name = "Nachher"
            manager.flush_async_saves()
            saved = json.loads((tmp_path / "w1.json").read_text(encoding="utf-8"))
    finally:
        manager.close()

    assert saved["settings"]["name"] == "Vorher"


def test_simulation_tick_only_marks_dirty_and_defers_persistence():
    from rpx_pro import main_window

    tick_source = inspect.getsource(main_window.RPXProMainWindow._simulation_tick)
    flush_source = inspect.getsource(main_window.RPXProMainWindow._flush_simulation_save)

    assert "save_session(" not in tick_source
    assert "_simulation_dirty" in tick_source
    assert "save_session_async" in flush_source
