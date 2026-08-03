# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Added
- Defined the macOS/Linux source smoke in `SOURCE_SMOKE_TEST.md`, added
  `tests/test_source_platform_smoke.py`, and wired a GitHub Actions
  `source-smoke` matrix for `ubuntu-latest` and `macos-latest`.

### Marketing & Discoverability
- Synchronized Shields.io badges in `README.md` and `README_de.md` with `entertain-and-more` organization and `open-bricks` ecosystem badges.
- Verified test suite status across Python Pytest (14 passed) and Node.js Web Companion PWA tests (17 passed, 31 total).
- Updated `llms.txt` header to `Last-checked: 2026-08-03` with updated test verification notes.

## [1.0.1] - 2026-07-25

### Marketing & Discoverability
- Integrated standard PEP 621 `pyproject.toml` with project metadata, dependencies, classifiers, and pytest configuration (`pythonpath = "."`).
- Added German landing page `README_de.md` with full parity, language switcher, badges, callouts, and Mermaid architecture diagram.
- Updated `README.md` with Shields.io badges (Pytest 9 passed, Web Companion 17 passed, PySide6, License, Python, Privacy, LLM Ready), language switcher, GitHub Alert Note callout, and Mermaid architecture & data flow diagram.
- Updated `llms.txt` header with `Last-checked: 2026-07-25`, verification status notes (26 passing tests), and link to `README_de.md`.

## [1.0.0] - 2026-07-23

### Documentation
- Added a README audience/use-case entry section and refreshed `llms.txt` discovery phrases for tabletop RPG, local-first game-master, PWA companion, and JSON-RPC LLM API searches.
- Restructured README.md to English-first; German documentation retained as collapsible secondary section.
- Added `llms.txt` with project description, tools, install instructions, audience, and search phrases.
- Standardized `llms.txt`: moved `Last-checked` header to first line, converted Search Phrases to fenced
  code block, added canonical repository URL and two additional search phrases.

### Maintenance
- Added `web_companion_FINAL_*/`, `*PREFIXBAK*`, and `docs/` to `.gitignore` to prevent stale build artifacts from being tracked.

### web_companion

- Bundle-Daten werden in den dynamischen Companion-Ansichten jetzt per
  `textContent`/DOM-Knoten statt per HTML-String gerendert.
- Fixed `skipWaiting()` race condition: moved into the `waitUntil` promise chain so the SW only advances to activate after all shell files are cached.
- Player Mode: Spieler können nach Bundle-Import ihren Charakter wählen und sehen eine portrait-optimierte Karte mit HP/Mana-Balken, Gold und aktiven Missionen.
- Neue `library.js`-Funktionen: `getCharacterList(bundle)` + `getPlayerView(bundle, sessionId, characterId)`.
- `apple-touch-icon` von SVG auf PNG korrigiert, weil iOS SVG dort ignoriert.
- Testsuite von 7 auf 10 Tests erweitert (`player.test.mjs` mit 5 Unit-Tests für neue library-Funktionen).
- Zuletzt geladenes Kampagnen-Bundle wird jetzt lokal gespeichert und bei Offline-Neustarts wiederhergestellt.
- Android-/iOS-PWA-Härtung ergänzt: `viewport-fit=cover`, Installhinweise, Safe-Area-Abstände und 44px-Touch-Ziele.
- Neuer `web_companion/PWA_TESTPLAN.md` beschreibt Bundle-Import, Touch-Layout, Installation und Offline-Start für Android/iOS.

### Store

- Reproduzierbaren Screenshot-Generator `generate_store_screenshots.py` für den Windows-Store-Strang ergänzt.
- Neues Screenshot-Set unter `README/screenshots/store/`: Hauptfenster, Weltkarte, Spieler-Bildschirm, Soundboard und KI-Prompts.
- Regressionstest `tests/test_store_screenshots.py` deckt PNG-Erzeugung, Mindestgröße und `summary.json` ab.

### Hinzugefügt / Added
- README-Hinweise für Screenshot, EXE-Build, lokales Datenschutzmodell und aktuelles GitHub-Repository ergänzt.
- GitHub Actions Syntax-Smoke-Test für Python 3.10-3.12 ergänzt.
- `EXPORTFORMAT.md` für `rpx-campaign-bundle-v1` ergänzt.
- Backend-Export für Kampagnen-Bundles mit Welten, Sessions, Regelwerken und optionalen Medien ergänzt.
- JSON-RPC-/API-Methode `export_campaign_bundle` ergänzt.
- JSON-RPC-/API-Methode `import_campaign_bundle` mit Konfliktstrategien `rename`, `replace` und `skip` ergänzt.
- Regressionstests für Bundle-Import, Medienextraktion und Legacy-Pfade ergänzt.
- Statischer Offline-Web/PWA-Companion unter `web_companion/` ergänzt: lokaler ZIP-Import für `rpx-campaign-bundle-v1`, Kampagnenübersicht, Welten-, Sessions-, Missions- und Regelwerk-Ansicht sowie Medienhinweise.
- PWA-Grundlagen mit `manifest.webmanifest`, Service Worker, SVG-Icons und Node-Regressionstests für ZIP-Leser und Shell-Dateien ergänzt.

### Geändert / Changed
- Store-Listing und Paketbeschreibung mit echten deutschen Umlauten abgeglichen.
- Portierungsplan für Windows Store, Web/PWA-Companion, Android/iOS-PWA-Testlinie sowie macOS-/Linux-Smoke-Tests ergänzt.
- README, `AUFGABEN.txt` und `PORTIERUNGSPLAN.md` auf den jetzt vorhandenen Web/PWA-Prototyp nachgezogen.
- `_WARTUNG/` und lokale Secret-/Cache-/Build-Artefakte werden ignoriert; bereits getrackte MSIX-Staging-Artefakte wurden aus dem Index entfernt.
- Security-, Privacy-, Contributing- und Code-of-Conduct-Dateien auf aktuelle Repository-Links und öffentliche Meldewege aktualisiert.
- Exportierte Welt- und Session-JSONs schreiben Medienpfade jetzt relativ als `media/...`, damit spätere Companion-Importer keine Desktop-Pfade voraussetzen.

### Behoben / Fixed
- Veraltete Legacy-Clone-Links und breit formulierte GPL/MIT/Apache-Haftungspassage bereinigt.
- Campaign-Bundle-Import normalisiert Bundle-Medienpfade jetzt auf lokale Desktop-Pfade und unterstützt auch ältere relative Pfade wie `maps/...` oder `images/...`.
