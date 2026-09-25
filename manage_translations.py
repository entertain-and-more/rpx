"""
manage_translations.py - Auto-Scanner fuer deutsche GUI-Strings
================================================================
Findet deutsche Strings in .py-Dateien und pflegt locales/translations.json.

Verwendung:
    python manage_translations.py [--dir PROJEKTVERZEICHNIS]
    python manage_translations.py --check [PROJEKTVERZEICHNIS]
"""

import json
import os
import re
import sys

TRANSLATION_FILE = "locales/translations.json"
LANGUAGE_SLOTS = ("de", "en", "es", "zh-Hans", "ja", "ru")

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurueck", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "oeffnen", "schliessen", "start", "aktualisieren",
]


def with_language_slots(entry):
    """Preserve legacy catalogs while reserving all supported language slots."""
    normalized = dict(entry) if isinstance(entry, dict) else {}
    for language in LANGUAGE_SLOTS:
        normalized.setdefault(language, "")
    return normalized


def is_german(text):
    if any(ch in text for ch in "\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir):
    german_strings = set()
    skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases'}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
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


def manage_translations(source_dir="."):
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        with open(trans_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        translations = {
            key: with_language_slots(value)
            for key, value in loaded.items()
        }
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

    os.makedirs(os.path.dirname(trans_file), exist_ok=True)
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)

    if added:
        print(f"[+] {len(added)} neue Eintraege hinzugefuegt:")
        for s in added[:20]:
            print(f"    - {s}")
        if len(added) > 20:
            print(f"    ... und {len(added) - 20} weitere")
    else:
        print("[i] Keine neuen deutschen Strings gefunden.")

    missing = [k for k, v in translations.items() if not v.get("en")]
    if missing:
        print(f"\n[!] {len(missing)} fehlende englische Uebersetzungen")
    else:
        print("\n[ok] Alle Strings haben englische Uebersetzungen.")

    print(f"\n[i] Gesamt: {len(translations)} Strings in {trans_file}")


def check_translations(source_dir=".") -> bool:
    """Validiert die Übersetzungsdatei auf vollständige de, en, es Werte und Slot-Struktur."""
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)
    if not os.path.exists(trans_file):
        print(f"[FAIL] Übersetzungsdatei nicht gefunden: {trans_file}")
        return False

    with open(trans_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or not data:
        print("[FAIL] Übersetzungsdatei ist leer oder ungültig")
        return False

    missing_slots = []
    missing_de = []
    missing_en = []
    missing_es = []
    mojibake = []

    for k, v in data.items():
        if not isinstance(v, dict):
            missing_slots.append(k)
            continue
        for slot in LANGUAGE_SLOTS:
            if slot not in v:
                missing_slots.append(f"{k}:{slot}")
        if not v.get("de"):
            missing_de.append(k)
        if not v.get("en"):
            missing_en.append(k)
        if not v.get("es"):
            missing_es.append(k)
        if any(c in k for c in ["\ufffd", "Ã", "âž•", "ðŸ"]):
            mojibake.append(k)

    if missing_slots or missing_de or missing_en or missing_es or mojibake:
        if missing_slots:
            print(f"[FAIL] {len(missing_slots)} Einträge mit fehlenden Sprach-Slots")
        if missing_de:
            print(f"[FAIL] {len(missing_de)} Einträge ohne deutsche Übersetzung")
        if missing_en:
            print(f"[FAIL] {len(missing_en)} Einträge ohne englische Übersetzung")
        if missing_es:
            print(f"[FAIL] {len(missing_es)} Einträge ohne spanische Übersetzung")
        if mojibake:
            print(f"[FAIL] {len(mojibake)} Einträge mit Mojibake-Artefakten")
        return False

    print(f"[PASS] Alle {len(data)} UI-Schlüssel besitzen vollständige de-, en- und es-Übersetzungen.")
    return True


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--check" in args:
        target = next((a for a in args if a != "--check"), ".")
        ok = check_translations(target)
        sys.exit(0 if ok else 1)
    target = args[0] if args else "."
    manage_translations(target)
