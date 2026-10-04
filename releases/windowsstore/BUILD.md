# RPX Pro — Windows Store MSIX Build & Packaging Guide

Dokumentation des Build- und Packaging-Prozesses für die Microsoft Store Version von RPX Pro (Identity: `Geiger.RPXPro`, Version: `1.0.0.0`).

---

## 1. Voraussetzungen

- **Python:** 3.10+ (x64) mit virtueller Umgebung und installierten Dependencies (`pip install -r requirements.txt`)
- **Windows SDK:** Version 10.0.17763.0 oder höher mit den Werkzeugen:
  - `makeappx.exe` (`C:\Program Files (x86)\Windows Kits\10\App Certification Kit\makeappx.exe` oder SDK `bin/x64`)
  - `signtool.exe` (für lokale Testzertifikate)
  - `appcert.exe` (Windows App Certification Kit / WACK)

---

## 2. Desktop-Binary erstellen (PyInstaller)

```powershell
# Im Root des Repositories
pyinstaller RPX_Pro.spec --clean --noconfirm
```

Ergebnis:
- `dist/RPX_Pro/RPX_Pro.exe` und zugehörige Binärdateien.

---

## 3. Desktop Bridge Staging vorbereiten

Für das MSIX-Packaging wird das Dateilayout in ein Staging-Verzeichnis zusammengestellt:

```text
staging/
├── AppxManifest.xml        (aus store_package/RPX Pro/AppxManifest.xml)
├── icons/
│   ├── StoreLogo.png       (50x50 PNG)
│   ├── Square44x44Logo.png
│   ├── Square50x50Logo.png
│   ├── Square150x150Logo.png
│   ├── Wide310x150Logo.png
│   └── Square310x310Logo.png
├── rulesets/               (Integrierte D&D 5e, DSA 5 und Fantasy Regelwerke)
├── locales/                (Lokalisierungskataloge: de, en, es)
└── RPXPro.exe              (Kopiert aus PyInstaller dist)
```

---

## 4. MSIX-Paket schnüren

```powershell
& "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\makeappx.exe" pack `
    /d "<Pfad-zu-staging>" `
    /p "releases\windowsstore\RPXPro.msix" `
    /l
```

---

## 5. Lokales Signieren (nur für Sideloading / Tests)

Für den Microsoft Store Upload im Partner Center ist **keine** manuelle Signierung erforderlich, da Microsoft das Paket während der Ingestion mit dem Store-Zertifikat signiert.

Für lokale Installationstests:
```powershell
& "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe" sign `
    /fd SHA256 `
    /a `
    /f "C:\_Local_DEV\certs\development.pfx" `
    /p "<Passwort>" `
    "releases\windowsstore\RPXPro.msix"
```

---

## 6. Preflight & WACK Prüfung

Vor dem Hochladen in das Partner Center:

```powershell
# 1. Store Readiness Preflight Auditor ausführen:
python scripts/check_store_readiness.py

# 2. WACK Preflight Evaluator ausführen:
python scripts/run_windows_wack.py --dry-run
```
