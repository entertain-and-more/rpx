"""
manage_translations.py - Multi-Language Translation Manager & CI Gate
======================================================================
Policy P-006: Tier-2 Multi-Language Standard (DE, EN, ES, ZH-HANS, JA, RU)

Verwendung:
    python manage_translations.py [--check] [--stats] [--scan] [--dir PROJEKTVERZEICHNIS]
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
LANGUAGE_SLOTS = ("de", "en", "es", "zh-Hans", "ja", "ru")
TRANSLATION_FILE = "locales/translations.json"


def _ensure_utf8_streams() -> None:
    """Sichert UTF-8-Stream-Encoding fuer stdout und stderr unter Windows."""
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            with contextlib.suppress(OSError, ValueError, AttributeError):
                stream.reconfigure(encoding="utf-8", errors="replace")


STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"\n]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\'\n]+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\'\n]+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\'\n]+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\'\n]+)["\']\s*\)'),
    re.compile(r'addAction\s*\([^,\n]*["\']([^"\'\n]+)["\']\s*\)'),
    re.compile(r'addTab\s*\([^,\n]+,\s*["\']([^"\'\n]+)["\']\s*\)'),
    re.compile(r'setToolTip\s*\(\s*["\']([^"\'\n]+)["\']\s*\)'),
    re.compile(r'setPlaceholderText\s*\(\s*["\']([^"\'\n]+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurueck", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "oeffnen", "schliessen", "start", "aktualisieren",
    "kampfsystem", "rundensteuerung", "spielsitzung", "barrierefreiheit",
    "uebersicht", "tastaturkuerzel", "charaktere", "soundboard",
]


def with_language_slots(entry: dict) -> dict:
    """Preserve legacy catalogs while reserving all supported language slots."""
    normalized = dict(entry) if isinstance(entry, dict) else {}
    for language in LANGUAGE_SLOTS:
        normalized.setdefault(language, "")
    return normalized


def is_german(text: str) -> bool:
    if any(ch in text for ch in "äöüÄÖÜß"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir: str | None = None) -> set[str]:
    if not source_dir:
        source_dir = str(APP_DIR)
    german_strings: set[str] = set()
    skip_dirs = {
        "build",
        "dist",
        "venv",
        ".venv",
        "__pycache__",
        "releases",
        "scratch",
        "tests",
        "scripts",
        "docs",
        "flutter_port",
        "web_companion",
        ".git",
        ".pytest_cache",
        ".pytest_temp",
        ".ruff_cache",
    }
    skip_files = {
        "run_tests.py",
        "manage_translations.py",
        "translator.py",
        "source_platform_smoke.py",
    }

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py") and not file.startswith("test_") and file not in skip_files:
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue
                for pattern in STRING_PATTERNS:
                    for match in pattern.findall(content):
                        if is_german(match):
                            german_strings.add(match.strip())
    return german_strings


def load_translations(trans_file: Path | str) -> dict[str, Any]:
    """Lädt den Übersetzungskatalog ein."""
    path = Path(trans_file)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _atomic_write_json(file_path: str, data: dict) -> None:
    """Persistiert JSON-Daten atomar via Staging (.tmp.<pid>), flush und fsync."""
    dirname = os.path.dirname(file_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    temp_path = f"{file_path}.tmp.{os.getpid()}"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        if os.path.exists(file_path):
            with contextlib.suppress(OSError, PermissionError):
                os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
        os.replace(temp_path, file_path)
    except Exception:
        if os.path.exists(temp_path):
            with contextlib.suppress(OSError):
                os.remove(temp_path)
        raise


def save_translations(trans_file: Path | str, translations: dict[str, Any]) -> None:
    """Öffentliche Fassade für atomares Speichern."""
    _atomic_write_json(str(trans_file), translations)


def validate_catalog(trans_file: Path | str) -> tuple[bool, list[str]]:
    """
    Validiert die Tier-2 6-Sprachen-Parität (DE, EN, ES, ZH-HANS, JA, RU).
    Gibt (is_valid, findings) zurück.
    """
    path = Path(trans_file)
    findings: list[str] = []

    if not path.exists():
        findings.append(f"Übersetzungsdatei nicht gefunden: {path}")
        return False, findings

    try:
        data = load_translations(path)
    except Exception as exc:
        findings.append(f"Fehler beim Parsen von {path}: {exc}")
        return False, findings

    if not isinstance(data, dict) or not data:
        findings.append(f"Übersetzungsdatei {path} ist leer oder ungültig")
        return False, findings

    keys_checked = 0
    missing_by_lang: dict[str, list[str]] = {lang: [] for lang in LANGUAGE_SLOTS}
    mojibake: list[str] = []

    for k, v in data.items():
        if k.startswith("_"):
            continue
        keys_checked += 1

        if not isinstance(v, dict):
            findings.append(f"Schlüssel '{k}': Wert ist kein Objekt mit Sprachschlüsseln")
            continue

        for slot in LANGUAGE_SLOTS:
            if slot not in v:
                findings.append(f"Schlüssel '{k}': Fehlender Sprach-Slot '{slot}'")
            elif not str(v.get(slot, "")).strip():
                missing_by_lang[slot].append(k)

        if any(c in k for c in ["\ufffd", "Ã", "âž•", "ðŸ"]):
            mojibake.append(k)
        for slot in LANGUAGE_SLOTS:
            val = v.get(slot, "")
            if isinstance(val, str) and any(c in val for c in ["\ufffd", "Ã", "âž•", "ðŸ"]):
                mojibake.append(f"{k}:{slot}")

    if keys_checked == 0:
        findings.append("Katalog enthält keine prüfbaren Übersetzungsschlüssel")

    for slot in LANGUAGE_SLOTS:
        if missing_by_lang[slot]:
            findings.append(f"{len(missing_by_lang[slot])} Einträge ohne {slot}-Übersetzung")

    if mojibake:
        findings.append(f"{len(mojibake)} Einträge mit Mojibake-Artefakten")

    is_valid = len(findings) == 0
    return is_valid, findings


def check_translations(source_dir: str | None = None) -> bool:
    """CI Check: Ueberprueft Vollstaendigkeit aller 6 Zielsprachen in translations.json."""
    _ensure_utf8_streams()
    if not source_dir:
        source_dir = str(APP_DIR)
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)
    is_valid, findings = validate_catalog(trans_file)

    if not is_valid:
        for finding in findings:
            print(f"[FAIL] {finding}")
        return False

    data = load_translations(trans_file)
    content_keys = [k for k in data if not k.startswith("_")]
    print(
        f"[PASS] Alle {len(content_keys)} UI-Schlüssel besitzen vollständige "
        f"de-, en-, es-, zh-Hans-, ja- und ru-Übersetzungen (100% Tier-2 Parität)."
    )
    return True


def get_catalog_stats(source_dir_or_file: Path | str | None = None) -> dict[str, Any]:
    """Liefert detaillierte Statistiken über den Katalog."""
    if source_dir_or_file is None:
        path = APP_DIR / TRANSLATION_FILE
    else:
        p = Path(source_dir_or_file)
        path = p if p.name.endswith(".json") else (p / TRANSLATION_FILE)

    if not path.exists():
        return {"error": f"Datei nicht gefunden: {path}", "perfect_parity": False}

    try:
        data = load_translations(path)
    except Exception as exc:
        return {"error": f"Parse-Fehler: {exc}", "perfect_parity": False}

    content_keys = [k for k in data if not k.startswith("_")]
    total_keys = len(content_keys)

    stats: dict[str, Any] = {
        "file": str(path),
        "total_keys": total_keys,
        "metadata_keys": len(data) - total_keys,
        "languages": {},
        "perfect_parity": True,
    }

    for lang in LANGUAGE_SLOTS:
        filled = 0
        missing = 0
        for k in content_keys:
            val = data.get(k, {})
            if isinstance(val, dict) and str(val.get(lang, "")).strip():
                filled += 1
            else:
                missing += 1
        pct = (filled / total_keys * 100.0) if total_keys > 0 else 0.0
        stats["languages"][lang] = {
            "filled": filled,
            "missing": missing,
            "coverage_pct": round(pct, 2),
        }
        if missing > 0:
            stats["perfect_parity"] = False

    return stats


def print_catalog_stats(source_dir_or_file: Path | str | None = None) -> bool:
    """Gibt eine strukturierte Statistik-Übersicht für die Konsole aus."""
    _ensure_utf8_streams()
    stats = get_catalog_stats(source_dir_or_file)
    if "error" in stats:
        print(f"[FAIL] {stats['error']}")
        return False

    print("=" * 65)
    print("RPX Pro — Tier-2 Übersetzungs-Statistik (Policy P-006)")
    print("=" * 65)
    print(f"Datei:           {stats['file']}")
    print(f"UI-Schlüssel:    {stats['total_keys']}")
    print(f"Metadaten-Keys:  {stats['metadata_keys']}")
    print("-" * 65)
    print(f"{'Sprache':<12} | {'Gefüllt':<10} | {'Fehlend':<10} | {'Abdeckung':<10}")
    print("-" * 65)
    for lang in LANGUAGE_SLOTS:
        lang_stat = stats["languages"].get(lang, {})
        filled = lang_stat.get("filled", 0)
        missing = lang_stat.get("missing", 0)
        pct = lang_stat.get("coverage_pct", 0.0)
        print(f"{lang:<12} | {filled:<10} | {missing:<10} | {pct:>8.1f} %")
    print("=" * 65)
    if stats.get("perfect_parity"):
        print("[PASS] 100% Tier-2 Parität über alle 6 Zielsprachen erfüllt.")
    else:
        print("[WARN] Übersetzungslücken vorhanden — Parität unvollständig.")
    print("=" * 65)
    return bool(stats.get("perfect_parity"))


def scan_translations(source_dir: str | None = None) -> dict[str, Any]:
    """Führt einen Dry-Run Quellcode-Scan nach neuen deutschen Strings durch."""
    _ensure_utf8_streams()
    if not source_dir:
        source_dir = str(APP_DIR)
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    translations = load_translations(trans_file) if os.path.exists(trans_file) else {}
    found = find_german_strings(source_dir)
    new_strings = [s for s in sorted(found) if s not in translations]

    print(f"[i] Quellcode-Scan in: {source_dir}")
    print(f"[i] Gefundene UI-Strings gesamt: {len(found)}")
    print(f"[i] Bereits im Katalog erfasst:   {len(found) - len(new_strings)}")
    print(f"[i] Neu zu erfassende Strings:   {len(new_strings)}")
    if new_strings:
        print("\nNeu gefundene Strings (Dry-Run, nicht gespeichert):")
        for s in new_strings[:20]:
            print(f"  + {s}")
        if len(new_strings) > 20:
            print(f"  ... und {len(new_strings) - 20} weitere")
    else:
        print("[ok] Alle gefundenen Strings sind bereits im Katalog enthalten.")

    return {
        "found_count": len(found),
        "cataloged_count": len(found) - len(new_strings),
        "new_strings": new_strings,
    }


def manage_translations(source_dir: str | None = None) -> None:
    _ensure_utf8_streams()
    if not source_dir:
        source_dir = str(APP_DIR)
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        try:
            loaded = load_translations(trans_file)
            translations = {
                key: with_language_slots(value)
                for key, value in loaded.items()
            }
        except Exception:
            translations = {}
    else:
        translations = {}

    found = find_german_strings(source_dir)

    added = []
    for s in sorted(found):
        if s not in translations:
            translations[s] = with_language_slots({"de": s})
            added.append(s)

    translations = {
        key: with_language_slots(value)
        for key, value in translations.items()
    }

    _atomic_write_json(trans_file, translations)

    if added:
        print(f"[+] {len(added)} neue Einträge hinzugefügt:")
        for s in added[:20]:
            print(f"    - {s}")
        if len(added) > 20:
            print(f"    ... und {len(added) - 20} weitere")
    else:
        print("[i] Keine neuen deutschen Strings gefunden.")

    missing = [k for k, v in translations.items() if not v.get("en")]
    if missing:
        print(f"\n[!] {len(missing)} fehlende englische Übersetzungen")
    else:
        print("\n[ok] Alle Strings haben englische Übersetzungen.")

    print(f"\n[i] Gesamt: {len(translations)} Strings in {trans_file}")


def main() -> None:
    _ensure_utf8_streams()
    parser = argparse.ArgumentParser(
        description="Auto-Scanner für deutsche GUI-Strings und Translations-CI-Gate (Tier-2)."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validiert Vollständigkeit und Parität der Übersetzungen in allen 6 Sprachen.",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Zeigt detaillierte Statistiken und Abdeckungsgrade je Zielsprache an.",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Quellcode-Scan nach neuen deutschen UI-Strings im Read-Only-Modus (Dry-Run).",
    )
    parser.add_argument(
        "--dir",
        default=str(APP_DIR),
        help=f"Projektverzeichnis (Standard: {APP_DIR})",
    )
    args = parser.parse_args()

    if args.check:
        sys.exit(0 if check_translations(args.dir) else 1)
    if args.stats:
        sys.exit(0 if print_catalog_stats(args.dir) else 1)
    if args.scan:
        scan_translations(args.dir)
        sys.exit(0)
    manage_translations(args.dir)


if __name__ == "__main__":
    main()
