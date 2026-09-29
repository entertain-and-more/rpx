# Windows Store Preparation & Packaging Status — RPX Pro

Dieses Dokument fasst den Vorbereitungsstand und die Konfiguration für die Einreichung von **RPX Pro** im Microsoft Windows Store zusammen.

---

## 1. Identität & Partner Center Metadaten

| Attribut | Wert |
|---|---|
| **Produktname** | RPX Pro |
| **Package / Identity Name** | `Geiger.RPXPro` |
| **Publisher-ID (DN)** | `CN=52596601-BAB4-4F3F-B182-E8F3F273B202` |
| **Publisher Display Name** | `Geiger` |
| **Package Version** | `1.0.0.0` |
| **Application Version** | `1.0.0` |
| **Architektur** | `x64` |
| **Kategorie** | `Entertainment / Gaming` |
| **Altersfreigabe** | `12+` (IARC Questionnaire konform) |
| **Kostenmodell** | Kostenlos (Open Source, MIT License) |
| **Capabilities** | `runFullTrust`, `internetClient` |
| **Store-ID** | `TBD` (Welle-3-Freigabe anstehend) |
| **Datenschutz-URL** | `https://github.com/entertain-and-more/rpx/blob/master/PRIVACY_POLICY.md` |
| **Support-URL** | `https://github.com/entertain-and-more/rpx/issues` |

---

## 2. Store Kachel- & Icon-Assets

Alle erforderlichen Kachelgrößen liegen in `store_package/RPX Pro/icons/` und `releases/windowsstore/` vor:

| Asset-Datei | Pixelgröße | Verwendung |
|---|---|---|
| `StoreLogo.png` | 50 × 50 | Kanonisches Store-Logo für Listing und AppxManifest `<Logo>` |
| `Square44x44Logo.png` | 44 × 44 | Windows Startmenü & Taskleisten-Kachel (Small) |
| `Square50x50Logo.png` | 50 × 50 | App-Listen-Kachel (Legacy) |
| `Square150x150Logo.png` | 150 × 150 | Windows Startmenü Mittlere Kachel (Medium) |
| `Wide310x150Logo.png` | 310 × 150 | Windows Startmenü Breite Kachel (Wide) |
| `Square310x310Logo.png` | 310 × 310 | Windows Startmenü Große Kachel (Large) |

---

## 3. Screenshots (1600 × 960 PNG)

In `releases/windowsstore/screenshots/`:
- `01-main-window.png`: Hauptfenster mit Welten- und Charakterübersicht
- `02-world-map.png`: Interaktive Weltkarte mit Ortsmarkierungen
- `03-player-screen.png`: Dynamischer Spieler-Bildschirm für zweiten Monitor
- `04-soundboard.png`: Integriertes Audio- und Soundboard-Modul
- `05-ai-prompts.png`: Kontextuelle Spielleiter- und Rollenspiel-Prompts

---

## 4. Richtlinie 10.1.3 Keyword-Compliance

Exakt 7 Keywords je Sprache, frei von geschützten Fremdmarken (keine Nennung von D&D, DSA oder Drittmarken im Keyword-Slot):
- **Deutsch:** `pen and paper, rollenspiel, spielleiter, soundboard, virtueller spieltisch, charakterbogen, wuerfelsystem`
- **Englisch:** `pen and paper, role playing game, game master, soundboard, virtual tabletop, character sheet, dice roller`

---

## 5. Preflight & WACK Status

- **Preflight Auditor:** `python scripts/check_store_readiness.py` — 0 Findings (PASS)
- **WACK Preflight:** `python scripts/run_windows_wack.py --dry-run` — 6 PASS / 0 FAIL
- **Vertragstests:** `pytest tests/test_store_readiness.py` — 100% grün
