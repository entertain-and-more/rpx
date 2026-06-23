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
from pathlib import Path

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


def test_map_widget_isnull_guards():
    src = _src("widgets/map_widget.py")
    assert src.count("isNull()") >= 2
