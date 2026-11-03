"""Hermetic contract and regression tests for manage_translations.py CLI and TranslationSystem."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import manage_translations
from translator import TranslationSystem

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_manage_translations_help():
    result = subprocess.run(
        [sys.executable, "manage_translations.py", "--help"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "--check" in result.stdout
    assert "--stats" in result.stdout
    assert "--scan" in result.stdout
    assert "--dir" in result.stdout


def test_manage_translations_check_flag_exits_cleanly():
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "manage_translations.py"), "--check"],
        cwd=Path.home(),  # Run from outside repo to verify CWD independence
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "100%" in result.stdout
    assert "194" in result.stdout


def test_manage_translations_check_flag_does_not_create_phantom_directory(tmp_path):
    phantom_dir = tmp_path / "--check"
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "manage_translations.py"), "--check", "--dir", str(tmp_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert not phantom_dir.exists()


def test_check_translations_detects_missing_keys(tmp_path):
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    catalog = {
        "_meta": {"version": "1.0"},
        "sample_key": {
            "de": "Datei",
            "en": "File",
            "es": "Archivo",
            "zh-Hans": "",  # missing in zh-Hans
            "ja": "ファイル",
            "ru": "Файл",
        },
    }
    (locales_dir / "translations.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")

    result = manage_translations.check_translations(str(tmp_path))
    assert result is False


def test_check_translations_passes_with_full_parity(tmp_path):
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    catalog = {
        "_meta": {"version": "1.0"},
        "sample_key": {
            "de": "Datei",
            "en": "File",
            "es": "Archivo",
            "zh-Hans": "文件",
            "ja": "ファイル",
            "ru": "Файл",
        },
    }
    (locales_dir / "translations.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")

    result = manage_translations.check_translations(str(tmp_path))
    assert result is True


def test_find_german_strings_excludes_tests_and_helpers(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "source_platform_smoke.py").write_text(
        'sample = "# Überschrift\\n\\nÄpfel, Öl, Übergabe."', encoding="utf-8"
    )
    (tests_dir / "test_sample.py").write_text('text = "Fehler im Test"', encoding="utf-8")

    src_file = tmp_path / "gui_widget.py"
    src_file.write_text('btn = QPushButton("Datei öffnen")', encoding="utf-8")

    found = manage_translations.find_german_strings(str(tmp_path))
    assert "Datei öffnen" in found
    assert not any("Äpfel" in s for s in found)
    assert not any("Fehler im Test" in s for s in found)


def test_atomic_write_json_creates_clean_file(tmp_path):
    target = tmp_path / "locales" / "translations.json"
    data = {"hello": {"de": "Hallo", "en": "Hello"}}
    manage_translations._atomic_write_json(str(target), data)

    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == data
    tmp_files = list(tmp_path.glob("**/*.tmp*"))
    assert tmp_files == []


def test_ensure_utf8_streams_safe_execution():
    manage_translations._ensure_utf8_streams()


def test_translator_find_german_strings_excludes_tests_and_helpers(tmp_path):
    ts = TranslationSystem("de", app_dir=tmp_path)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "source_platform_smoke.py").write_text(
        'sample = "# Überschrift\\n\\nÄpfel, Öl, Übergabe."', encoding="utf-8"
    )
    (tmp_path / "component.py").write_text('lbl = QLabel("Einstellungen")', encoding="utf-8")

    found = ts._find_german_strings(tmp_path)
    assert "Einstellungen" in found
    assert not any("Äpfel" in s for s in found)


def test_manage_translations_stats_flag():
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "manage_translations.py"), "--stats"],
        cwd=Path.home(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "Tier-2 Übersetzungs-Statistik" in result.stdout
    assert "194" in result.stdout
    assert "100.0 %" in result.stdout
    assert "100% Tier-2 Parität" in result.stdout


def test_manage_translations_scan_flag_is_dry_run(tmp_path):
    widget_file = tmp_path / "sample_view.py"
    widget_file.write_text('btn = QPushButton("Einstellungen speichern")', encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "manage_translations.py"), "--scan", "--dir", str(tmp_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "Quellcode-Scan" in result.stdout
    assert "Einstellungen speichern" in result.stdout
    # Verify no translations.json was generated in dry-run mode
    assert not (tmp_path / "locales" / "translations.json").exists()


def test_get_catalog_stats_programmatic_api():
    stats = manage_translations.get_catalog_stats(PROJECT_ROOT)
    assert stats["perfect_parity"] is True
    assert stats["total_keys"] >= 194
    for lang in ("de", "en", "es", "zh-Hans", "ja", "ru"):
        lang_data = stats["languages"][lang]
        assert lang_data["filled"] >= 194
        assert lang_data["missing"] == 0
        assert lang_data["coverage_pct"] == 100.0


def test_validate_catalog_handles_corrupt_and_missing_files(tmp_path):
    # Non-existent
    valid, findings = manage_translations.validate_catalog(tmp_path / "nonexistent.json")
    assert valid is False
    assert any("nicht gefunden" in f for f in findings)

    # Corrupt JSON
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{ corrupt json ...", encoding="utf-8")
    valid, findings = manage_translations.validate_catalog(bad_file)
    assert valid is False
    assert any("Fehler beim Parsen" in f for f in findings)

    # Empty dictionary
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("{}", encoding="utf-8")
    valid, findings = manage_translations.validate_catalog(empty_file)
    assert valid is False
    assert any("leer oder ungültig" in f for f in findings)


def test_translator_atomic_save_persistence(tmp_path):
    ts = TranslationSystem("de", app_dir=tmp_path)
    ts.add_translation("test_action", de="Test Aktion", en="Test Action", es="Acción de prueba",
                       **{"zh-Hans": "测试操作", "ja": "テストアクション", "ru": "Тестовое действие"})

    trans_file = tmp_path / "locales" / "translations.json"
    assert trans_file.exists()
    data = json.loads(trans_file.read_text(encoding="utf-8"))
    assert "test_action" in data
    assert data["test_action"]["de"] == "Test Aktion"
    assert data["test_action"]["zh-Hans"] == "测试操作"

    # Verify no temporary staging files remain
    tmp_files = list(tmp_path.glob("**/*.tmp*"))
    assert tmp_files == []


def test_save_translations_public_helper(tmp_path):
    dest = tmp_path / "catalog.json"
    data = {"sample": {"de": "Muster", "en": "Sample"}}
    manage_translations.save_translations(dest, data)
    assert dest.exists()
    loaded = json.loads(dest.read_text(encoding="utf-8"))
    assert loaded == data
