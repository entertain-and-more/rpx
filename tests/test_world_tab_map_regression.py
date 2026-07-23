# -*- coding: utf-8 -*-
"""Regressionen fuer Multi-Map-Umschaltung im WorldTab."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication

from rpx_pro.models.entities import GameMap
from rpx_pro.models.world import World
from rpx_pro.tabs.world_tab import WorldTab


class _DummyMapWidget:
    def __init__(self):
        self._elements = {}
        self._character_positions = {}

    def load_map(self, _path):
        return None

    def load_elements(self, elements):
        self._elements = dict(elements)

    def set_locations(self, _locations):
        return None

    def set_characters(self, _characters):
        return None

    def get_elements(self):
        return dict(self._elements)

    def get_character_positions(self):
        return dict(self._character_positions)


class _DummyDataManager:
    def __init__(self, world):
        self.current_world = world
        self.current_session = None
        self.worlds = {world.id: world}
        self.saved_world_ids = []

    def save_world(self, world):
        self.saved_world_ids.append(world.id)


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_add_map_preserves_previous_map_elements():
    _app()
    old_elements = {"legacy-note": {"kind": "note", "text": "Altbestand"}}
    old_positions = {"char-1": (12.0, 34.0)}
    world = World(id="world-1")
    world.maps["map-old"] = GameMap(
        id="map-old",
        name="Alte Karte",
        elements=dict(old_elements),
        character_positions=dict(old_positions),
    )
    world.active_map_id = "map-old"

    data_manager = _DummyDataManager(world)
    tab = WorldTab(data_manager)
    tab.world_map_widget = _DummyMapWidget()
    tab.world_map_widget._elements = dict(old_elements)
    tab.world_map_widget._character_positions = dict(old_positions)

    with patch("rpx_pro.tabs.world_tab.QInputDialog.getText", return_value=("Neue Karte", True)):
        with patch("rpx_pro.tabs.world_tab.generate_short_id", return_value="map-new"):
            tab.add_map()

    assert world.active_map_id == "map-new"
    assert world.maps["map-old"].elements == old_elements
    assert world.maps["map-old"].character_positions == old_positions
    assert world.maps["map-new"].elements == {}
    assert world.maps["map-new"].character_positions == {}
    assert data_manager.saved_world_ids == ["world-1", "world-1"]
