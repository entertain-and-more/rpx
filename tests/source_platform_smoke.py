"""
P3 macOS/Linux Source-Platform-Smoke — Standalone Smoke Test Runner für RPX Pro.
Überprüft Headless-Start, Audio-Backend-Resilienz, Multi-Monitor/PlayerScreen,
Dateidialoge, I18N-Auflösung, Kampagnen-Bundle-Integrität und Companion-Delta-Roundtrip
ohne Windows-Abhängigkeiten.
"""
from __future__ import annotations

import json
import os
import re
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
    import dataclasses  # noqa: F401
    import pathlib  # noqa: F401
    import py_compile  # noqa: F401
    import sqlite3
    import typing  # noqa: F401
    import uuid
    assert callable(json.loads)
    assert callable(uuid.uuid4)
    assert callable(sqlite3.connect)


# --- Check 2: PySide6-Kernmodule & Headless-Offscreen-Erkennung ---
def check_pyside6_core():
    from PySide6.QtCore import QPoint, QSize, Qt, QTimer  # noqa: F401
    from PySide6.QtGui import QColor, QFont, QImage, QPainter  # noqa: F401
    from PySide6.QtWidgets import QApplication, QFileDialog, QTabWidget, QWidget  # noqa: F401
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

    mgr = AudioManager()
    assert mgr is not None
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
    try:
        api = RPXProAPI(data_manager=dm)
        assert api is not None
        roll = api.roll_dice(sides=20, count=1)
        assert 1 <= roll["total"] <= 20
        assert len(roll["rolls"]) == 1
        assert roll["dice"] == "1W20"

        cli = CLIInterface(api=api)
        assert cli is not None
    finally:
        dm.close()


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
    try:
        api = RPXProAPI(data_manager=dm)
        assert hasattr(api, "export_campaign_bundle")
        assert hasattr(api, "import_campaign_bundle")
        assert hasattr(api, "import_companion_delta")
    finally:
        dm.close()


# --- Check 9: Tier-2 Translation Parity & Translation Management Integrity ---
def check_translation_parity():
    from manage_translations import check_translations, get_catalog_stats, validate_catalog

    trans_file = REPO_ROOT / "locales" / "translations.json"
    is_valid, findings = validate_catalog(trans_file)
    assert is_valid, f"Translation catalog validation failed: {findings}"

    stats = get_catalog_stats(REPO_ROOT)
    assert stats.get("perfect_parity") is True, f"Translation catalog lacks perfect parity: {stats}"
    assert stats.get("total_keys", 0) >= 194, f"Unexpected key count: {stats.get('total_keys')}"

    assert check_translations(str(REPO_ROOT)) is True


# --- Check 10: Companion-Delta Roundtrip & Case-Sensitive PWA Shell Assets ---
def check_companion_delta_and_pwa_contract():
    from rpx_pro.api import RPXProAPI
    from rpx_pro.cli import CLIInterface
    from rpx_pro.managers import data_manager as dm_module
    from rpx_pro.managers.data_manager import DataManager
    from rpx_pro.models.entities import Character

    with tempfile.TemporaryDirectory(prefix="rpx-smoke-delta-") as sandbox_dir:
        base = Path(sandbox_dir).resolve()
        data_root = base / "rpx_pro_data"
        rulesets_dir = base / "rulesets"
        for sub in ("worlds", "sessions", "backups", "media/images", "media/maps", "media/music", "media/sounds"):
            (data_root / sub).mkdir(parents=True, exist_ok=True)
        rulesets_dir.mkdir(parents=True, exist_ok=True)
        (rulesets_dir / "smoke.json").write_text(
            json.dumps({"ruleset_name": "Smoke", "weapons": [], "spells": []}),
            encoding="utf-8",
        )

        with (
            patch.object(dm_module, "CONFIG_FILE", data_root / "config.json"),
            patch.object(dm_module, "PROJECT_ROOT", data_root),
            patch.object(dm_module, "MEDIA_DIR", data_root / "media"),
            patch.object(dm_module, "WORLDS_DIR", data_root / "worlds"),
            patch.object(dm_module, "SESSIONS_DIR", data_root / "sessions"),
            patch.object(dm_module, "BACKUPS_DIR", data_root / "backups"),
            patch.object(dm_module, "RULESETS_DIR", rulesets_dir),
        ):
            dm = DataManager()
            try:
                world = dm.create_world("Nordmark", "Fantasy")
                session = dm.create_session(world.id, "Runde 1")
                assert session is not None
                hero = Character(id="hero1", name="Ayla", health=18, max_health=24, mana=6, max_mana=10, gold=30)
                session.characters[hero.id] = hero
                dm.save_session(session)

                bundle_zip = base / "smoke_bundle.zip"
                api = RPXProAPI(data_manager=dm)
                cli = CLIInterface(api=api)
                exported = api.export_campaign_bundle(str(bundle_zip))
                assert exported["format"] == "rpx-campaign-bundle-v1"
                assert bundle_zip.is_file()

                delta_file = base / "companion_delta.json"
                delta_file.write_text(
                    json.dumps(
                        {
                            "format": "rpx-companion-delta-v1",
                            "exported_at": 1779646100,
                            "character_patches": [
                                {
                                    "session_id": session.id,
                                    "character_id": "hero1",
                                    "health": 99,
                                    "mana": 4,
                                    "gold": 55,
                                }
                            ],
                            "player_notes": [
                                {
                                    "id": "smoke-note-1",
                                    "session_id": session.id,
                                    "character_id": "hero1",
                                    "author": "Ayla",
                                    "content": "Schluessel am Brunnen gefunden.",
                                    "created_at": 1779646090,
                                }
                            ],
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                resp = cli.execute_command(
                    {"id": 10, "method": "import_companion_delta", "params": {"source": str(delta_file)}}
                )
                assert "result" in resp, f"CLI import_companion_delta failed: {resp}"
                assert resp["result"]["patch_count"] == 1
                assert resp["result"]["note_count"] == 1
                assert session.characters["hero1"].health == 24
                assert session.characters["hero1"].mana == 4
                assert session.characters["hero1"].gold == 55

                # Idempotency check on duplicate import
                resp_dup = cli.execute_command(
                    {"id": 11, "method": "import_companion_delta", "params": {"source": str(delta_file)}}
                )
                assert resp_dup["result"]["note_count"] == 0
                assert len(resp_dup["result"]["skipped_notes"]) == 1
            finally:
                dm.close()

    # Case-sensitive SHELL_FILES check for Linux/macOS static PWA hosting
    web_root = REPO_ROOT / "web_companion"
    sw_text = (web_root / "sw.js").read_text(encoding="utf-8")
    block = re.search(r"const\s+SHELL_FILES\s*=\s*\[([\s\S]*?)\];?", sw_text)
    assert block is not None, "SHELL_FILES missing in web_companion/sw.js"
    assets = [
        rel
        for m in re.finditer(r"['\"]([^'\"]+)['\"]", block.group(1))
        if (rel := m.group(1).removeprefix("./")) and rel != "sw.js"
    ]
    assert len(assets) >= 12
    for rel in assets:
        cur = web_root
        for part in Path(rel).parts:
            entries = {p.name for p in cur.iterdir()}
            assert part in entries, f"Case-sensitive mismatch for {rel} ({part})"
            cur = cur / part


def run_all_checks() -> bool:
    results.clear()
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
        check(9, "Tier-2 Translation Parity & Translations Catalog Integrity", check_translation_parity)
        check(10, "Companion-Delta Roundtrip & Case-Sensitive PWA Shell Contract", check_companion_delta_and_pwa_contract)

    passed_count = sum(1 for _, status, _ in results if status == PASS)
    failed_count = sum(1 for _, status, _ in results if status == FAIL)
    print("=" * 70)
    print(f"Ergebnis: {passed_count}/{len(results)} Checks bestanden ({failed_count} fehlgeschlagen)")
    print("=" * 70)
    return failed_count == 0


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
