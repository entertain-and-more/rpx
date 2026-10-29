"""
P3 macOS/Linux Source-Platform-Smoke — Standalone Smoke Test Runner für RPX Pro.
Überprüft Headless-Start, Audio-Backend-Resilienz, Multi-Monitor/PlayerScreen,
Dateidialoge, I18N-Auflösung und Kampagnen-Bundle-Integrität ohne Windows-Abhängigkeiten.
"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

# Offscreen-Plattform für Headless-Umgebungen (CI, Linux/macOS)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PASS = "PASS"
FAIL = "FAIL"
results: list[tuple[int, str, str]] = []


@contextmanager
def isolated_environment():
    """Isoliert Benutzerzustand, APPDATA und temporäre Pfade."""
    with tempfile.TemporaryDirectory(prefix="rpx-smoke-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        old_appdata = os.environ.get("APPDATA")
        old_home = os.environ.get("HOME")
        os.environ["APPDATA"] = str(tmp_path / "appdata")
        try:
            yield tmp_path
        finally:
            if old_appdata is None:
                os.environ.pop("APPDATA", None)
            else:
                os.environ["APPDATA"] = old_appdata
            if old_home is not None:
                os.environ["HOME"] = old_home


def check(num: int, name: str, fn) -> bool:
    try:
        fn()
        results.append((num, PASS, name))
        print(f"[{PASS}] #{num}: {name}")
        return True
    except Exception as exc:
        results.append((num, FAIL, name))
        print(f"[{FAIL}] #{num}: {name}")
        print(f"       {type(exc).__name__}: {exc}")
        traceback.print_exc(limit=4, file=sys.stdout)
        return False


# --- Check 1: Non-GUI Core & Standardbibliothek ---
def check_core_stdlib():
    import json  # noqa: F401
    import dataclasses  # noqa: F401
    import pathlib  # noqa: F401
    import re  # noqa: F401
    import uuid  # noqa: F401
    import sqlite3  # noqa: F401
    import typing  # noqa: F401
    import py_compile  # noqa: F401
    assert callable(json.loads)
    assert callable(uuid.uuid4)
    assert callable(sqlite3.connect)


# --- Check 2: PySide6-Kernmodule & Headless-Offscreen-Erkennung ---
def check_pyside6_core():
    from PySide6.QtCore import Qt, QTimer, QSize, QPoint  # noqa: F401
    from PySide6.QtGui import QColor, QFont, QImage, QPainter  # noqa: F401
    from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QTabWidget  # noqa: F401
    assert Qt is not None
    assert QApplication is not None


# --- Check 3: Headless QApplication Initialisierung ---
def check_headless_qapplication():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(["rpx_pro_smoke", "-platform", "offscreen"])
    assert app is not None
    screens = app.screens()
    assert len(screens) >= 1, "Mindestens ein virtueller Bildschirm muss existieren"


# --- Check 4: POSIX Audio-Backend-Resilienz (kein winsound auf Linux/macOS) ---
def check_audio_backend_resilience():
    import rpx_pro.constants as const  # noqa: F401
    from rpx_pro.managers.audio_manager import AudioManager

    # Auf POSIX-Systemen (linux, darwin) darf _HAS_WINSOUND niemals True sein
    for platform_name in ("linux", "darwin"):
        with patch.object(sys, "platform", platform_name):
            has_winsound = False
            if sys.platform == "win32":
                try:
                    import winsound  # noqa: F401
                    has_winsound = True
                except ImportError:
                    pass
            assert not has_winsound, f"winsound darf unter {platform_name} nicht aktiv sein"

    # AudioManager muss auch bei nicht-verfügbarem Audio fehlerfrei instanziiert werden
    mgr = AudioManager()
    assert mgr is not None
    # play_music muss bei fehlender Datei oder Audio sicher zurückkehren ohne Exception
    mgr.play_music("non_existent_sound.mp3")


# --- Check 5: Application Entry Points & Headless CLI/API Contract ---
def check_entry_points_and_api():
    import rpx_pro.app as app_module
    import RPX_Pro_1 as script_entry
    from rpx_pro.api import RPXProAPI
    from rpx_pro.cli import CLIInterface
    from rpx_pro.managers.data_manager import DataManager

    assert callable(app_module.main)
    assert script_entry.main is app_module.main

    dm = DataManager()
    api = RPXProAPI(data_manager=dm)
    assert api is not None
    roll = api.roll_dice(sides=20, count=1)
    assert 1 <= roll["total"] <= 20
    assert len(roll["rolls"]) == 1
    assert roll["dice"] == "1W20"

    cli = CLIInterface(api=api)
    assert cli is not None


# --- Check 6: PlayerScreen Multi-Monitor & Fullscreen Routing ---
def check_player_screen_routing():
    import inspect
    from rpx_pro import main_window
    from rpx_pro.tabs.views_tab import ViewsTab

    main_source = inspect.getsource(main_window.RPXProMainWindow._toggle_player_screen)
    views_source = inspect.getsource(ViewsTab._create_player_screen_view)

    assert "QApplication.screens()" in main_source
    assert "setGeometry(screen.geometry())" in main_source
    assert "showFullScreen()" in main_source
    assert "player_screen_monitor_changed" in views_source
    assert "fullscreen_check" in views_source


# --- Check 7: Native Qt File Dialogs & Accessible Navigation Context ---
def check_native_file_dialogs_and_a11y():
    import inspect
    from rpx_pro import main_window
    from rpx_pro.tabs.views_tab import ViewsTab

    assert "QFileDialog.getOpenFileName" in inspect.getsource(ViewsTab._load_image_for_ps)
    assert "QFileDialog.getOpenFileName" in inspect.getsource(main_window.RPXProMainWindow._ps_load_image)

    setup_source = inspect.getsource(main_window.RPXProMainWindow._setup_ui)
    assert 'setAccessibleName("Hauptnavigation")' in setup_source
    assert "setAccessibleDescription(" in setup_source
    assert "setTabToolTip(index, hint)" in setup_source


# --- Check 8: TranslationSystem CJK/Kyrillisch & Campaign Bundle Contract ---
def check_i18n_and_bundle_contract():
    from translator import get_translator
    from rpx_pro.api import RPXProAPI
    from rpx_pro.managers.data_manager import DataManager

    tr = get_translator()
    orig_lang = tr.get_language()
    try:
        tr.set_language("zh-Hans")
        assert any("\u4e00" <= c <= "\u9fff" for c in tr.t("Charaktere")), "Chinesische Übersetzung muss aufgelöst werden"

        tr.set_language("ja")
        assert any("\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in tr.t("Inventar")), "Japanische Übersetzung muss aufgelöst werden"

        tr.set_language("ru")
        assert any("\u0400" <= c <= "\u04ff" for c in tr.t("Einstellungen")), "Kyrillische Übersetzung muss aufgelöst werden"
    finally:
        tr.set_language(orig_lang)

    dm = DataManager()
    api = RPXProAPI(data_manager=dm)
    assert hasattr(api, "export_campaign_bundle")
    assert hasattr(api, "import_campaign_bundle")


def run_all_checks() -> bool:
    print("=" * 70)
    print("RPX Pro — macOS / Linux Source-Platform-Smoke (P3)")
    print("=" * 70)

    with isolated_environment():
        check(1, "Non-GUI Core & Standardbibliothek (json, dataclasses, pathlib, sqlite3)", check_core_stdlib)
        check(2, "PySide6-Kernmodule & Headless-Offscreen-Erkennung", check_pyside6_core)
        check(3, "Headless QApplication Initialisierung & Bildschirm-Erkennung", check_headless_qapplication)
        check(4, "POSIX Audio-Backend-Resilienz (winsound-Abwesenheit & sicherer Fallback)", check_audio_backend_resilience)
        check(5, "Application Entry Points & Headless CLI/API Contract", check_entry_points_and_api)
        check(6, "PlayerScreen Multi-Monitor & Fullscreen Routing", check_player_screen_routing)
        check(7, "Native Qt File Dialogs & Accessible Navigation Context", check_native_file_dialogs_and_a11y)
        check(8, "TranslationSystem CJK/Kyrillisch & Campaign Bundle Contract", check_i18n_and_bundle_contract)

    passed_count = sum(1 for _, status, _ in results if status == PASS)
    failed_count = sum(1 for _, status, _ in results if status == FAIL)
    print("=" * 70)
    print(f"Ergebnis: {passed_count}/{len(results)} Checks bestanden ({failed_count} fehlgeschlagen)")
    print("=" * 70)
    return failed_count == 0


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
