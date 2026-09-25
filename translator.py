"""
TranslationSystem - Multi-Language Support fuer Anwendungen
============================================================
Version: 2.0.0 (Tier-2 Curated Expansion)
Quelle: ARC_EntwicklungsschleifeAdvanced/TranslationSystem.py

Verwendung:
-----------
from translator import TranslationSystem, get_translator, t

translator = get_translator('de')
label.setText(translator.t('Datei oeffnen'))
translator.set_language('es')
"""

import contextlib
import json
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

LANGUAGE_SLOTS = ("de", "en", "es", "zh-Hans", "ja", "ru")
SUPPORTED_LANGUAGES = LANGUAGE_SLOTS

LANGUAGE_DISPLAY_NAMES = {
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "zh-Hans": "简体中文",
    "ja": "日本語",
    "ru": "Русский",
}

# Kuratierte spanische UI-Uebersetzungen fuer TTRPG- und Pen-&-Paper-Begriffe.
# Regelwerk-, Kampagnen- und Charakterinhalte duerfen NIEMALS implizit uebersetzt werden.
SPANISH_UI_TRANSLATIONS = {
    "Abbrechen": "Cancelar",
    "Abschließen": "Completar",
    "Abschliessen": "Completar",
    "Ablegen": "Soltar",
    "Abspielen": "Reproducir",
    "Aktionen: 0/Unbegrenzt": "Acciones: 0/Ilimitadas",
    "Aktive Missionen": "Misiones activas",
    "Aktive Welt:": "Mundo activo:",
    "Aktuell: -": "Actual: -",
    "Ambiente": "Ambiente",
    "An Charakter geben...": "Dar a personaje...",
    "Angreifer:": "Atacante:",
    "Angriff würfeln!": "¡Tirar ataque!",
    "Ansichten": "Vistas",
    "Anzahl:": "Cantidad:",
    "Bearbeiten": "Editar",
    "Betreten": "Entrar",
    "Bild": "Imagen",
    "Bild laden...": "Cargar imagen...",
    "Bitte auswählen:": "Por favor seleccione:",
    "Bitte Regelwerk auswählen": "Por favor seleccione reglamento",
    "Blitz": "Rayo",
    "Charakter:": "Personaje:",
    "Charaktere": "Personajes",
    "Charaktername": "Nombre del personaje",
    "Chat": "Chat",
    "Details anzeigen": "Mostrar detalles",
    "Einstellungen": "Configuración",
    "Element löschen": "Eliminar elemento",
    "Entfernen": "Quitar",
    "Ergebnis: -": "Resultado: -",
    "Fehler beim Laden": "Error al cargar",
    "Filter anwenden": "Aplicar filtro",
    "Filter entfernen": "Quitar filtro",
    "Fähigkeiten definieren": "Definir habilidades",
    "Fähigkeiten definieren...": "Definir habilidades...",
    "Generieren": "Generar",
    "Generierter Prompt:": "Prompt generado:",
    "Gesamtgewicht: 0.0": "Peso total: 0.0",
    "Gescheitert": "Fallido",
    "Gold:": "Oro:",
    "Gold: 0": "Oro: 0",
    "HP": "PV",
    "Haupt-Toolbar": "Barra de herramientas principal",
    "Heilen": "Curar",
    "Helden": "Héroes",
    "Hilfe": "Ayuda",
    "Hintergrund...": "Fondo...",
    "Hinzufügen": "Añadir",
    "In Zwischenablage": "Al portapapeles",
    "Info/Preisliste": "Información/Lista de precios",
    "Inventar": "Inventario",
    "Inventaransicht": "Vista de inventario",
    "Item hier platzieren...": "Colocar objeto aquí...",
    "KI-Aufträge & Rollen": "Tareas y roles de IA",
    "KI-Promptgenerator": "Generador de prompts de IA",
    "KI-Prompts": "Prompts de IA",
    "Kacheln": "Casillas",
    "Kampf": "Combate",
    "Karte": "Mapa",
    "Karte:": "Mapa:",
    "Kein Bild": "Sin imagen",
    "Kein Bild verfügbar": "Sin imagen disponible",
    "Kein Hintergrund": "Sin fondo",
    "Kein Ort ausgewählt": "Ningún lugar seleccionado",
    "Keine Ansichten aktiviert": "No hay vistas activadas",
    "Keine Karte hinterlegt": "Sin mapa disponible",
    "Keine aktiven Missionen": "No hay misiones activas",
    "Lautstärke:": "Volumen:",
    "Letzte Session wiederhergestellt: {session.name}": "Última sesión restaurada: {session.name}",
    "Löschen": "Eliminar",
    "MP": "PM",
    "Mana abziehen": "Deducir maná",
    "Mana auffüllen": "Rellenar maná",
    "Missionen": "Misiones",
    "Monitor:": "Monitor:",
    "NPC hier platzieren...": "Colocar PNJ aquí...",
    "Nacht-Modus": "Modo noche",
    "Name:": "Nombre:",
    "Nächste Runde": "Siguiente ronda",
    "Ort:": "Lugar:",
    "Ort: -": "Lugar: -",
    "Ortsansicht": "Vista de lugar",
    "RPX": "RPX",
    "RPX - Spieler-Ansicht": "RPX - Vista del jugador",
    "Rasse | Beruf": "Raza | Clase",
    "Regel hinzufügen": "Añadir regla",
    "Regel löschen": "Eliminar regla",
    "Regelwerk importieren": "Importar reglamento",
    "Rolle:": "Rol:",
    "Rotation": "Rotación",
    "Runde: -": "Ronda: -",
    "Runde: 1": "Ronda: 1",
    "Rundensteuerung": "Control de rondas",
    "Schaden": "Daño",
    "Schließen": "Cerrar",
    "Schliessen": "Cerrar",
    "Schwarzbild": "Pantalla negra",
    "Seiten:": "Caras:",
    "Senden": "Enviar",
    "Sound entfernen": "Quitar sonido",
    "Sound hinzufügen": "Añadir sonido",
    "Soundboard": "Tabla de sonidos",
    "Speichern": "Guardar",
    "Spieler-Bildschirm": "Pantalla del jugador",
    "Spieler-Bildschirm öffnen": "Abrir pantalla del jugador",
    "Spieler-Bildschirm schließen": "Cerrar pantalla del jugador",
    "Spieler: -": "Jugador: -",
    "Spielstart-Prompt": "Prompt de inicio de partida",
    "Spielverlauf": "Registro de juego",
    "Stopp": "Detener",
    "Stroboskop": "Estroboscopio",
    "Tag-Modus": "Modo día",
    "Typ:": "Tipo:",
    "Umbenennen": "Renombrar",
    "Update-Prompt": "Actualizar prompt",
    "Verlassen": "Salir",
    "Verteidiger:": "Defensor:",
    "Völker": "Razas",
    "Waffe erstellen": "Crear arma",
    "Waffe erstellen...": "Crear arma...",
    "Welt": "Mundo",
    "Welt speichern": "Guardar mundo",
    "Welteinstellungen": "Configuración del mundo",
    "Würfel": "Dados",
    "Würfeln": "Tirar dados",
    "Würfeln!": "¡Tirar dados!",
    "Zeile löschen": "Eliminar línea",
    "Zug beenden": "Terminar turno",
    "+ Charakter erstellen": "+ Crear personaje",
    "+ Karte": "+ Mapa",
    "+ Mission hinzufügen": "+ Añadir misión",
    "+ Neue Welt": "+ Nuevo mundo",
    "+ Ort hinzufügen": "+ Añadir lugar",
    "+ Waffe hinzufügen": "+ Añadir arma",
    "+ Zauber hinzufügen": "+ Añadir hechizo",
    "▶ Ausführen → Spielverlauf": "▶ Ejecutar → Registro de juego",
    "▶ Nächster Zug": "▶ Siguiente turno",
    "▶ Start (Loop)": "▶ Iniciar (bucle)",
    "✅ Abschließen": "✅ Completar",
    "✏️ Bearbeiten": "✏️ Editar",
    "✓ Abschließen": "✓ Completar",
    "✖ Filter löschen": "✖ Borrar filtro",
    "❌ Abbrechen": "❌ Cancelar",
    "➕ Hinzufügen": "➕ Añadir",
    "➕ Mission hinzufügen": "➕ Añadir misión",
    "➕ Ort hinzufügen": "➕ Añadir lugar",
    "➕ Sound hinzufügen": "➕ Añadir sonido",
    "➕ Waffe hinzufügen": "➕ Añadir arma",
    "➕ Zauber hinzufügen": "➕ Añadir hechizo",
    "🎨 Farbfilter wählen": "🎨 Elegir filtro de color",
    "🎬 Start-Prompt generieren": "🎬 Generar prompt de inicio",
    "🎲 Regeln & Würfel": "🎲 Reglas y dados",
    "🎲 Würfeln!": "🎲 ¡Tirar dados!",
    "🏞 Außen": "🏞 Exterior",
    "🏞️\nKein Bild verfügbar": "🏞️\nSin imagen disponible",
    "🏞️\nKein Ort ausgewählt": "🏞️\nNingún lugar seleccionado",
    "💾 Chat exportieren": "💾 Exportar chat",
    "💾 Speichern": "💾 Guardar",
    "💾 Welt speichern": "💾 Guardar mundo",
    "📊 Details anzeigen": "📊 Mostrar detalles",
    "📋 Spielstart → Clipboard": "📋 Inicio de partida → Portapapeles",
    "📥 Zu Session hinzufügen": "📥 Añadir a sesión",
    "🔄 Runde zurücksetzen": "🔄 Reiniciar ronda",
    "🔲 Effekte löschen": "🔲 Borrar efectos",
    "🔴 Rot-Filter": "🔴 Filtro rojo",
    "🔵 Blau-Filter": "🔵 Filtro azul",
    "🗑 Löschen": "🗑 Eliminar",
    "🗑️ Löschen": "🗑️ Eliminar",
    "🗺 Weltkarte laden": "🗺 Cargar mapa mundial",
    "🚀 Spielstart-Prompt": "🚀 Prompt de inicio de partida",
}


class TranslationSystem:
    """Multi-Language Support System v2.0 mit Tier-2 Curated Expansion."""

    def __init__(self, default_lang: str = "de", app_dir: Optional[Path] = None):
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

        self._callbacks: List[Callable[[str], None]] = []
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self):
        if self.translations_file.exists():
            try:
                with open(self.translations_file, "r", encoding="utf-8") as f:
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
        """Hält alle sechs Zielsprachenslots konsistent."""
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
        with open(self.translations_file, "w", encoding="utf-8") as f:
            json.dump(self.translations, f, indent=2, ensure_ascii=False)

    def t(self, key: str) -> str:
        """
        Übersetzt einen Schlüssel in die aktive Sprache mit deterministischer
        Fallback-Kette (target -> es (curated) -> en -> de -> key).
        """
        if not key:
            return key

        if key in self.translations:
            entry = self._with_language_slots(self.translations[key])
            self.translations[key] = entry

            translated = entry.get(self.current_lang, "")
            if translated:
                return translated

            if self.current_lang == "es":
                curated = SPANISH_UI_TRANSLATIONS.get(key) or SPANISH_UI_TRANSLATIONS.get(entry.get("de", key))
                if curated:
                    return curated

            return entry.get("en") or entry.get("de") or key

        # Key nicht im geladenen Katalog -> Curated fallback wenn Spanisch
        if self.current_lang == "es" and key in SPANISH_UI_TRANSLATIONS:
            return SPANISH_UI_TRANSLATIONS[key]

        return key

    def translate_ui(self, key: str) -> str:
        """Übersetzt ausschließlich einen festen UI-Schlüssel."""
        return self.t(key)

    @staticmethod
    def translate_content(text: str) -> str:
        """
        Gibt nutzergeführten Regelwerk-, Kampagnen-, Lore- oder Chat-Inhalt
        strikt unverändert zurück (TW-RPG-11: Trennung von UI und Inhalt).
        """
        return text

    def set_language(self, lang: str) -> bool:
        if lang in LANGUAGE_SLOTS:
            self.current_lang = lang
            for cb in self._callbacks:
                with contextlib.suppress(Exception):
                    cb(lang)
            return True
        return False

    def get_language(self) -> str:
        return self.current_lang

    def register_language_changed_callback(self, cb: Callable[[str], None]):
        """Registriert einen Listener für Sprachänderungen."""
        if cb not in self._callbacks:
            self._callbacks.append(cb)

    @staticmethod
    def get_supported_languages() -> tuple:
        return LANGUAGE_SLOTS

    @staticmethod
    def get_language_display_names() -> Dict[str, str]:
        return dict(LANGUAGE_DISPLAY_NAMES)

    def add_translation(self, key: str, de: str, en: str, **additional):
        """Fügt einen UI-Schlüssel hinzu."""
        unknown = set(additional) - set(LANGUAGE_SLOTS)
        if unknown:
            raise ValueError(f"Unsupported language slots: {sorted(unknown)}")
        self.translations[key] = self._with_language_slots(
            {"de": de, "en": en, **additional}
        )
        self._save_translations()

    def scan_and_update(self, project_dir: Optional[Path] = None) -> Dict:
        """Scannt Projektdateien und ergänzt neue deutsche Strings."""
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
        return {"added": added, "missing": missing, "total": len(self.translations)}

    def _find_german_strings(self, directory: Path) -> Set[str]:
        german_strings = set()
        skip_dirs = {"build", "dist", "venv", ".venv", "__pycache__", "releases"}

        for py_file in directory.rglob("*.py"):
            if any(folder in py_file.parts for folder in skip_dirs):
                continue
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            for pattern in self.string_patterns:
                for match in pattern.findall(content):
                    if match and self._is_german(match):
                        german_strings.add(match.strip())

        return german_strings

    def _is_german(self, text: str) -> bool:
        if any(ch in text for ch in "äöüÄÖÜß"):
            return True
        text_lower = text.lower()
        return any(hint in text_lower for hint in self.german_hints)


# Globaler Singleton-Zugriff
_GLOBAL_TRANSLATOR: Optional[TranslationSystem] = None


def get_translator(default_lang: str = "de", app_dir: Optional[Path] = None) -> TranslationSystem:
    global _GLOBAL_TRANSLATOR
    if _GLOBAL_TRANSLATOR is None:
        _GLOBAL_TRANSLATOR = TranslationSystem(default_lang=default_lang, app_dir=app_dir)
    return _GLOBAL_TRANSLATOR


def t(key: str) -> str:
    """Globaler Übersetzungs-Shortcut."""
    return get_translator().t(key)
