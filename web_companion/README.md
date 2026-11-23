# RPX Pro Companion

Stand: 2026-11-23

Der Companion ist eine statische Offline-Web/PWA für lokale
`rpx-campaign-bundle-v1`-ZIPs. Er ergänzt die Desktop-App für Spieler,
Spielleiter und Zweitgeräte auf Web, Android und iOS/iPadOS, ersetzt aber nicht
die PySide6-Vollversion.

## Enthalten

- Lokaler ZIP-Import per Dateiauswahl oder Drag-and-drop ohne Server-Upload
- Vollständige Tier-2-Mehrsprachigkeit über alle 6 Sprachen (`DE`, `EN`, `ES`, `ZH`, `JA`, `RU`) mit 92 synchronisierten UI-Schlüsseln
- Kampagnenübersicht mit Welten-, Session-, Charakter- und Missionsstatus
- Medien- und Kartenreferenzen aus `media/manifest.json` sowie Read-only-Regelwerk-Ansicht
- Barrierefreier Spieler-Modus (`role="dialog"`, `aria-modal="true"`, `Escape`-Schließen, Tastaturnavigation, `>= 44×44 px` Touch-Ziele)
- Optionaler Offline-Tisch-Notizen- & Status-Delta-Rückexport (`rpx-companion-delta-v1` JSON) für LP/HP, Mana, Gold und Spielernotizen (getrennt vom unveränderlichen Basis-Bundle im lokalen Gerätespeicher gehalten)
- Offline-Shell per Manifest und Service Worker (`rpx-companion-v6` mit SHA-256 `ASSET_HASH`-Wächter)
- Lokale Wiederherstellung des zuletzt geladenen Bundles und offener Companion-Deltas für Offline-Neustarts
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
node --test web_companion/tests/i18n.test.mjs
node --test web_companion/tests/library.test.mjs
node --test web_companion/tests/pwa.test.mjs
node --test web_companion/tests/player.test.mjs
node --test web_companion/tests/sw_asset_hash.test.mjs
node --check web_companion/app.js
node --check web_companion/library.js
node --check web_companion/i18n.js
node --check web_companion/sw.js
```

## Mobile-Smokes & Rückimport

Der konkrete Android-/iOS-PWA-Prüfpfad steht in
`web_companion/PWA_TESTPLAN.md`. Exportierte `*-companion-delta.json`-Dateien
können am Desktop kontrolliert und nicht-destruktiv über
`RPXProAPI.import_companion_delta` bzw. die JSON-RPC-CLI (`import_companion_delta`)
eingelesen werden.

## Nicht-Ziele

- Keine direkte Bearbeitung von Welten, Karten, Orten oder Regelwerken im Browser
- Kein Starten lokaler Audio-, Karten- oder GM-Zweitmonitor-Funktionen im Browser
- Kein Cloud-Zwang und kein Server-Upload von Kampagnenpaketen
- Keine native Android-/iOS-Vollapp vor belegtem Mehrwert gegenüber der PWA
