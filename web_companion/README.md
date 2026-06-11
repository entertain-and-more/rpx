# RPX Pro Companion

Stand: 2026-06-12

Der Companion ist eine statische Offline-Web/PWA für lokale
`rpx-campaign-bundle-v1`-ZIPs. Er ergänzt die Desktop-App für Spieler,
Spielleiter und Zweitgeräte, ersetzt aber nicht die PySide6-Vollversion.

## Enthalten

- Lokaler ZIP-Import per Dateiauswahl oder Drag-and-drop
- ZIP-Leser ohne zusätzlichen Server oder Cloud-Upload
- Kampagnenübersicht mit Welten-, Session-, Charakter- und Missionsstatus
- Medien- und Kartenreferenzen aus `media/manifest.json`
- Read-only-Regelwerk-Ansicht mit Zählwerten für Waffen und Zauber
- Offline-Shell per Manifest und Service Worker
- Lokale Wiederherstellung des zuletzt geladenen Bundles für Offline-Neustarts
- Android-/iOS-Installhinweise direkt in der UI

## Start lokal

```bash
cd web_companion
python -m http.server 8765
```

Danach im Browser öffnen:

- `http://127.0.0.1:8765/`

## Tests

```bash
node --test web_companion/tests/library.test.mjs
node --test web_companion/tests/pwa.test.mjs
node --test web_companion/tests/player.test.mjs
node --check web_companion/app.js
node --check web_companion/library.js
node --check web_companion/sw.js
```

## Mobile-Smokes

Der konkrete Android-/iOS-PWA-Prüfpfad steht in
`web_companion/PWA_TESTPLAN.md`. Der Companion ist weiterhin read-only und
speichert nur den zuletzt geladenen Bundle-Stand lokal auf dem Gerät.

## Nicht-Ziele

- Keine direkte Bearbeitung von Desktop-Projektdaten
- Kein Starten lokaler Audio-, Karten- oder GM-Desktop-Funktionen im Browser
- Kein Server-Upload von Kampagnenpaketen
- Keine native Android-/iOS-App vor den geplanten PWA-Smokes
