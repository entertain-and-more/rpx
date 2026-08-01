<img src="assets/banner.svg" width="100%" alt="RPX Pro — RolePlay Xtreme Professional Edition" />

# RPX Pro — RolePlay Xtreme Professional Edition

[English](README.md) | [Deutsch](README_de.md)

> Professionelles Rollenspiel-Kontrollzentrum für Pen & Paper Tabletop-Abenteuer. Offline-fähig, kostenlos und Open Source.

[![Pytest](https://img.shields.io/badge/Pytest-14%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![Web Companion](https://img.shields.io/badge/Web%20Companion-17%20passed-brightgreen.svg)](web_companion/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-blue.svg)](https://www.qt.io/)
[![License](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Plattform-Windows-lightgrey.svg)](https://github.com/entertain-and-more/rpx)
[![Datenschutz](https://img.shields.io/badge/Datenschutz-Local--First%20%2F%20Offline-success.svg)](#datenschutz--lokale-daten)
[![LLM Bereit](https://img.shields.io/badge/LLM-Bereit%20%2F%20JSON--RPC-purple.svg)](#cli--api-f%C3%BCr-llm-integration)

> [!NOTE]
> **Local-First & Maschinenlesbare Architektur**: RPX Pro läuft zu 100% offline. Alle Kampagnendaten, Karten, Audiodateien und Regelwerke verbleiben lokal in `rpx_pro_data/`. Für KI-Agenten und externe LLM-Workflows bietet RPX Pro eine abhaengigkeitsfreie JSON-RPC CLI (`python -m rpx_pro.app --cli`) über `stdin`/`stdout` sowie standardisierte `rpx-campaign-bundle-v1` ZIP-Exporte für den offline PWA-Companion in `web_companion/`.

![RPX Pro Hauptfenster](README/screenshots/main.png)

## Für wen ist RPX Pro gedacht?

| Anforderung | Vorteil von RPX Pro |
|-------------|---------------------|
| Pen & Paper Runden vom eigenen Desktop aus leiten | Welten, Karten, Orte, Charaktere, Missionen, Ambiente, Kampf und Notizen in einem lokalen Arbeitsbereich |
| Spielern einen eigenen Tisch-Bildschirm bieten | Der Spieler-Bildschirm (2. Monitor) zeigt Karten, Orte, Gruppenstatus, Missionen, Chat und Event-Overlays |
| KI nutzen ohne Kampagnendaten an gehostete VTTs zu geben | RPX Pro generiert strukturierte Prompts und bietet eine JSON-RPC CLI/API; das externe KI-Tool bleibt optional |
| Kampagnen auf Smartphone oder Tablet mitnehmen | Der statische Web/PWA-Companion liest lokale `rpx-campaign-bundle-v1` ZIP-Exporte offline |
| Architektur einer PySide6 Game-Master App studieren | Modular aufgebaut mit Dataclass-Modellen, Manager-Injektion, Qt-Signalen und testbarer API/CLI-Schicht |

Suchbegriffe: `Tabletop RPG Kontrollzentrum`, `Offline Spielleiter Tools`, `PySide6 Pen and Paper Manager`, `Virtual Tabletop Companion`, `JSON-RPC LLM Spielleiter API`, `rpx-campaign-bundle-v1`.

## Features

| Feature | Beschreibung |
|---------|-------------|
| **Welten-System** | Multi-Map-Karten, Orte (Außen-/Innenansicht), Nationen, Völker, Trigger-Automatisierung |
| **Soundboard** | Multi-Backend Audio (Qt Multimedia, pygame, winsound) |
| **Lichteffekte** | Blitz, Stroboskop, Tag/Nacht-Zyklus, Farbfilter (konfigurierbar für Spieler-Bildschirm) |
| **Kampfsystem** | Waffen, Rüstungen, Magie, Kampftechniken, konfigurierbares Würfelsystem |
| **Spieler-Bildschirm** | Separater Monitor mit dynamischen Ansichten (Kacheln, Rotation, Bilder) |
| **Regelwerk-Import** | D&D 5e, DSA 5, Generisches Fantasy — oder eigene JSON-Templates |
| **KI-Integration** | Promptgenerator mit 7 spezialisierten KI-Rollen |
| **CLI / API** | JSON-RPC CLI für LLM-Steuerung via stdin/stdout |
| **Web/PWA Companion** | Liest lokale `rpx-campaign-bundle-v1` ZIPs für Kampagnenübersicht, Charakterstatus, Missionen und Medienhinweise |
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

Unter Windows: `START.bat` doppelklicken.

### Voraussetzungen

- Python 3.10+
- PySide6 (Qt6) — inklusive Qt Multimedia für Audio
- pygame (optionaler Audio-Fallback)

## EXE Build

```bash
build_exe.bat

# oder direkt
python -m PyInstaller --noconfirm --clean RPX_Pro.spec
```

Die erstellte Anwendung landet in `dist/RPX_Pro/`. Die Spec-Datei bindet `rulesets/` ein; Laufzeitdaten verbleiben in `rpx_pro_data/`.

## Tests

```bash
pytest
pytest tests/test_source_platform_smoke.py
python -m compileall -q RPX_Pro_1.py manage_translations.py translator.py rpx_pro tests
python generate_store_screenshots.py
node --test web_companion/tests/*.mjs
```

Für macOS-/Linux-Source-Smokes siehe [SOURCE_SMOKE_TEST.md](SOURCE_SMOKE_TEST.md).

## Schnellstart

1. **Welt erstellen**: Welt-Tab > "Neue Welt" > Name eingeben
2. **Karte hinterlegen**: Welt-Tab > "Karte laden..." > Bilddatei auswählen
3. **Orte anlegen**: Welt-Tab > "Ort hinzufügen" > mit "Bearbeiten" Bilder/Sound zuweisen
4. **Session starten**: Datei > Neue Session > Welt auswählen
5. **Charaktere erstellen**: Charaktere-Tab > "Charakter erstellen" > mit "Bearbeiten" Details setzen
6. **Spiel starten**: Toolbar > "Spiel starten" — KI-Prompt wird in die Zwischenablage kopiert

## Systemarchitektur

```mermaid
graph TD
    subgraph Desktop App [RPX Pro - PySide6 Desktop GUI]
        WM[World & Map System]
        SB[Multi-Backend Soundboard]
        FX[Light & Event Effects]
        CE[Combat & Dice Engine]
        AI[AI Prompt Generator]
        PM[Player Screen Manager]
    end

    subgraph Programmatic Interfaces
        CLI[JSON-RPC CLI Interface]
        API[RPXProAPI Dataclass Contract]
    end

    subgraph Data & Storage
        ZIP[rpx-campaign-bundle-v1 ZIP Export]
        DATA[Local Disk Storage / rpx_pro_data]
    end

    subgraph Mobile & Offline
        PWA[Web PWA Companion App]
        SW[Service Worker Cache]
    end

    WM --> DATA
    CE --> DATA
    Desktop App <--> API
    API <--> CLI
    CLI <-->|stdin/stdout| ExternalAI[External LLM / AI Agents]
    Desktop App -->|Export| ZIP
    ZIP -->|Import| PWA
    PWA <--> SW
    PM -->|Second Monitor| PlayerDisplay[Player Display Output]
```

## Tab-Übersicht

- **Chat (Tab 1):** Nachrichten mit verschiedenen Rollen (Spieler, SL, KI-Rollen), Farbcodierung, Befehle (`/roll`, `/heal`, `/damage`, `/check`, `/give`).
- **Ansichten (Tab 2):** Ortsansicht, Inventaransicht, Ambiente (Lichteffekte + Musik), Spieler-Bildschirm-Steuerung.
- **Welt (Tab 3):** Welten verwalten, Multi-Map-System, interaktive Karte, Ortsbaum.
- **Charaktere (Tab 4):** Charaktertabelle, Inventar-Button, Bearbeiten-Dialog, HP/Mana-Schnellsteuerung.
- **Kampf (Tab 5):** Würfelsystem (W4–W100), Angriffsmechanik, Waffen- und Zauberlisten.
- **Missionen (Tab 6):** Aktive und abgeschlossene Missionen, Status-Log im Chat.
- **Inventar (Tab 7):** Welt-Item-Bibliothek, Items und NPCs an Orten mit Wahrscheinlichkeiten.
- **Soundboard (Tab 8):** Sound-Effekte per Drag&Drop, Play/Stop pro Sound.
- **KI-Prompts (Tab 9):** 7 KI-Rollen, Spielstart- und Update-Prompt generieren und kopieren.
- **Einstellungen (Tab 10):** Session- und Welt-Parameter (Zeit, Simulation, Spielleiter-Typ).

## Spieler-Bildschirm (2. Monitor)

Der Spielleiter kann einen separaten Bildschirm für die Spieler öffnen (Ansichten > Spieler-Bildschirm):

- **4 Anzeige-Modi**: Bild, Karte, Rotation, Kacheln
- **Dynamische Kacheln**: Sichtbarkeit von Helden-Status, Missionen, Karte, Chat und Rundensteuerung
- **Effekt-Spiegelung**: Blitz, Tag/Nacht und Farbfilter separat zuschaltbar

## CLI / API für LLM-Integration

RPX Pro bietet eine programmgesteuerte Schnittstelle für KI-Integrationen:

```bash
python -m rpx_pro.app --cli
```

**JSON-RPC-Protokoll** über stdin/stdout:

```json
{"id": 1, "method": "roll_dice", "params": {"count": 2, "sides": 20}}
{"id": 1, "result": {"dice": "2d20", "rolls": [14, 7], "total": 21}}
```

## Datenschutz & Lokale Daten

RPX Pro arbeitet vollständig offline. Welten, Sessions, Medien, Konfigurationsdateien und Sicherungen verbleiben in `rpx_pro_data/` auf dem lokalen Gerät.

## Lizenz & Haftung

MIT License — siehe [LICENSE](LICENSE).

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gilt der Haftungsausschluss der MIT-Lizenz.
