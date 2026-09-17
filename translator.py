"""
TranslationSystem - Multi-Language Support fuer Anwendungen
============================================================
Version: 1.0.0 (isoliert aus _LANG)
Quelle: ARC_EntwicklungsschleifeAdvanced/TranslationSystem.py v2.4

Verwendung:
-----------
from translator import TranslationSystem

translator = TranslationSystem('de')
label.setText(translator.t('Datei oeffnen'))
translator.set_language('en')
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set


LANGUAGE_SLOTS = ("de", "en", "es", "zh-Hans", "ja", "ru")
SUPPORTED_LANGUAGES = LANGUAGE_SLOTS

# Curated UI copy is deliberately small and explicit. Rulebook, campaign and
# character text must never be translated implicitly.
SPANISH_UI_TRANSLATIONS = {
    "Abbrechen": "Cancelar",
    "Abschließen": "Completar",
    "Bearbeiten": "Editar",
    "Fehler beim Laden": "Error al cargar",
    "Filter anwenden": "Aplicar filtro",
    "Filter entfernen": "Quitar filtro",
    "Keine Ansichten aktiviert": "No hay vistas activadas",
    "Lautstärke:": "Volumen:",
    "Löschen": "Eliminar",
    "Regelwerk importieren": "Importar reglamento",
    "Schließen": "Cerrar",
    "Welt speichern": "Guardar mundo",
    "Welteinstellungen": "Configuración del mundo",
    "Würfeln": "Tirar dados",
}


class TranslationSystem:
    """Multi-Language Support System v1.0"""

    def __init__(self, default_lang: str = 'de', app_dir: Path = None):
        """
        Initialisiert Translation-System.

        Args:
            default_lang: Standard-Sprache aus ``LANGUAGE_SLOTS``
            app_dir: Verzeichnis der Anwendung (default: aktuelles Verzeichnis)
        """
        self.current_lang = default_lang if default_lang in LANGUAGE_SLOTS else "de"

        if app_dir is None:
            app_dir = Path.cwd()
        self.app_dir = Path(app_dir)

        self.translations_file = self.app_dir / "locales" / "translations.json"

        self.string_patterns = [
            re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addTab\s*\([^,]+,\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'text\s*=\s*"([^"]+)"'),
        ]

        self.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "oeffnen", "speichern",
            "schliessen", "einstellungen", "abbrechen", "ok", "ja", "nein",
            "start", "stop", "pause", "fortsetzen", "laden", "aktualisieren",
            "filter", "fehler", "export", "import", "optionen", "anzeigen",
        ]

        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        if self.translations_file.exists():
            try:
                with open(self.translations_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                if not isinstance(loaded, dict):
                    raise ValueError("Translations must be a JSON object")
                self.translations = {
                    key: self._with_language_slots(value)
                    for key, value in loaded.items()
                }
            except Exception:
                self.translations = {}
        else:
            self.translations = {}

    @staticmethod
    def _with_language_slots(entry: dict) -> dict:
        """Hält alte DE/EN-Kataloge mit allen geplanten Slots kompatibel."""
        normalized = dict(entry) if isinstance(entry, dict) else {}
        for language in LANGUAGE_SLOTS:
            normalized.setdefault(language, "")
        return normalized

    def _save_translations(self):
        self.translations_file.parent.mkdir(parents=True, exist_ok=True)
        self.translations = {
            key: self._with_language_slots(value)
            for key, value in self.translations.items()
        }
        with open(self.translations_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations, f, indent=2, ensure_ascii=False)

    def t(self, key: str) -> str:
        """
        Uebersetzt einen Key in die aktuelle Sprache.

        Args:
            key: Translation-Key (oft der deutsche Originaltext)

        Returns:
            Uebersetzter Text oder Key als Fallback
        """
        if key in self.translations:
            entry = self._with_language_slots(self.translations[key])
            self.translations[key] = entry
            translated = entry.get(self.current_lang, "")
            if translated:
                return translated
            if self.current_lang == "es":
                curated = SPANISH_UI_TRANSLATIONS.get(entry.get("de", key))
                if curated:
                    return curated
            return entry.get("en") or entry.get("de") or key

        if self._is_german(key):
            self.translations[key] = self._with_language_slots({"de": key})
            self._save_translations()

        return key

    def set_language(self, lang: str):
        if lang in LANGUAGE_SLOTS:
            self.current_lang = lang
            return True
        return False

    def get_language(self) -> str:
        return self.current_lang

    def add_translation(self, key: str, de: str, en: str, **additional):
        """Fügt UI-Text hinzu; Kampagneninhalt bleibt außerhalb dieses Katalogs."""
        unknown = set(additional) - set(LANGUAGE_SLOTS)
        if unknown:
            raise ValueError(f"Unsupported language slots: {sorted(unknown)}")
        self.translations[key] = self._with_language_slots(
            {"de": de, "en": en, **additional}
        )
        self._save_translations()

    def translate_ui(self, key: str) -> str:
        """Übersetzt ausschließlich einen festen UI-Schlüssel."""
        return self.t(key)

    @staticmethod
    def translate_content(text: str) -> str:
        """Gibt nutzergeführten Regelwerk-/Kampagneninhalt unverändert zurück."""
        return text

    def scan_and_update(self, project_dir: Path = None) -> Dict:
        """Scannt Projekt-Dateien nach deutschen Strings und aktualisiert translations.json."""
        if project_dir is None:
            project_dir = self.app_dir

        found_strings = self._find_german_strings(project_dir)

        added = []
        for string in sorted(found_strings):
            if string not in self.translations:
                self.translations[string] = self._with_language_slots({"de": string})
                added.append(string)

        if added:
            self._save_translations()

        missing = [k for k, v in self.translations.items() if not v.get("en")]

        return {'added': added, 'missing': missing, 'total': len(self.translations)}

    def _find_german_strings(self, directory: Path) -> Set[str]:
        german_strings = set()
        skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases'}

        for py_file in directory.rglob("*.py"):
            if any(folder in py_file.parts for folder in skip_dirs):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            for pattern in self.string_patterns:
                for match in pattern.findall(content):
                    if match and self._is_german(match):
                        german_strings.add(match.strip())

        return german_strings

    def _is_german(self, text: str) -> bool:
        if any(ch in text for ch in "aeoeueAeOeUess"):
            return True
        text_lower = text.lower()
        return any(hint in text_lower for hint in self.german_hints)

    def get_missing_translations(self, language: str = "en") -> List[str]:
        if language not in LANGUAGE_SLOTS:
            raise ValueError(f"Unsupported language slot: {language}")
        return [
            key for key, value in self.translations.items()
            if not self._with_language_slots(value).get(language)
        ]


if __name__ == "__main__":
    tr = TranslationSystem('de')
    print(f"Sprache: {tr.get_language()}")
    result = tr.scan_and_update()
    print(f"Scan: {result['total']} Strings, {len(result['added'])} neu, {len(result['missing'])} ohne EN")
