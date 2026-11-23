# PWA-Testplan - RPX Pro Companion

Stand: 2026-11-23

Dieser Testplan deckt den P2-Pfad für Android-/iOS-PWA-Smokes ab. Ziel ist
kein nativer GM-Desktop-Klon, sondern die Companion-Nutzung für Bundle-Import,
6-Sprachen-Umschaltung, Touch-/Tastatur-Bedienung, Offline-Start und optionalen
`rpx-companion-delta-v1`-Rückexport.

## Testdaten

- Ein kleines `rpx-campaign-bundle-v1` mit mindestens:
  - 1 Welt
  - 1 Session
  - 1 Charakter
  - 1 aktive Mission
  - 1 Medienreferenz
- Optional ein zweites Bundle mit längeren Namen und mehr Missionen für
  Scroll-/Touch-Checks.

## Android-Smoketest

1. Browser öffnen und `web_companion/` laden.
2. Bundle über Dateiauswahl importieren.
3. Prüfen:
   - Statusmeldung bestätigt erfolgreichen Import.
   - Kampagnenstand zeigt Welten, Sessions, Charaktere und Missionen.
   - Sprachumschalter (`DE`/`EN`/`ES`/`ZH`/`JA`/`RU`) aktualisiert alle Karten, Labels und Aria-Attribute ohne deutsche Resttexte.
   - Spieler-Modus lässt sich öffnen, ein Charakter antippen, Status-Delta/Notiz speichern und per `Escape` oder Schließen-Button beenden.
4. PWA installieren:
   - Browser-Menü → App installieren oder Zum Startbildschirm hinzufügen.
5. Installierte PWA starten und prüfen:
   - Safe-Area/Abstände stimmen.
   - Alle Buttons, Sprachschalter und Charakterkarten erfüllen `>= 44×44 px` Touch-Ziele.
   - Keine horizontale Scrollbar (`scrollWidth <= clientWidth`).
6. Offline-Test:
   - Flugmodus oder Browser offline.
   - PWA komplett schließen und erneut öffnen.
   - Erwartung: Shell startet offline (`rpx-companion-v6`), zuletzt geladenes Bundle und erfasste Companion-Deltas werden lokal wiederhergestellt; Delta-Export liefert valides `rpx-companion-delta-v1`-JSON.

## iPhone-/iPad-Smoketest

1. Safari öffnen und `web_companion/` laden.
2. Bundle importieren und dieselben Basisprüfungen wie auf Android ausführen.
3. PWA installieren:
   - Teilen → Zum Home-Bildschirm (`apple-touch-icon-180.png`).
4. Home-Screen-App starten und prüfen:
   - Statusleiste/Notch überdeckt keine Inhalte (`viewport-fit=cover`).
   - Importbereich, Sprachwähler, Spieler-Modus und Notizformular bleiben mit dem Daumen gut bedienbar.
   - App wirkt wie eine Standalone-PWA ohne störende Safari-Leiste.
5. Offline-Test:
   - Netzwerk deaktivieren.
   - App aus dem App-Switcher schließen und neu öffnen.
   - Erwartung: Shell, letzter Bundle-Stand und lokales Companion-Delta sind offline verfügbar.

## Verifikationsstand (2026-11-23)

- **Automatisiert verifiziert (Playwright Chromium Mobile-Viewport & Offline-SW-Smoke):**
  Android-Viewport (`390×844` / `412×915`) und iOS-Standalone-Viewport (`390×844`) gegen real exportiertes `rpx-campaign-bundle-v1`-ZIP geprüft: Service-Worker-Aktivierung (`rpx-companion-v6`), `>= 44×44 px` Touch-Ziele auf allen Sprach- und Aktionsbuttons, `0` horizontaler Overflow, 6-Sprachen-Umschaltung ohne unübersetzte Reststrings, Offline-Reload (`context.set_offline(True)`) mit Bundle- & Delta-Wiederherstellung sowie `rpx-companion-delta-v1`-Download und Desktop-Reimport bestanden.
- **Offen (manuelle Echtgeräte-Gegenprobe):**
  Physischer Handtest auf realer Android-Chrome- und iOS-Safari-Hardware bei nächster Tischrunde.

## Abnahmekriterien

- Bundle-Import und optionaler `rpx-companion-delta-v1`-Export funktionieren ohne Server und ohne Upload.
- Touch-Ziele bleiben auf Mobilgeräten `>= 44×44 px` bedienbar.
- Der zuletzt geladene Bundle-Stand und lokale Deltas werden offline wiederhergestellt.
- Die App startet nach Installation im PWA-Modus ohne sichtbare Layout-Brüche.

## Nicht Teil dieses P2-Smokes

- Native Android- oder iOS-Wrapper.
- Desktop-GM-Funktionen wie Audio, Kartenbearbeitung oder Zweitmonitorsteuerung.
- Cloud-Sync oder Mehrgeräte-Serverkollaboration.
