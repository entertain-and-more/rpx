# RPX Pro - RolePlay Xtreme Professional Edition

A professional role-playing control center for pen & paper adventures. Offline-capable, free, open source.

## Features

| Feature | Description |
|---------|-------------|
| **World System** | Multi-map support, locations (exterior/interior views), nations, peoples, trigger automation |
| **Soundboard** | Multi-backend audio (Qt Multimedia, pygame, winsound) |
| **Light Effects** | Lightning, strobe, day/night cycle, color filters (configurable for player screen) |
| **Combat System** | Weapons, armor, magic, combat techniques, configurable dice system |
| **Player Screen** | Separate monitor with dynamic views (tiles, rotation, images) |
| **Ruleset Import** | D&D 5e, DSA 5, Generic Fantasy (or custom JSON templates) |
| **AI Integration** | Prompt generator with 7 specialized AI roles |
| **CLI/API** | JSON-RPC CLI for LLM control via stdin/stdout |
| **Session Manager** | Missions, groups, turn management |
| **Characters** | Attributes, inventory dialog, gold, avatar, hunger/thirst simulation |
| **Simulation** | Hunger/thirst timer, time progression, natural disasters |

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python RPX_Pro_1.py
# or directly:
python -m rpx_pro.app
```

On Windows: double-click `START.bat`.

### Prerequisites

- Python 3.10+
- PySide6 (Qt6) - includes Qt Multimedia for audio
- pygame (optional, audio fallback)

## Quick Start

1. **Create a world**: World tab > "New World" > enter a name
2. **Add a map**: World tab > "Load Map..." > select an image file
3. **Create locations**: World tab > "Add Location" > use "Edit" to assign images/sounds
4. **Start a session**: File > New Session > select a world
5. **Create characters**: Characters tab > "Create Character" > use "Edit" to set details
6. **Start the game**: Toolbar > "Start Game" > AI prompt is copied to clipboard

## Architecture

RPX Pro is built as a modular Python package (`rpx_pro/`):

```
rpx_pro/
  app.py                     # Entry point
  main_window.py             # Lean orchestrator (~1200 lines)
  constants.py               # Configuration, paths, logging
  api.py                     # Programmatic Python API (JSON-serializable)
  cli.py                     # JSON-RPC CLI for LLM control
  models/                    # Data models (dataclasses)
    enums.py                 # MessageRole, PlayerScreenMode, DamageType, ...
    entities.py              # Character, Weapon, Armor, Spell, Item, ...
    world.py                 # World, Location, WorldSettings
    session.py               # Session, ChatMessage, Mission
  managers/                  # Business logic
    data_manager.py          # Persistence (JSON files)
    audio_manager.py         # Multi-backend audio
    light_manager.py         # Light effects (overlay-based)
    prompt_generator.py      # AI prompt generation
    dice_roller.py           # Dice system
  widgets/                   # Reusable UI components
    chat.py                  # Chat widget with role selection
    soundboard.py            # Drag & Drop soundboard
    player_screen.py         # Player screen (2nd monitor)
    map_widget.py            # Interactive map with drawing tools
    location_view.py         # Location view (exterior/interior)
    inventory_dialog.py      # Character inventory dialog
    prompt_widget.py         # AI prompt generator widget
    ruleset_importer.py      # Ruleset import
  tabs/                      # Standalone tab classes
    views_tab.py             # Views (location, inventory, ambience, player screen)
    world_tab.py             # World management + multi-map
    characters_tab.py        # Characters + inventory button
    combat_tab.py            # Combat + dice
    missions_tab.py          # Missions
    inventory_tab.py         # World item library
    immersion_tab.py         # Soundboard
    settings_tab.py          # Session/world settings
```

**Design Principles:**
- Tabs communicate exclusively via Qt Signals (no `self.window()`)
- Managers are passed via dependency injection
- MainWindow is a pure orchestrator (connects signals, routes events)
- Models are pure dataclasses with `to_dict()`/`from_dict()` serialization

## Tab Overview

### Chat (Tab 1)
- Messages with different roles (player, GM, AI roles, narrator)
- Color coding by role
- Chat commands: `/roll`, `/heal`, `/damage`, `/check`, `/give`
- System events are logged automatically

### Views (Tab 2)
Four sub-tabs in one:

- **Location View**: Exterior/interior view with blackout transition, color filter, triggers
- **Inventory View**: Character dropdown, inventory table (name, quantity, weight, value), gold
- **Ambience**: Light effects (lightning, strobe, day/night, color filter) + background music (playlist, volume)
- **Player Screen**: Monitor selection, fullscreen, display mode, view checkboxes, effect mirroring

### World (Tab 3)
- Create, edit, save worlds
- **Multi-Map System**: Multiple maps per world (world map, dungeons, cities)
- Interactive map with drawing tools
- Manage locations in a tree with edit dialog

### Characters (Tab 4)
- Table of all characters with core data
- **Inventory Button** per row -- opens the inventory dialog with gold, weight, items
- Edit dialog: name, race, class, level, HP, mana, skills, NPC status, image, biography
- Quick HP/mana controls (damage, heal, mana)

### Combat (Tab 5)
- Dice system (1-10 dice, D4 to D100)
- Attack mechanics with accuracy, critical hits, armor
- Weapon and spell lists

### Missions (Tab 6)
- Active and completed missions
- Complete or mark as failed
- Status changes logged in chat

### Inventory (Tab 7)
- World item library (name, class, weight, value, bonuses)
- Items at locations with find probability
- NPCs at locations with encounter probability

### Soundboard (Tab 8)
- Add sound effects via drag & drop or dialog
- Play/stop per sound

### AI Prompts (Tab 9)
- 7 AI roles: Storyteller, Plot Twist, Game Master, Opponents, NPCs, Landscape, Fauna/Flora
- Generate game start prompt and update prompt
- Copy to clipboard

### Settings (Tab 10)
- Session: Turn mode, actions/turn, game master (human/AI)
- World: Time ratio, hours/day, hunger/thirst simulation, natural disasters

## Player Screen (2nd Monitor)

The GM can open a separate screen for players (Views > Player Screen):

- **4 Display Modes**: Image, map, rotation, tiles
- **Dynamic Views**: Select via checkboxes which tiles are active
  - Characters (hero overview with HP/mana bars)
  - Missions (active quests)
  - Map (world map with markers)
  - Chat (game log)
  - Turn Control (round/turn order)
  - Location View (current location)
  - Inventory (character inventory)
- **Rotation**: Only activated views are cycled through
- **Event Overlay**: Announcements for damage, healing, death, missions, rounds
- **Effect Mirroring**: Lightning, day/night, color filter individually controllable
- Monitor selection, fullscreen, black screen

## CLI / API for LLM Integration

RPX Pro offers a programmatic API and a CLI interface for AI control:

```bash
# Start with CLI
python -m rpx_pro.app --cli
```

**JSON-RPC Protocol** via stdin/stdout:

```json
{"id": 1, "method": "roll_dice", "params": {"count": 2, "sides": 20}}
{"id": 1, "result": {"dice": "2D20", "rolls": [14, 7], "total": 21}}
```

**Available Methods:**
`create_world`, `list_worlds`, `load_world`, `create_session`, `list_sessions`, `load_session`,
`create_character`, `get_character`, `heal_character`, `damage_character`, `get_inventory`, `give_item`,
`send_chat_message`, `get_chat_history`, `roll_dice`, `create_mission`, `complete_mission`,
`generate_start_prompt`, `generate_context_update`

## Simulation

### Hunger/Thirst
- Increase proportionally to game time, warnings at 50% and 75%
- Rate per game hour configurable, race modifiers possible

### Natural Disasters
- Random events: earthquake, flood, volcanic eruption, tornado, etc.
- Visual strobe effect + chat message

### Time Progression
- Game time runs proportionally to real time (ratio configurable)
- Day change notifications, time of day on player screen

## Ruleset Import

Three included templates:

- **D&D 5e (SRD)** - 9 races, 19 weapons, 12 armor sets, 14 spells
- **DSA 5 (Abstracted)** - 12 peoples, 15 weapons, 7 armor sets, 12 spells
- **Generic Fantasy** - 5 races, 10 weapons, 5 armor sets, 10 spells

Custom rulesets can be imported as JSON (`File > Import Ruleset`).

## Data Structure

```
rpx_pro_data/
  config.json              # Global settings
  worlds/                  # World JSONs (locations, weapons, races, etc.)
  sessions/                # Session JSONs (characters, missions, chat)
  media/
    sounds/                # Sound effects (.mp3, .wav, .ogg)
    music/                 # Background music
    images/                # Location/character images
    maps/                  # World maps
  backups/                 # Auto-backups
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New session |
| Ctrl+O | Load session |
| Ctrl+S | Save session |

## Market Comparison

| Feature | RPX Pro | Roll20 | Foundry VTT | Fantasy Grounds |
|---------|:------:|:-----:|:-----------:|:---------------:|
| Offline-capable | x | - | x | x |
| Light effects | x | - | ~ | - |
| AI integration | x | - | ~ | - |
| LLM API/CLI | x | - | - | - |
| Hunger simulation | x | - | - | - |
| Natural disasters | x | - | - | - |
| 2nd monitor (dynamic) | x | - | ~ | ~ |
| Modular/extensible | x | - | x | - |
| Free | x | ~ | - | - |
| Open source | x | - | - | - |

## License

AGPL-3.0 - see [LICENSE](LICENSE).

RPX is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License (version 3 or later). For commercial use without copyleft obligation, contact the author.

The ruleset templates contain only generic game mechanics. D&D content is based on the SRD 5.1 (OGL). DSA content is abstracted and does not contain any copyrighted text.

---

Deutsche Version: [README.de.md](README.de.md)
