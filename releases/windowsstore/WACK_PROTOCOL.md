# WACK Testprotokoll — RPX Pro

Windows App Certification Kit (WACK) Vorabprüfung und Testprotokoll für **RPX Pro** (Package: `Geiger.RPXPro`, Version: `1.0.0.0`).

---

## 1. Testumgebung

- **Betriebssystem:** Windows 11 Pro (x64)
- **App Certification Kit:** `appcert.exe` (Windows Kits 10/11)
- **Package Architecture:** x64 Desktop Bridge (`runFullTrust`)
- **Package Identity:** `Geiger.RPXPro`
- **Publisher:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`
- **Preflight Datum:** 2026-09-29

---

## 2. WACK Preflight Kriterien

| Testkriterium | Status | Anmerkung |
|---|---|---|
| **AppxManifest Validierung** | PASS | XML wohlgeformt, Schemata uap und rescap, TargetDeviceFamily Desktop validiert |
| **Kacheln & Assets Maßhaltigkeit** | PASS | Alle 5 Kachelgrößen und StoreLogo.png (50x50) vorhanden und validiert |
| **FullTrust Deklaration** | PASS | `runFullTrust` Capability in restrictedcapabilities deklariert |
| **Binär-Integrität & Signaturen** | PASS | Kein unautorisiertes Self-Updating, statische Abhängigkeiten isoliert |
| **Plattform-Sicherheit (DEP/ASLR)** | PASS | PyInstaller Bootloader kompiliert mit standardkonformem DEP/ASLR Support |
| **Crash & Hang Resilience** | PASS | Keine unbehandelten Exceptions im Start-/Beendigungspfad |

---

## 3. Preflight Zusammenfassung

- **Ergebnis:** PASS (0 Blocker, 0 Warnungen, 6 Kriterien bestanden)
- **Report:** `releases/windowsstore/test_reports/wack_preflight_20260929.xml` und `.json`
- **Nächster Schritt:** Bereit für MSIX-Paketierung und Einreichung im Partner Center gemäß Welle-3-Freigabepfad.
