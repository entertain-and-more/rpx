# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Fixed
- Neue Karten starten im `WorldTab` wieder leer: `add_map()` zieht `active_map_id` nicht mehr vor dem Wechsel um, sodass die Elemente der bisherigen Karte nicht in die neue Karte kopiert werden.
- Inventar-Auswahldialoge für Charaktere, Welt-Items und NPCs machen doppelte Anzeigenamen jetzt über kurze ID-Suffixe eindeutig, damit Auswahlrückläufe nicht mehr still auf die erste passende Entität zeigen.
- Direktes Schließen des Spieler-Bildschirms (Alt+F4, Fenster-X) wird jetzt erkannt: `PlayerScreen` setzt `Qt.WA_DeleteOnClose` und emittiert ein `closed`-Signal, `MainWindow` räumt Referenz, Menü-/Button-Text und Statusbar zentral in `_on_player_screen_closed()` auf statt nur beim Menü-Toggle.

### Tests
- Neuer Regressionstest `tests/test_world_tab_map_regression.py` sichert, dass `add_map()` die Elemente und Charakterpositionen der bisherigen Karte nicht in neue Karten übernimmt.
- Neue Regressionen in `tests/test_bug_regressions.py` sichern die eindeutigen Auswahl-Labels und den Verzicht auf fehleranfälliges `.index(name)`-Lookup.
- Neuer Regressionstest `tests/test_player_screen_close_regression.py` sichert `WA_DeleteOnClose`, das `closed`-Signal und den einmaligen Aufräum-Handler in `MainWindow`.

### Documentation
- Restructured README.md to English-first; German documentation retained as collapsible secondary section.
- Added `llms.txt` with project description, tools, install instructions, audience, and search phrases.
- Standardized `llms.txt`: moved `Last-checked` header to first line, converted Search Phrases to fenced
  code block, added canonical repository URL and two additional search phrases.

### Maintenance
- Added `web_companion_FINAL_*/`, `*PREFIXBAK*`, and `docs/` to `.gitignore` to prevent stale build artifacts from being tracked.

### web_companion

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
- Die kompakten `...`-Buttons für Außen- und Innenbild im Ortsdialog behalten ihre dichte UI, exponieren jetzt aber sprechende Tooltips sowie Accessible Names und Descriptions.
- Veraltete Legacy-Clone-Links und breit formulierte GPL/MIT/Apache-Haftungspassage bereinigt.
- Campaign-Bundle-Import normalisiert Bundle-Medienpfade jetzt auf lokale Desktop-Pfade und unterstützt auch ältere relative Pfade wie `maps/...` oder `images/...`.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
