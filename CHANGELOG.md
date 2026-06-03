# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- README-Hinweise für Screenshot, EXE-Build, lokales Datenschutzmodell und aktuelles GitHub-Repository ergänzt.
- GitHub Actions Syntax-Smoke-Test für Python 3.10-3.12 ergänzt.
- `EXPORTFORMAT.md` für `rpx-campaign-bundle-v1` ergänzt.
- Backend-Export für Kampagnen-Bundles mit Welten, Sessions, Regelwerken und optionalen Medien ergänzt.
- JSON-RPC-/API-Methode `export_campaign_bundle` ergänzt.
- JSON-RPC-/API-Methode `import_campaign_bundle` mit Konfliktstrategien `rename`, `replace` und `skip` ergänzt.
- Regressionstests für Bundle-Import, Medienextraktion und Legacy-Pfade ergänzt.

### Geändert / Changed
- Store-Listing und Paketbeschreibung mit echten deutschen Umlauten abgeglichen.
- Portierungsplan für Windows Store, Web/PWA-Companion, Android/iOS-PWA-Testlinie sowie macOS-/Linux-Smoke-Tests ergänzt.
- `_WARTUNG/` und lokale Secret-/Cache-/Build-Artefakte werden ignoriert; bereits getrackte MSIX-Staging-Artefakte wurden aus dem Index entfernt.
- Security-, Privacy-, Contributing- und Code-of-Conduct-Dateien auf aktuelle Repository-Links und öffentliche Meldewege aktualisiert.
- Exportierte Welt- und Session-JSONs schreiben Medienpfade jetzt relativ als `media/...`, damit spätere Companion-Importer keine Desktop-Pfade voraussetzen.

### Behoben / Fixed
- Veraltete Legacy-Clone-Links und breit formulierte GPL/MIT/Apache-Haftungspassage bereinigt.
- Campaign-Bundle-Import normalisiert Bundle-Medienpfade jetzt auf lokale Desktop-Pfade und unterstützt auch ältere relative Pfade wie `maps/...` oder `images/...`.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
