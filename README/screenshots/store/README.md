# Store-Screenshots

Reproduzierbare Windows-Store-Screenshots für RPX Pro.

## Erzeugung

```bash
python generate_store_screenshots.py
```

Der Generator nutzt isolierte Demo-Daten, erzeugt keine echten Nutzerdaten und
schreibt folgende Dateien:

- `main-window.png`
- `world-map.png`
- `player-screen.png`
- `soundboard.png`
- `ai-prompts.png`
- `summary.json`

## Zweck

Die Bilder decken die Kernflächen für das Store-Listing ab:

- GM-Hauptfenster mit Chat und Rundensteuerung
- Weltkarte mit Orten und Mehrkarten-Support
- Spieler-Bildschirm für den zweiten Monitor
- Soundboard für lokale Effekte
- KI-Promptgenerator für Story- und Szenenhilfe
