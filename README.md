<img src="assets/banner.svg" width="100%" alt="RPX Pro — RolePlay Xtreme Professional Edition" />

# RPX Pro — RolePlay Xtreme Professional Edition

[English](README.md) | [Deutsch](README_de.md)

> Professional role-playing game control center for tabletop pen & paper adventures. Offline-capable, free, and open source.

[![Pytest](https://img.shields.io/badge/Pytest-14%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![Web Companion](https://img.shields.io/badge/Web%20Companion-17%20passed-brightgreen.svg)](web_companion/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-blue.svg)](https://www.qt.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://github.com/entertain-and-more/rpx)
[![Privacy](https://img.shields.io/badge/Privacy-Local--First%20%2F%20Offline-success.svg)](#privacy--local-data)
[![LLM Ready](https://img.shields.io/badge/LLM-Ready%20%2F%20JSON--RPC-purple.svg)](#cli--api-for-llm-integration)
[![Org](https://img.shields.io/badge/Org-entertain--and--more-0055ff.svg)](https://github.com/entertain-and-more)
[![Ecosystem](https://img.shields.io/badge/Ecosystem-open--bricks-orange.svg)](https://github.com/open-bricks)

> [!NOTE]
> **Local-First & Machine-Readable Architecture**: RPX Pro runs 100% offline. All campaign data, maps, audio, and rulesets remain locally in `rpx_pro_data/`. For AI agents and external LLM workflows, RPX Pro provides a zero-dependency JSON-RPC CLI (`python -m rpx_pro.app --cli`) over `stdin`/`stdout` and exports standardized `rpx-campaign-bundle-v1` ZIP files readable by the offline PWA companion in `web_companion/`.

![RPX Pro Main Window](README/screenshots/main.png)

## Who It Is For

| Need | RPX Pro fit |
|------|-------------|
| Run a tabletop RPG session from one local desktop | Worlds, maps, locations, characters, missions, ambience, combat, and notes stay in one offline workspace |
| Give players a dedicated table display | The second-monitor player screen shows maps, locations, party status, missions, chat, and event overlays |
| Use AI without handing campaign data to a hosted VTT | RPX Pro generates structured prompts and exposes a JSON-RPC CLI/API; the external AI tool stays optional |
| Carry a campaign to a phone or tablet between sessions | The static Web/PWA companion reads local `rpx-campaign-bundle-v1` ZIP exports and restores the last loaded bundle offline |
| Study a PySide6 game-master app architecture | The codebase uses dataclass models, injected managers, Qt signals, and a testable API/CLI layer |

Useful search terms: `tabletop RPG control center`, `offline game master tools`, `PySide6 RPG session manager`, `local-first virtual tabletop companion`, `JSON-RPC LLM game master API`, `rpx-campaign-bundle-v1`.

## Features

| Feature | Description |
|---------|-------------|
| **World System** | Multi-map worlds, locations (exterior/interior views), nations, species, trigger automation |
| **Soundboard** | Multi-backend audio (Qt Multimedia, pygame, winsound) |
| **Light Effects** | Lightning, strobe, day/night cycle, color filters (configurable for player screen) |
| **Combat System** | Weapons, armor, magic, combat techniques, configurable dice system |
| **Player Screen** | Separate monitor with dynamic views (tiles, rotation, images) |
| **Ruleset Import** | D&D 5e, DSA 5, Generic Fantasy — or custom JSON templates |
| **AI Integration** | Prompt generator with 7 specialized AI roles |
| **CLI / API** | JSON-RPC CLI for LLM control via stdin/stdout |
| **Web/PWA Companion** | Reads local `rpx-campaign-bundle-v1` ZIPs for campaign overview, character status, missions, media, and restores the last loaded bundle for offline mobile restarts |
| **Session Manager** | Missions, groups, round control |
| **Characters** | Attributes, inventory dialog, gold, avatar, hunger/thirst simulation |
| **Simulation** | Hunger/thirst timer, time progression, natural disasters |

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Launch
python RPX_Pro_1.py
# or:
python -m rpx_pro.app
```

On Windows: double-click `START.bat`.

### Requirements

- Python 3.10+
- PySide6 (Qt6) — includes Qt Multimedia for audio
- pygame (optional, audio fallback)

## EXE Build

```bash
build_exe.bat

# or directly
python -m PyInstaller --noconfirm --clean RPX_Pro.spec
```

Build output lands in `dist/RPX_Pro/`. The spec file includes `rulesets/`; runtime data stays in `rpx_pro_data/`.
`build/`, `dist/`, `releases/`, and `_WARTUNG/` are local build/staging directories and are not versioned.

## Windows Store Screenshots

Reproducible Store screenshots are generated with:

```bash
python generate_store_screenshots.py
```

The generator writes anonymized demo screenshots to `README/screenshots/store/`
and documents the file set in `README/screenshots/store/README.md`.

## Tests

```bash
pytest
pytest tests/test_source_platform_smoke.py
python -m compileall -q RPX_Pro_1.py manage_translations.py translator.py rpx_pro tests
python generate_store_screenshots.py
node --test web_companion/tests/*.mjs
```

For macOS/Linux source launch checks, see [SOURCE_SMOKE_TEST.md](SOURCE_SMOKE_TEST.md).

## Quick Start

1. **Create a world**: World tab > "New World" > enter a name
2. **Add a map**: World tab > "Load Map..." > select an image file
3. **Create locations**: World tab > "Add Location" > use "Edit" to assign images/sounds
4. **Start a session**: File > New Session > select a world
5. **Create characters**: Characters tab > "Create Character" > use "Edit" to set details
6. **Start playing**: Toolbar > "Start Game" — AI prompt is copied to clipboard

## System Architecture

```mermaid
graph TD
    subgraph Desktop App [RPX Pro - PySide6 Desktop GUI]
        WM[World & Map System]
        SB[Multi-Backend Soundboard]
        FX[Light & Event Effects]
        CE[Combat & Dice Engine]
        AI[AI Prompt Generator]
        PM[Player Screen Manager]
    end

    subgraph Programmatic Interfaces
        CLI[JSON-RPC CLI Interface]
        API[RPXProAPI Dataclass Contract]
    end

    subgraph Data & Storage
        ZIP[rpx-campaign-bundle-v1 ZIP Export]
        DATA[Local Disk Storage / rpx_pro_data]
    end

    subgraph Mobile & Offline
        PWA[Web PWA Companion App]
        SW[Service Worker Cache]
    end

    WM --> DATA
    CE --> DATA
    Desktop App <--> API
    API <--> CLI
    CLI <-->|stdin/stdout| ExternalAI[External LLM / AI Agents]
    Desktop App -->|Export| ZIP
    ZIP -->|Import| PWA
    PWA <--> SW
    PM -->|Second Monitor| PlayerDisplay[Player Display Output]
```

RPX Pro is built as a modular Python package (`rpx_pro/`):

```
rpx_pro/
  app.py                 # Entry point
  main_window.py         # Lean orchestrator (~1200 lines)
  constants.py           # Configuration, paths, logging
  api.py                 # Programmatic Python API (JSON-serializable)
  cli.py                 # JSON-RPC CLI for LLM control
  models/                # Data models (dataclasses)
    enums.py             # MessageRole, PlayerScreenMode, DamageType, ...
    entities.py          # Character, Weapon, Armor, Spell, Item, ...
    world.py             # World, Location, WorldSettings
    session.py           # Session, ChatMessage, Mission
  managers/              # Business logic
    data_manager.py      # Persistence (JSON files)
    audio_manager.py     # Multi-backend audio
    light_manager.py     # Light effects (overlay-based)
    prompt_generator.py  # AI prompt generation
    dice_roller.py       # Dice system
  widgets/               # Reusable UI components
    chat.py              # Chat widget with role selection
    soundboard.py        # Drag-and-drop soundboard
    player_screen.py     # Player screen (2nd monitor)
    map_widget.py        # Interactive map with drawing tools
    location_view.py     # Location view (exterior/interior)
    inventory_dialog.py  # Character inventory dialog
    prompt_widget.py     # AI prompt generator widget
    ruleset_importer.py  # Ruleset import
  tabs/                  # Standalone tab classes
    views_tab.py         # Views (location, inventory, ambience, player screen)
    world_tab.py         # World management + multi-map
    characters_tab.py    # Characters + inventory button
    combat_tab.py        # Combat + dice
    missions_tab.py      # Missions
    inventory_tab.py     # World item library
    immersion_tab.py     # Soundboard
    settings_tab.py      # Session/world settings
```

**Design principles:**
- Tabs communicate exclusively via Qt Signals (no `self.window()`)
- Managers are passed via dependency injection
- MainWindow is a pure orchestrator (connects signals, routes events)
- Models are pure dataclasses with `to_dict()`/`from_dict()` serialization

## Tab Overview

### Chat (Tab 1)
- Messages with multiple roles (Player, GM, AI roles, Narrator)
- Color-coded by role
- Chat commands: `/roll`, `/heal`, `/damage`, `/check`, `/give`
- System events are logged automatically

### Views (Tab 2)
Four sub-tabs in one:

- **Location view**: Exterior/interior with blackout transition, color filter, triggers
- **Inventory view**: Character dropdown, inventory table (name, count, weight, value), gold
- **Ambience**: Light effects (lightning, strobe, day/night, color filter) + background music (playlist, volume)
- **Player Screen**: Monitor selection, fullscreen, display mode, view checkboxes, effect mirroring

### World (Tab 3)
- Create, edit, and save worlds
- **Multi-map system**: Multiple maps per world (world map, dungeons, cities)
- Interactive map with drawing tools
- Manage locations in a tree with edit dialog

### Characters (Tab 4)
- Table of all characters with core stats
- **Inventory button** per row — opens inventory dialog with gold, weight, items
- Edit dialog: name, race, class, level, HP, mana, skills, NPC status, image, biography
- Quick HP/mana control (damage, heal, mana)

### Combat (Tab 5)
- Dice system (1–10 dice, d4 to d100)
- Attack mechanic with hit chance, critical hits, armor
- Weapon and spell lists

### Missions (Tab 6)
- Active and completed missions
- Mark as complete or failed
- Status changes are logged in chat

### Inventory (Tab 7)
- World item library (name, class, weight, value, bonuses)
- Items at locations with find probability
- NPCs at locations with encounter probability

### Soundboard (Tab 8)
- Add sound effects via drag-and-drop or dialog
- Play/stop per sound

### AI Prompts (Tab 9)
- 7 AI roles: Storyteller, Plot Twist, Game Master, Villain, NPCs, Landscape, Fauna/Flora
- Generate start prompt and context update prompt
- Copy to clipboard

### Settings (Tab 10)
- Session: round mode, actions per round, game master (human/AI)
- World: time ratio, hours per day, hunger/thirst simulation, natural disasters

## Player Screen (2nd Monitor)

The GM can open a separate display for players (Views > Player Screen):

- **4 display modes**: Image, Map, Rotation, Tiles
- **Dynamic views**: Checkboxes control which tiles are active
  - Characters (hero overview with HP/mana bars)
  - Missions (active quests)
  - Map (world map with markers)
  - Chat (session log)
  - Round control (round/initiative order)
  - Location view (current location)
  - Inventory (character inventory)
- **Rotation**: only active views cycle
- **Event overlay**: announcements for damage, healing, death, missions, rounds
- **Effect mirroring**: lightning, day/night, color filter individually switchable
- Monitor selection, fullscreen, blackout

## CLI / API for LLM Integration

RPX Pro offers a programmatic API and CLI interface for AI control:

```bash
python -m rpx_pro.app --cli
```

**JSON-RPC protocol** via stdin/stdout:

```json
{"id": 1, "method": "roll_dice", "params": {"count": 2, "sides": 20}}
{"id": 1, "result": {"dice": "2d20", "rolls": [14, 7], "total": 21}}
```

**Available methods:**
`create_world`, `list_worlds`, `load_world`, `create_session`, `list_sessions`, `load_session`,
`create_character`, `get_character`, `heal_character`, `damage_character`, `get_inventory`, `give_item`,
`send_chat_message`, `get_chat_history`, `roll_dice`, `create_mission`, `complete_mission`,
`generate_start_prompt`, `generate_context_update`, `export_campaign_bundle`, `import_campaign_bundle`

For cross-platform data exchange, `export_campaign_bundle` produces a ZIP bundle in `rpx-campaign-bundle-v1` format with `manifest.json`, worlds, sessions, rulesets, and optional media. `import_campaign_bundle` reads this format back, normalizes media paths for the desktop, and supports conflict strategies for existing worlds, sessions, and rulesets.

## Web/PWA Companion

`web_companion/` is a static offline companion for the same bundle format.
It loads local ZIP files via file picker or drag-and-drop and shows:

- Campaign overview with export time and bundle statistics
- Worlds, maps, and location hints
- Session views with character status, missions, and recent chat lines
- Rulesets and media references from `media/manifest.json`

Run locally:

```bash
cd web_companion
python -m http.server 8765
```

See [EXPORTFORMAT.md](EXPORTFORMAT.md) for the bundle format specification.

## Simulation

### Hunger/Thirst
- Rise proportionally to play time; warnings at 50% and 75%
- Rate per in-game hour is configurable; race modifiers possible

### Natural Disasters
- Random events: earthquake, flood, volcanic eruption, tornado, etc.
- Visual strobe effect + chat message

### Time Progression
- Game time runs proportionally to real time (ratio configurable)
- Day-change notifications, time of day on player screen

## Ruleset Import

Three bundled templates:

- **D&D 5e (SRD)** — 9 races, 19 weapons, 12 armor sets, 14 spells
- **DSA 5 (abstracted)** — 12 peoples, 15 weapons, 7 armor sets, 12 spells
- **Generic Fantasy** — 5 races, 10 weapons, 5 armor sets, 10 spells

Custom rulesets importable as JSON (`File > Import Ruleset`).

## Data Structure

```
rpx_pro_data/
  config.json          # Global settings
  worlds/              # World JSONs (locations, weapons, races, etc.)
  sessions/            # Session JSONs (characters, missions, chat)
  media/
    sounds/            # Sound effects (.mp3, .wav, .ogg)
    music/             # Background music
    images/            # Location/character images
    maps/              # World maps
  backups/             # Auto-backups
```

## Privacy & Local Data

RPX Pro runs entirely offline. Worlds, sessions, media, configuration, and backups stay in `rpx_pro_data/` on the device and are excluded from the repository via `.gitignore`. The AI integration generates prompts for use in an external tool; RPX Pro itself does not transmit this content to external services.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Session |
| Ctrl+O | Load Session |
| Ctrl+S | Save Session |

## Market Comparison

| Feature | RPX Pro | Roll20 | Foundry VTT | Fantasy Grounds |
|---------|:-------:|:------:|:-----------:|:---------------:|
| Offline-capable | ✓ | — | ✓ | ✓ |
| Light effects | ✓ | — | ~ | — |
| AI integration | ✓ | — | ~ | — |
| LLM API/CLI | ✓ | — | — | — |
| Hunger simulation | ✓ | — | — | — |
| Natural disasters | ✓ | — | — | — |
| 2nd monitor (dynamic) | ✓ | — | ~ | ~ |
| Modular/extensible | ✓ | — | ✓ | — |
| Free | ✓ | ~ | — | — |
| Open source | ✓ | — | — | — |

## License

MIT License — see [LICENSE](LICENSE).

RPX Pro is free software under the MIT License. You are free to use, modify, and redistribute it, including for commercial projects.

The ruleset templates contain only generic game mechanics. D&D content is based on SRD 5.1 (OGL). DSA content is abstracted and contains no protected text.

---

## Liability

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed. The MIT License disclaimer also applies.

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gilt der Haftungsausschluss der MIT-Lizenz.
