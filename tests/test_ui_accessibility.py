# -*- coding: utf-8 -*-
"""Gezielte UI-A11y-Regressionen für kompakte Desktop-Steuerelemente."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication, QDialog

from rpx_pro.tabs.world_tab import WorldTab


class _DummyDataManager:
    current_world = None
    current_session = None
    worlds = {}


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_location_image_browse_buttons_expose_accessible_context():
    _app()
    tab = WorldTab(_DummyDataManager())
    dialog = QDialog()

    _, exterior_btn, _ = tab._create_image_picker_row(
        dialog,
        "",
        "Außenbild",
        "Außenbild auswählen",
        "Öffnet einen Dateidialog, um ein Außenbild für den Ort auszuwählen.",
        "locationExteriorBrowseButton",
    )
    _, interior_btn, _ = tab._create_image_picker_row(
        dialog,
        "",
        "Innenbild",
        "Innenbild auswählen",
        "Öffnet einen Dateidialog, um ein Innenbild für den Ort auszuwählen.",
        "locationInteriorBrowseButton",
    )

    assert exterior_btn.text() == "..."
    assert exterior_btn.accessibleName() == "Außenbild auswählen"
    assert exterior_btn.accessibleDescription() == (
        "Öffnet einen Dateidialog, um ein Außenbild für den Ort auszuwählen."
    )
    assert exterior_btn.toolTip() == "Außenbild auswählen"
    assert exterior_btn.objectName() == "locationExteriorBrowseButton"

    assert interior_btn.text() == "..."
    assert interior_btn.accessibleName() == "Innenbild auswählen"
    assert interior_btn.accessibleDescription() == (
        "Öffnet einen Dateidialog, um ein Innenbild für den Ort auszuwählen."
    )
    assert interior_btn.toolTip() == "Innenbild auswählen"
    assert interior_btn.objectName() == "locationInteriorBrowseButton"

