# RPX Pro - RolePlay Xtreme Professional Edition

Ein professionelles Rollenspiel-Kontrollzentrum für Pen & Paper Abenteuer. Offline-fähig, kostenlos, Open Source.

![RPX Pro Hauptfenster](README/screenshots/main.png)

**Repository:** https://github.com/entertain-and-more/rpx

## Features

| Feature | Beschreibung |
|---------|-------------|
| **Welten-System** | Multi-Map-Karten, Orte (Außen-/Innenansicht), Nationen, Völker, Trigger-Automatisierung |
| **Soundboard** | Multi-Backend Audio (Qt Multimedia, pygame, winsound) |
| **Lichteffekte** | Blitz, Stroboskop, Tag/Nacht-Zyklus, Farbfilter (konfigurierbar für Spieler-Bildschirm) |
| **Kampfsystem** | Waffen, Rüstungen, Magie, Kampftechniken, konfigurierbares Würfelsystem |
| **Spieler-Bildschirm** | Separater Monitor mit dynamischen Ansichten (Kacheln, Rotation, Bilder) |
| **Regelwerk-Import** | D&D 5e, DSA 5, Generisches Fantasy (oder eigene JSON-Templates) |
| **KI-Integration** | Promptgenerator mit 7 spezialisierten KI-Rollen |
| **CLI/API** | JSON-RPC CLI für LLM-Steuerung via stdin/stdout |
| **Web/PWA-Companion** | Liest lokale `rpx-campaign-bundle-v1`-ZIPs für Kampagnenübersicht, Charakterstatus, Missionen und Medienhinweise |
| **Session-Manager** | Missionen, Gruppen, Rundensteuerung |
| **Charaktere** | Attribute, Inventar-Dialog, Gold, Avatar, Hunger/Durst-Simulation |
| **Simulation** | Hunger/Durst-Timer, Zeitfortschritt, Naturkatastrophen |

## Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Starten
python RPX_Pro_1.py
# oder direkt:
python -m rpx_pro.app
```

Oder unter Windows: `START.bat` doppelklicken.

### Voraussetzungen

- Python 3.10+
- PySide6 (Qt6) - beinhaltet Qt Multimedia für Audio
- pygame (optional, Audio-Fallback)

## EXE-Build

```bash
build_exe.bat

# oder direkt
python -m PyInstaller --noconfirm --clean RPX_Pro.spec
```

Die Build-Ausgabe landet in `dist/RPX_Pro/`. Das Spec-File bindet die `rulesets/` mit ein; Laufzeitdaten bleiben weiterhin in `rpx_pro_data/`.
`build/`, `dist/`, `releases/` und `_WARTUNG/` sind lokale Build-/Staging-Verzeichnisse und werden nicht versioniert.

### Tests

```bash
python -m pytest -q
python -m compileall -q RPX_Pro_1.py manage_translations.py translator.py rpx_pro tests
node --test web_companion/tests/library.test.mjs
node --test web_companion/tests/pwa.test.mjs
```

## Schnellstart

1. **Welt erstellen**: Welt-Tab > "Neue Welt" > Name eingeben
2. **Karte hinterlegen**: Welt-Tab > "Karte laden..." > Bilddatei auswählen
3. **Orte anlegen**: Welt-Tab > "Ort hinzufügen" > mit "Bearbeiten" Bilder/Sound zuweisen
4. **Session starten**: Datei > Neue Session > Welt auswählen
5. **Charaktere erstellen**: Charaktere-Tab > "Charakter erstellen" > mit "Bearbeiten" Details setzen
6. **Spiel starten**: Toolbar > "Spiel starten" > KI-Prompt wird in die Zwischenablage kopiert

## Architektur

RPX Pro ist modular aufgebaut als Python-Package (`rpx_pro/`):

```
rpx_pro/
  app.py                 # Entry Point
  main_window.py         # Schlanker Orchestrator (~1200 Zeilen)
  constants.py           # Konfiguration, Pfade, Logging
  api.py                 # Programmatische Python-API (JSON-serialisierbar)
  cli.py                 # JSON-RPC CLI für LLM-Steuerung
  models/                # Datenmodelle (Dataclasses)
    enums.py             # MessageRole, PlayerScreenMode, DamageType, ...
    entities.py          # Character, Weapon, Armor, Spell, Item, ...
    world.py             # World, Location, WorldSettings
    session.py           # Session, ChatMessage, Mission
  managers/              # Geschäftslogik
    data_manager.py      # Persistenz (JSON-Dateien)
    audio_manager.py     # Multi-Backend Audio
    light_manager.py     # Lichteffekte (Overlay-basiert)
    prompt_generator.py  # KI-Prompt-Erzeugung
    dice_roller.py       # Würfelsystem
  widgets/               # Wiederverwendbare UI-Komponenten
    chat.py              # Chat-Widget mit Rollenauswahl
    soundboard.py        # Drag&Drop Soundboard
    player_screen.py     # Spieler-Bildschirm (2. Monitor)
    map_widget.py        # Interaktive Karte mit Zeichenwerkzeugen
    location_view.py     # Ortsansicht (Außen/Innen)
    inventory_dialog.py  # Charakter-Inventar-Dialog
    prompt_widget.py     # KI-Prompt-Generator Widget
    ruleset_importer.py  # Regelwerk-Import
  tabs/                  # Eigenständige Tab-Klassen
    views_tab.py         # Ansichten (Ort, Inventar, Ambiente, PlayerScreen)
    world_tab.py         # Weltverwaltung + Multi-Map
    characters_tab.py    # Charaktere + Inventar-Button
    combat_tab.py        # Kampf + Würfel
    missions_tab.py      # Missionen
    inventory_tab.py     # Welt-Item-Bibliothek
    immersion_tab.py     # Soundboard
    settings_tab.py      # Session-/Welt-Einstellungen
```

**Design-Prinzipien:**
- Tabs kommunizieren ausschließlich über Qt Signals (kein `self.window()`)
- Manager werden per Dependency Injection übergeben
- MainWindow ist reiner Orchestrator (verbindet Signals, routet Events)
- Models sind reine Dataclasses mit `to_dict()`/`from_dict()` Serialisierung

## Tab-Übersicht

### Chat (Tab 1)
- Nachrichten mit verschiedenen Rollen (Spieler, GM, KI-Rollen, Erzähler)
- Farbcodierung nach Rolle
- Chat-Befehle: `/roll`, `/heal`, `/damage`, `/check`, `/give`
- System-Events werden automatisch geloggt

### Ansichten (Tab 2)
Vier Sub-Tabs in einem:

- **Ortsansicht**: Außen-/Innenansicht mit Blackout-Übergang, Farbfilter, Trigger
- **Inventaransicht**: Charakter-Dropdown, Inventar-Tabelle (Name, Anzahl, Gewicht, Wert), Gold
- **Ambiente**: Lichteffekte (Blitz, Stroboskop, Tag/Nacht, Farbfilter) + Hintergrundmusik (Playlist, Lautstärke)
- **Spieler-Bildschirm**: Monitor-Auswahl, Vollbild, Anzeigemodus, Ansichten-Checkboxen, Effekt-Spiegelung

### Welt (Tab 3)
- Welten erstellen, bearbeiten, speichern
- **Multi-Map-System**: Mehrere Karten pro Welt (Weltkarte, Dungeons, Städte)
- Interaktive Karte mit Zeichenwerkzeugen
- Orte im Baum verwalten mit Bearbeiten-Dialog

### Charaktere (Tab 4)
- Tabelle aller Charaktere mit Kerndaten
- **Inventar-Button** pro Zeile -- öffnet den Inventar-Dialog mit Gold, Gewicht, Items
- Bearbeiten-Dialog: Name, Rasse, Beruf, Level, HP, Mana, Skills, NPC-Status, Bild, Biografie
- Schnelle HP/Mana-Steuerung (Schaden, Heilen, Mana)

### Kampf (Tab 5)
- Würfelsystem (1-10 Würfel, W4 bis W100)
- Angriffsmechanik mit Treffsicherheit, kritischen Treffern, Rüstung
- Waffen- und Zauberlisten

### Missionen (Tab 6)
- Aktive und abgeschlossene Missionen
- Abschließen oder als gescheitert markieren
- Status-Änderungen im Chat geloggt

### Inventar (Tab 7)
- Welt-Item-Bibliothek (Name, Klasse, Gewicht, Wert, Boni)
- Items an Orten mit Fundwahrscheinlichkeit
- NPCs an Orten mit Begegnungswahrscheinlichkeit

### Soundboard (Tab 8)
- Sound-Effekte per Drag&Drop oder Dialog hinzufügen
- Play/Stop pro Sound

### KI-Prompts (Tab 9)
- 7 KI-Rollen: Storyteller, Plottwist, Spielleiter, Gegner, NPCs, Landschaft, Fauna/Flora
- Spielstart-Prompt und Update-Prompt generieren
- In Zwischenablage kopieren

### Einstellungen (Tab 10)
- Session: Rundenmodus, Aktionen/Runde, Spielleiter (Mensch/KI)
- Welt: Zeitverhältnis, Stunden/Tag, Hunger/Durst-Simulation, Naturkatastrophen

## Spieler-Bildschirm (2. Monitor)

Der GM kann einen separaten Bildschirm für Spieler öffnen (Ansichten > Spieler-Bildschirm):

- **4 Anzeigemodi**: Bild, Karte, Rotation, Kacheln
- **Dynamische Ansichten**: Per Checkbox wählbar welche Kacheln aktiv sind
  - Charaktere (Helden-Übersicht mit HP/Mana-Balken)
  - Missionen (aktive Quests)
  - Karte (Weltkarte mit Markierungen)
  - Chat (Spielverlauf)
  - Rundensteuerung (Runde/Zugreihenfolge)
  - Ortsansicht (aktueller Ort)
  - Inventar (Charakter-Inventar)
- **Rotation**: Nur aktivierte Ansichten werden durchrotiert
- **Event-Overlay**: Ankündigungen bei Schaden, Heilung, Tod, Missionen, Runden
- **Effekt-Spiegelung**: Blitz, Tag/Nacht, Farbfilter einzeln steuerbar
- Monitor-Auswahl, Vollbild, Schwarzbild

## CLI / API für LLM-Integration

RPX Pro bietet eine programmatische API und ein CLI-Interface für KI-Steuerung:

```bash
# Mit CLI starten
python -m rpx_pro.app --cli
```

**JSON-RPC Protokoll** via stdin/stdout:

```json
{"id": 1, "method": "roll_dice", "params": {"count": 2, "sides": 20}}
{"id": 1, "result": {"dice": "2W20", "rolls": [14, 7], "total": 21}}
```

**Verfügbare Methoden:**
`create_world`, `list_worlds`, `load_world`, `create_session`, `list_sessions`, `load_session`,
`create_character`, `get_character`, `heal_character`, `damage_character`, `get_inventory`, `give_item`,
`send_chat_message`, `get_chat_history`, `roll_dice`, `create_mission`, `complete_mission`,
`generate_start_prompt`, `generate_context_update`, `export_campaign_bundle`, `import_campaign_bundle`

Für plattformübergreifenden Datenaustausch erzeugt `export_campaign_bundle` ein ZIP-Bundle im Format
`rpx-campaign-bundle-v1` mit `manifest.json`, Welten, Sessions, Regelwerken und optionalen Medien.
`import_campaign_bundle` liest dieses Format wieder ein, normalisiert Medienpfade für den Desktop
und unterstützt Konfliktstrategien für bestehende Welten, Sessions und Regelwerke.

## Web/PWA-Companion

Unter `web_companion/` liegt jetzt ein statischer Offline-Companion für dasselbe Bundle-Format.
Er lädt lokale ZIP-Dateien per Dateiauswahl oder Drag-and-drop und zeigt:

- Kampagnenübersicht mit Exportzeit und Bundle-Statistiken
- Welten, Karten und Orts-Hinweise
- Session-Ansichten mit Charakterstatus, Missionen und letzten Chat-Zeilen
- Regelwerke sowie Medienreferenzen aus `media/manifest.json`

Start lokal:

```bash
cd web_companion
python -m http.server 8765
```
Details stehen in [EXPORTFORMAT.md](EXPORTFORMAT.md).

## Simulation

### Hunger/Durst
- Steigen proportional zur Spielzeit, Warnungen bei 50% und 75%
- Rate pro Spielstunde konfigurierbar, Rassen-Modifikatoren möglich

### Naturkatastrophen
- Zufallsereignisse: Erdbeben, Überschwemmung, Vulkanausbruch, Tornado, etc.
- Visueller Stroboskop-Effekt + Chat-Nachricht

### Zeitfortschritt
- Spielzeit läuft proportional zur Echtzeit (Verhältnis konfigurierbar)
- Tageswechsel-Benachrichtigungen, Tageszeit auf Spieler-Bildschirm

## Regelwerk-Import

Drei mitgelieferte Templates:

- **D&D 5e (SRD)** - 9 Rassen, 19 Waffen, 12 Rüstungen, 14 Zauber
- **DSA 5 (Abstrahiert)** - 12 Völker, 15 Waffen, 7 Rüstungen, 12 Zauber
- **Generisches Fantasy** - 5 Rassen, 10 Waffen, 5 Rüstungen, 10 Zauber

Eigene Regelwerke als JSON importierbar (`Datei > Regelwerk importieren`).

## Datenstruktur

```
rpx_pro_data/
  config.json          # Globale Einstellungen
  worlds/              # Welt-JSONs (Orte, Waffen, Rassen, etc.)
  sessions/            # Session-JSONs (Charaktere, Missionen, Chat)
  media/
    sounds/            # Sound-Effekte (.mp3, .wav, .ogg)
    music/             # Hintergrundmusik
    images/            # Orts-/Charakter-Bilder
    maps/              # Weltkarten
  backups/             # Auto-Backups
```

## Datenschutz und lokale Daten

RPX Pro arbeitet lokal. Spielwelten, Sessions, Medien, Konfigurationen und Backups bleiben in `rpx_pro_data/` auf dem Gerät und sind über `.gitignore` vom Repository ausgeschlossen. Die KI-Integration erzeugt Prompts zur Weiterverwendung in einem externen Tool; RPX Pro überträgt diese Inhalte nicht selbst an externe Dienste.

## Tastenkürzel

| Kürzel | Aktion |
|---------|--------|
| Ctrl+N | Neue Session |
| Ctrl+O | Session laden |
| Ctrl+S | Session speichern |

## Markt-Vergleich

| Feature | RPX Pro | Roll20 | Foundry VTT | Fantasy Grounds |
|---------|:-------:|:------:|:-----------:|:---------------:|
| Offline-fähig | x | - | x | x |
| Lichteffekte | x | - | ~ | - |
| KI-Integration | x | - | ~ | - |
| LLM-API/CLI | x | - | - | - |
| Hunger-Simulation | x | - | - | - |
| Naturkatastrophen | x | - | - | - |
| 2. Monitor (dynamisch) | x | - | ~ | ~ |
| Modular/Erweiterbar | x | - | x | - |
| Kostenlos | x | ~ | - | - |
| Open Source | x | - | - | - |

## Lizenz

MIT License - siehe [LICENSE](LICENSE).

RPX Pro ist freie Software unter der MIT-Lizenz. Du kannst es frei verwenden, modifizieren und weitergeben, auch für kommerzielle Projekte.

Die Regelwerk-Templates enthalten nur generische Spielmechaniken. D&D-Inhalte basieren auf dem SRD 5.1 (OGL). DSA-Inhalte sind abstrahiert und enthalten keine geschützten Texte.

---

## English

A professional role-playing game control center with world systems, soundboard, and AI integration.

### Features

- World/campaign management
- Character sheets
- Integrated soundboard
- AI-powered storytelling
- Map viewer

### Installation

```bash
git clone https://github.com/entertain-and-more/rpx.git
cd rpx
pip install -r requirements.txt
python "RPX_Pro_1.py"
```

### License

See [LICENSE](LICENSE) for details.

---

## Haftung / Liability

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gilt der Haftungsausschluss der MIT-Lizenz.

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed. The MIT License disclaimer also applies.
