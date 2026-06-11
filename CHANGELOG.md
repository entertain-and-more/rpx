# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

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

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
