# PWA-Testplan - RPX Pro Companion

Stand: 2026-06-12

Dieser Testplan deckt den offenen P2-Pfad für Android-/iOS-PWA-Smokes ab. Ziel ist
kein nativer GM-Desktop-Klon, sondern die Companion-Nutzung für Bundle-Import,
Touch-Bedienung und Offline-Start.

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
   - Spieler-Modus lässt sich öffnen und ein Charakter antippen.
4. PWA installieren:
   - Browser-Menü → App installieren oder Zum Startbildschirm hinzufügen.
5. Installierte PWA starten und prüfen:
   - Safe-Area/Abstände stimmen.
   - Buttons und Charakterkarten sind sauber antippbar.
   - Keine horizontale Scrollbar.
6. Offline-Test:
   - Flugmodus oder Browser offline.
   - PWA komplett schließen und erneut öffnen.
   - Erwartung: Shell startet offline, zuletzt geladenes Bundle wird lokal
     wiederhergestellt.

## iPhone-/iPad-Smoketest

1. Safari öffnen und `web_companion/` laden.
2. Bundle importieren und dieselben Basisprüfungen wie auf Android ausführen.
3. PWA installieren:
   - Teilen → Zum Home-Bildschirm.
4. Home-Screen-App starten und prüfen:
   - Statusleiste/Notch überdeckt keine Inhalte.
   - Importbereich, Spieler-Modus und Missionslisten bleiben mit dem Daumen
     gut bedienbar.
   - App wirkt wie eine Standalone-PWA ohne störende Safari-Leiste.
5. Offline-Test:
   - Netzwerk deaktivieren.
   - App aus dem App-Switcher schließen und neu öffnen.
   - Erwartung: Shell und letzter Bundle-Stand sind lokal verfügbar.

## Abnahmekriterien

- Bundle-Import funktioniert ohne Server und ohne Upload.
- Touch-Ziele bleiben auf Mobilgeräten gut bedienbar.
- Der zuletzt geladene Bundle-Stand wird lokal wiederhergestellt.
- Die App startet nach Installation im PWA-Modus ohne sichtbare Layout-Brüche.

## Nicht Teil dieses P2-Smokes

- Native Android- oder iOS-Wrapper.
- Desktop-GM-Funktionen wie Audio, Kartenbearbeitung oder Zweitmonitorsteuerung.
- Cloud-Sync oder Mehrgeräte-Kollaboration.
