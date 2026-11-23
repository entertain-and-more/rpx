---
name: rpx-pro
category: games
description: Control RPX Pro (RolePlay Xtreme Professional Edition) programmatically via Python API or JSON-RPC CLI, manage tabletop RPG worlds, sessions, characters, combat, audio/soundboard cues, and exchange offline campaign bundles (rpx-campaign-bundle-v1) and companion player deltas (rpx-companion-delta-v1).
---

# RPX Pro — Agent & Developer Skill (`P-022`)

RPX Pro is a 100% local-first, zero-egress tabletop pen & paper RPG control center built with Python 3.10+ and PySide6 (Qt6), accompanied by a static offline Web/PWA Player Companion (`web_companion/`).

## Interfaces (`API + CLI + GUI + Offline PWA`)

1. **Desktop GUI (Game Master Workstation):**
   - Windows launcher: `START.bat`
   - Cross-platform Python entrypoint: `python RPX_Pro_1.py` (or `python -m rpx_pro.app`)
2. **Headless JSON-RPC CLI (`stdin`/`stdout` & one-shot `--command`):**
   - Single JSON-RPC call:
     ```bash
     python -m rpx_pro.cli --command '{"id": 1, "method": "list_worlds", "params": {}}'
     ```
   - Interactive line-delimited JSON-RPC stream:
     ```bash
     python -m rpx_pro.cli --interactive
     ```
   - Combined GUI + live stdin listener:
     ```bash
     python -m rpx_pro.app --cli
     ```
3. **Programmatic Python API (`RPXProAPI`):**
   ```python
   from rpx_pro.api import RPXProAPI
   from rpx_pro.managers.data_manager import DataManager

   dm = DataManager()
   api = RPXProAPI(data_manager=dm)
   world = api.create_world(name="Nordmark", genre="Fantasy")
   session = api.create_session(world_id=world["id"], name="Kapitel 1")
   ```
4. **Static Offline Web/PWA Companion (`web_companion/`):**
   - Serve locally via `cd web_companion && python -m http.server 8765`
   - Reads `rpx-campaign-bundle-v1` `.zip` files completely offline in the browser (`de`, `en`, `es`, `zh`, `ja`, `ru`) and optionally exports player notes and proposed character HP/Mana/Gold updates as `rpx-companion-delta-v1` `.json` files.

## Core JSON-RPC Methods

| Category | Methods |
|---|---|
| Worlds & Locations | `create_world`, `list_worlds`, `load_world`, `get_world`, `create_location`, `list_locations`, `set_location`, `set_environment` |
| Sessions & Characters | `create_session`, `list_sessions`, `load_session`, `get_session_state`, `create_character`, `get_character`, `heal_character`, `damage_character`, `get_inventory`, `give_item` |
| Combat & Dice | `get_combat_state`, `start_combat`, `next_turn`, `end_combat`, `execute_attack`, `roll_dice` |
| Audio, Chat & Missions | `list_sounds`, `play_sound`, `list_music`, `play_music`, `stop_music`, `set_volume`, `send_chat_message`, `get_chat_history`, `create_mission`, `complete_mission` |
| AI Prompts | `generate_start_prompt`, `generate_context_update` |
| Offline Bundles & Companion Deltas | `export_campaign_bundle`, `import_campaign_bundle`, `import_companion_delta` |

## Offline Roundtrip Workflow (`Desktop <-> PWA Companion`)

1. **Export Campaign Bundle on Desktop:**
   ```json
   {"id": 10, "method": "export_campaign_bundle", "params": {"destination": "exports/round1.zip", "include_media": "manifest"}}
   ```
2. **Player Mode on Mobile/Web (`web_companion/`):**
   - Load `round1.zip` via file picker or drag-and-drop.
   - Open **Player Mode**, record character HP/Mana/Gold adjustments or short table notes offline, and click **Export delta** (`*-companion-delta.json`, format `rpx-companion-delta-v1`).
3. **Non-Destructive Reimport on Desktop:**
   ```json
   {"id": 11, "method": "import_companion_delta", "params": {"source": "exports/round1-companion-delta.json"}}
   ```
   - Bounds character stats safely (`0 <= health <= max_health`, `0 <= mana <= max_mana`, `gold >= 0`), appends player notes idempotently (deduplicated via `companion_note_id`), and never overwrites worlds, maps, locations, or rulesets.

## Verification Gates

- Python unit & contract suite: `python -B -X utf8 -m pytest`
- Cross-platform source smoke (macOS/Linux/Windows): `python -B -X utf8 tests/source_platform_smoke.py`
- Web/PWA Companion suite & SW asset-hash guard: `node --test web_companion/tests/*.mjs`
- Windows Store readiness preflight: `python -B -X utf8 scripts/check_store_readiness.py`
