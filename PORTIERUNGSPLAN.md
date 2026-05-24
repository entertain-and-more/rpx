# Portierungsplan - RPX Pro

Stand: 2026-05-24

## Kurzentscheidung

RPX Pro bleibt zuerst eine Windows-Desktop-App für den Microsoft Store. Das ist sinnvoll, weil die Kernnutzung am Spieltisch einen Laptop, lokale Medien, Soundboard, Kartenansicht und einen zweiten Bildschirm braucht. Eine vollständige native Mobile- oder Web-Neuentwicklung wäre für diesen Funktionsumfang unverhältnismäßig.

Die plattformübergreifende Linie soll stattdessen über zwei Wege laufen:

- Desktop-Codebasis auf Windows, macOS und Linux möglichst gemeinsam halten.
- Web/PWA-Companion für Android, iOS und Browser entwickeln, der Kampagnen lesen, Spielersichten anzeigen und einfache Session-Aktionen unterstützen kann.

Als Austauschformat wird ein versioniertes Kampagnenpaket `rpx-campaign-bundle-v1` eingeführt. Es soll Welten, Sessions, Regelwerk-Metadaten und einen Medien-Manifestindex enthalten. Große Mediendateien bleiben optional, damit Mobilgeräte nicht unnötig belastet werden.

## Warum Portierung sinnvoll ist

- Nachfrage: Pen-and-Paper-Gruppen nutzen häufig gemischte Geräte. Der Spielleiter arbeitet am Laptop, Spieler lesen Handouts oder Statusinformationen auf Smartphone/Tablet.
- Mobilität: Vorbereitung und Nachschlagen unterwegs sind relevant, aber vollständige Karten-, Licht- und Soundsteuerung gehört an den Desktop.
- Usecases: GM-Desktop am Tisch, Spieler-Companion im Browser, Tablet-Spielerbildschirm, mobile Kampagnenübersicht, plattformübergreifender Datenaustausch.
- Wettbewerb: Roll20, Foundry VTT und Fantasy Grounds sind plattformübergreifend oder browsernah. RPX Pro kann sich als offlinefähige Desktop-Zentrale mit leichtem Companion differenzieren.

## Plattformbewertung

| Plattform | Bewertung | Entscheidung |
|---|---|---|
| Windows Store | Sehr hoch | Hauptkanal. Store-Listing, Screenshots, MSIX/WACK und Dogfooding über `_STORE/` priorisieren. |
| Webapp | Hoch | Als Companion/PWA planen, nicht als vollständiger Desktop-Clone. Fokus: Kampagnenübersicht, Spieleransicht, Handouts, Chat-/Session-Auszüge. |
| Android | Mittel-hoch | Über PWA/WebView testen. Native Android-App erst nach bewiesenem Companion-Nutzen. |
| iOS | Mittel | Über PWA testen. Native iOS-App wegen Aufwand und Store-Pflege zurückstellen. |
| Mac App | Mittel | Aus derselben PySide6-Codebasis als Smoke-/Build-Ziel prüfen; Audio, Vollbild, Dateipfade und zweiter Bildschirm sind die Risikopunkte. |
| Linux Version | Mittel | Aus derselben PySide6-Codebasis als Smoke-/Build-Ziel prüfen; pygame/Qt-Multimedia und Dateiauswahl testen. |

## Zielarchitektur

1. **Desktop Pro**
   - Windows bleibt primäres Release-Ziel.
   - macOS/Linux werden als P3-Smoke- und später als optionale Build-Ziele geführt.
   - Lokale Daten bleiben unter `rpx_pro_data/`, aber Export/Import darf nicht an absolute Pfade gebunden sein.

2. **Austauschformat `rpx-campaign-bundle-v1`**
   - JSON/ZIP-basiertes Paket mit `manifest.json`, `worlds/`, `sessions/`, `rulesets/` und optionalem `media/`.
   - Pfade werden relativ gespeichert.
   - Medien können vollständig, manifest-only oder ausgelassen exportiert werden.
   - Import muss alte Desktop-Daten nicht zerstören und Konflikte sichtbar machen.

3. **Web/PWA-Companion**
   - Lädt `rpx-campaign-bundle-v1`.
   - Zeigt Spielerstatus, aktuelle Missionen, Handouts, Karten-Snapshot und Chat-Auszüge.
   - Kann optional kleine Session-Notizen oder Spieleraktionen als separates Delta exportieren.
   - Keine direkte Abhängigkeit von PySide6, pygame oder lokalen Desktop-Pfaden.

4. **Mobile Linie**
   - Android/iOS zunächst über PWA.
   - Ziel ist eine Companion-Erfahrung, kein nativer GM-Desktop-Clone.
   - Touch-Layout und Offline-Cache sind wichtiger als vollständige Bearbeitung.

## Umsetzungsstatus

| Bereich | Status | Notiz |
|---|---|---|
| Windows Desktop | Teilweise vorhanden | PySide6-App, Store-Listing, `store_package.json`, Start-/Builddateien vorhanden. |
| Windows Store | Vorbereitung | Store-Screenshots, finale Store-Texte, MSIX/WACK und Lizenzabgleich offen. |
| Export/Import | Offen | Daten sind JSON-basiert, aber noch kein stabiles Campaign-Bundle dokumentiert. |
| Web/PWA | Offen | Noch kein Companion-Projekt vorhanden. |
| Android/iOS | Offen | Wird aus Web/PWA abgeleitet. |
| macOS/Linux | Offen | PySide6 spricht dafür, Audio und Zweitmonitor müssen getestet werden. |

## Priorisierte Aufgaben

### P0 - Datenaustausch

- `rpx-campaign-bundle-v1` als `EXPORTFORMAT.md` dokumentieren.
- Exportfunktion für Welten, Sessions, Regelwerke und optional Medien ergänzen.
- Importpfad mit Konfliktstrategie und Rückwärtskompatibilität testen.

### P1 - Windows Store

- Store-Screenshots für Hauptfenster, Weltkarte, Spieler-Bildschirm, Soundboard und KI-Prompts erstellen.
- Store-Listing DE/EN aktualisieren und echte Umlaute in deutschen Texten verwenden.
- MSIX mit `_STORE/` bauen und WACK-Testprotokoll ablegen.

### P2 - Web/PWA-Companion

- Minimalen PWA-Prototyp für `rpx-campaign-bundle-v1` planen.
- Views: Kampagnenübersicht, Charakterstatus, Missionen, Handouts, Karten-Snapshot.
- Offline-Cache und Touch-Bedienung für Tablet/Smartphone berücksichtigen.

### P3 - macOS/Linux

- Source-Smoke-Test auf macOS und Linux definieren.
- Audio-Backend, Dateiauswahl, Vollbild und Zweitmonitor prüfen.
- Erst nach grünem Smoke-Test optionale Paketierung bewerten.

## Nicht-Ziele

- Keine native Android-/iOS-Vollversion vor einem funktionierenden PWA-Companion.
- Keine vollständige Browser-Neuentwicklung der GM-Zentrale im ersten Schritt.
- Keine Cloud-Pflicht. RPX Pro bleibt offline-first; Synchronisation läuft über explizite Export-/Importpakete.
