"""
manage_translations.py - Multi-Language Translation Manager & CI Gate
======================================================================
Policy P-006: Tier-2 Multi-Language Standard (DE, EN, ES, ZH-HANS, JA, RU)

Verwendung:
    python manage_translations.py [--check] [--dir PROJEKTVERZEICHNIS]
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


def _atomic_write_json(file_path: str, data: dict) -> None:
    dirname = os.path.dirname(file_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    temp_path = f"{file_path}.tmp.{os.getpid()}"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
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


def check_translations(source_dir: str | None = None) -> bool:
    """CI Check: Ueberprueft Vollstaendigkeit aller 6 Zielsprachen in translations.json."""
    _ensure_utf8_streams()
    if not source_dir:
        source_dir = str(APP_DIR)
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)
    if not os.path.exists(trans_file):
        print(f"[FAIL] Übersetzungsdatei nicht gefunden: {trans_file}")
        return False

    try:
        with open(trans_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except (json.JSONDecodeError, OSError, Exception) as e:
        print(f"[FAIL] Fehler beim Parsen von {trans_file}: {e}")
        return False

    if not isinstance(translations, dict) or not translations:
        print("[FAIL] Übersetzungsdatei ist leer oder ungültig")
        return False

    missing_slots: list[str] = []
    missing_by_lang: dict[str, list[str]] = {lang: [] for lang in LANGUAGE_SLOTS}
    mojibake: list[str] = []

    for k, v in translations.items():
        if k.startswith("_"):
            continue
        if not isinstance(v, dict):
            missing_slots.append(k)
            continue
        for slot in LANGUAGE_SLOTS:
            if slot not in v:
                missing_slots.append(f"{k}:{slot}")
            elif not v.get(slot):
                missing_by_lang[slot].append(k)

        if any(c in k for c in ["\ufffd", "Ã", "âž•", "ðŸ"]):
            mojibake.append(k)
        for slot in LANGUAGE_SLOTS:
            val = v.get(slot, "")
            if isinstance(val, str) and any(c in val for c in ["\ufffd", "Ã", "âž•", "ðŸ"]):
                mojibake.append(f"{k}:{slot}")

    has_error = False
    if missing_slots:
        print(f"[FAIL] {len(missing_slots)} Einträge mit fehlenden Sprach-Slots")
        has_error = True
    for slot in LANGUAGE_SLOTS:
        if missing_by_lang[slot]:
            print(f"[FAIL] {len(missing_by_lang[slot])} Einträge ohne {slot}-Übersetzung")
            has_error = True
    if mojibake:
        print(f"[FAIL] {len(mojibake)} Einträge mit Mojibake-Artefakten")
        has_error = True

    if has_error:
        return False

    print(
        f"[PASS] Alle {len(translations)} UI-Schlüssel besitzen vollständige "
        f"de-, en-, es-, zh-Hans-, ja- und ru-Übersetzungen (100% Tier-2 Parität)."
    )
    return True


def manage_translations(source_dir: str | None = None) -> None:
    _ensure_utf8_streams()
    if not source_dir:
        source_dir = str(APP_DIR)
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        try:
            with open(trans_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
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
        "--dir",
        default=str(APP_DIR),
        help=f"Projektverzeichnis (Standard: {APP_DIR})",
    )
    args = parser.parse_args()

    if args.check:
        sys.exit(0 if check_translations(args.dir) else 1)
    manage_translations(args.dir)


if __name__ == "__main__":
    main()
