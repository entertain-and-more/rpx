# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 7/15).

A: data_manager nicht-atomare JSON-Writes -> Savegame-Verlust bei Crash.
B: player_screen hasattr() immer True -> Crash im TILES-Modus bei deaktivierter Kachel.
C: world_tab editierbare Skill-Zellen -> int()-ValueError-Crash beim Speichern.
D: map_widget QPixmap ohne isNull-Guard -> 0x0-Szene / leeres persistiertes Element.
"""
import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).parent.parent
RPX = ROOT / "rpx_pro"
sys.path.insert(0, str(ROOT))


def _src(rel: str) -> str:
    return (RPX / rel).read_text(encoding="utf-8")


def test_atomic_write_json(tmp_path):
    from rpx_pro.managers.data_manager import _atomic_write_json
    p = tmp_path / "sub" / "x.json"
    _atomic_write_json(p, {"a": 1, "umlaut": "ö"})
    assert json.loads(p.read_text(encoding="utf-8")) == {"a": 1, "umlaut": "ö"}
    # kein temp-Rest nach erfolgreichem os.replace
    assert not list(tmp_path.glob("**/*.tmp"))


def test_save_methods_use_atomic_write():
    src = _src("managers/data_manager.py")
    assert "_atomic_write_json(CONFIG_FILE" in src
    assert "_atomic_write_json(path, world.to_dict())" in src
    assert "_atomic_write_json(path, session.to_dict())" in src


def test_player_screen_tile_guards_use_is_not_none():
    src = _src("widgets/player_screen.py")
    assert 'hasattr(self, "tile_chars_list")' not in src
    assert "self.tile_chars_list is not None" in src
    assert "self.tile_missions_list is not None" in src
    assert "self.tile_chat_text is not None" in src


def test_world_tab_skill_int_guarded():
    src = _src("tabs/world_tab.py")
    assert "_cell_int(row, 1, 10)" in src
    assert "int(table.item(row, 1).text())" not in src


def test_inventory_tab_duplicate_choice_labels_are_disambiguated():
    from rpx_pro.tabs.inventory_tab import InventoryTab

    labels, label_to_id = InventoryTab._build_choice_labels([
        ("char-alpha", "Alex (NPC)"),
        ("char-beta", "Alex (NPC)"),
        ("char-gamma", "Mira (GM)"),
    ])

    assert labels[0] != labels[1]
    assert label_to_id[labels[0]] == "char-alpha"
    assert label_to_id[labels[1]] == "char-beta"
    assert labels[2] == "Mira (GM)"
    assert label_to_id[labels[2]] == "char-gamma"


def test_inventory_tab_no_longer_uses_label_index_lookup():
    src = _src("tabs/inventory_tab.py")
    assert ".index(name)" not in src
    assert "_build_choice_labels" in src
    assert "label_to_char_id[name]" in src
    assert "label_to_item_id[name]" in src
    assert "label_to_npc_id[name]" in src


def test_map_widget_isnull_guards():
    src = _src("widgets/map_widget.py")
    assert src.count("isNull()") >= 2


def test_models_from_dict_tolerate_missing_core_fields():
    from rpx_pro.models.enums import MessageRole, WeatherType
    from rpx_pro.models.session import ChatMessage, Session
    from rpx_pro.models.world import World

    world = World.from_dict({"settings": {"name": "Alte Welt"}})
    assert world.id
    assert world.settings.name == "Alte Welt"

    session = Session.from_dict({"chat_history": [{}], "current_weather": "kaputt"})
    assert session.id == ""
    assert session.name == "Unbenannte Session"
    assert session.current_weather is WeatherType.CLEAR
    assert session.chat_history[0].role is MessageRole.SYSTEM

    message = ChatMessage.from_dict({})
    assert message.role is MessageRole.SYSTEM
    assert message.author == "System"
    assert message.content == ""


def test_data_manager_quarantines_unloadable_savegame():
    from rpx_pro.managers import data_manager as dm_module
    from rpx_pro.managers.data_manager import DataManager

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        worlds_dir = base / "worlds"
        sessions_dir = base / "sessions"
        backups_dir = base / "backups"
        config_file = base / "config.json"
        for directory in (worlds_dir, sessions_dir, backups_dir):
            directory.mkdir(parents=True, exist_ok=True)
        broken = worlds_dir / "broken-world.json"
        broken.write_text("{not valid json", encoding="utf-8")

        patches = [
            patch.object(dm_module, "CONFIG_FILE", config_file),
            patch.object(dm_module, "WORLDS_DIR", worlds_dir),
            patch.object(dm_module, "SESSIONS_DIR", sessions_dir),
            patch.object(dm_module, "BACKUPS_DIR", backups_dir),
        ]
        for patcher in patches:
            patcher.start()
        try:
            dm = DataManager()
            quarantined = list((backups_dir / "quarantine").glob("world_broken-world_*.json"))
            assert not broken.exists()
            assert len(quarantined) == 1
        finally:
            for patcher in reversed(patches):
                patcher.stop()

    assert dm.worlds == {}
    assert dm.load_warnings
