# Feature-Analyse: RPX (RolePlay Xtreme) Pro & Light

## Kurzbeschreibung
Ein professionelles Rollenspiel-Kontrollzentrum für Pen & Paper RPGs. Bietet Welten-Management, Soundboard, Lichteffekte, Charakterverwaltung und KI-Integration. Verfügbar in zwei Varianten: Pro (Vollversion) und Light (Einsteiger).

---

## ✨ Highlights RPX Pro

| Feature | Beschreibung |
|---------|-------------|
| **Welten-System** | Karten, Orte, Nationen, Völker |
| **Soundboard** | Multi-Backend Audio (Qt, pygame, winsound) |
| **Lichteffekte** | Blitz, Stroboskop, Tag/Nacht, Farbfilter |
| **Trigger-System** | Event-basierte Automatisierung |
| **Kampfsystem** | Waffen, Rüstungen, Magie, Kampftechniken |
| **Inventar** | Items, Fahrzeuge, Zauber |
| **Session-Manager** | Missionen, Gruppen, Rundensteuerung |
| **KI-Integration** | 7 KI-Rollen, Promptgenerator |
| **Charaktere** | Vollständige Charakterverwaltung |
| **Chat-System** | Rollen-basierte Nachrichten |

---

## 📦 Editionen-Vergleich

| Feature | RPX Light | RPX Pro |
|---------|:---------:|:-------:|
| Welten & Orte | ✅ | ✅ |
| Soundboard | ✅ | ✅ |
| Lichteffekte | ✅ | ✅ |
| Würfelsystem | ✅ | ✅ |
| Session-Management | ✅ | ✅ |
| KI-Prompts | 5 Rollen | 7 Rollen |
| Waffen/Rüstungen | ❌ | ✅ |
| Magie/Zauber | ❌ | ✅ |
| Items/Inventar | ❌ | ✅ |
| Fahrzeuge | ❌ | ✅ |
| Trigger-System | ❌ | ✅ |

---

## 📊 Feature-Vergleich (Markt)

| Feature | RPX Pro | Roll20 | Foundry VTT | Fantasy Grounds |
|---------|:-------:|:------:|:-----------:|:---------------:|
| Offline-fähig | ✅ | ❌ | ✅ | ✅ |
| Soundboard | ✅ | ⚠️ | ✅ | ⚠️ |
| Lichteffekte | ✅ | ❌ | ⚠️ | ❌ |
| KI-Integration | ✅ | ❌ | ⚠️ | ❌ |
| Kostenlos | ✅ | ⚠️ | ❌ | ❌ |
| Trigger-System | ✅ | ⚠️ | ✅ | ⚠️ |
| Lokale Daten | ✅ | ❌ | ✅ | ✅ |

---

## 🎯 Bewertung

### Aktueller Stand: **Production Ready (85%)**

| Kategorie | Bewertung |
|-----------|:---------:|
| Funktionsumfang | ⭐⭐⭐⭐⭐ |
| UI/UX | ⭐⭐⭐⭐ |
| Immersion | ⭐⭐⭐⭐⭐ |
| Erweiterbarkeit | ⭐⭐⭐⭐ |

**Gesamtbewertung: 8.5/10** - Professionelles RPG-Kontrollzentrum

---

## 🚀 Empfohlene Erweiterungen

### Priorität: Hoch
1. **Netzwerk-Modus** - Multi-Spieler über LAN/Internet
2. **Bildschirm-Sharing** - Zweiter Monitor für Spieler

### Priorität: Mittel
3. **Regelwerk-Import** - D&D, Pathfinder, DSA Templates
4. **Karten-Editor** - Interaktive Karten mit Token
5. **Dice-Animation** - 3D Würfel-Visualisierung
6. **Mobile-App** - Spieler-Companion App

---

## 💻 Technische Details

### Code-Statistik
```
RPX Pro:      3.234 Zeilen Python
RPX Light:    3.236 Zeilen Python
Framework:    PySide6 (Qt6)
```

### Audio-Backend (Multi-Fallback)
```
1. QtMultimedia (QMediaPlayer)
2. pygame
3. winsound (Windows, nur WAV)
4. QSoundEffect (nur WAV)
```

### Datenstruktur (Pro)
```
rpx_pro_data/
├── worlds/        # Welten-Definitionen
├── sessions/      # Spielsitzungen
├── characters/    # Charaktere
├── items/         # Gegenstände
├── weapons/       # Waffen
├── armor/         # Rüstungen
├── spells/        # Zauber
├── vehicles/      # Fahrzeuge
├── media/
│   ├── sounds/    # Sound-Effekte
│   ├── music/     # Hintergrundmusik
│   ├── images/    # Bilder
│   └── maps/      # Karten
└── backups/       # Automatische Backups
```

---

## 🎭 KI-Rollen (Promptgenerator)

| Rolle | Beschreibung |
|-------|-------------|
| Spielleiter | Haupt-Erzähler |
| Erzähler | Atmosphäre & Beschreibung |
| NPC | Nicht-Spieler-Charaktere |
| Regel-Experte | Regelwerk-Beratung |
| Kampf-Manager | Kampfablauf |
| Welt-Architekt | Weltenbau |
| Item-Designer | Gegenstands-Erstellung |

---

## 🔑 Unique Selling Points

1. **Lichteffekte** - Echte Stroboskop/Blitz-Effekte für Immersion
2. **Trigger-System** - Automatisierung bei Ortswechsel
3. **Multi-Audio-Backend** - Funktioniert auf allen Systemen
4. **Zwei Editionen** - Light für Einsteiger, Pro für Power-User

---
*Analyse erstellt: 02.01.2026*
