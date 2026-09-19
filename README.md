<img src="assets/banner.svg" width="100%" alt="RPX Pro — RolePlay Xtreme Professional Edition" />

# RPX Pro — RolePlay Xtreme Professional Edition

[English](README.md) | [Deutsch](README_de.md)

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/entertain-and-more/rpx/releases)
[![Store Package](https://img.shields.io/badge/store%20package-1.0.0.0-informational.svg)](store_package.json)
[![Status](https://img.shields.io/badge/status-unreleased-yellow.svg)](SECURITY.md)
[![Pytest](https://img.shields.io/badge/pytest-32%20passed%20%7C%20100%25-brightgreen.svg)](tests/)
[![Web Companion](https://img.shields.io/badge/web%20companion-17%20passed-brightgreen.svg)](web_companion/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-blue.svg)](https://www.qt.io/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/entertain-and-more/rpx)
[![Privacy](https://img.shields.io/badge/privacy-100%25%20Local--First%20%7C%20Zero--Egress-success.svg)](#16-third-party-licenses--governance)
[![Security](https://img.shields.io/badge/security-RunAsInvoker%20%7C%20Non--Elevation-informational.svg)](SECURITY.md)
[![Security SLA](https://img.shields.io/badge/security%20SLA-48h%20%2F%205d-blue.svg)](SECURITY.md)
[![Third-Party Audited](https://img.shields.io/badge/third--party-audited%20%7C%20LGPL%20Dynamic-success.svg)](THIRD_PARTY_LICENSES.md)
[![Marketing Log](https://img.shields.io/badge/marketing%20log-active-blueviolet.svg)](MARKETING-LOG.txt)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![LLM Ready](https://img.shields.io/badge/llms.txt-ready-purple.svg)](llms.txt)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Org](https://img.shields.io/badge/org-entertain--and--more-0055ff.svg)](https://github.com/entertain-and-more)
[![Umbrella](https://img.shields.io/badge/umbrella-open--bricks-orange.svg)](https://github.com/open-bricks)

> Professional role-playing game control center for tabletop pen & paper adventures. Offline-capable, free, and open source.

### Release metadata

| Field | Value |
|-------|-------|
| Application version | `1.0.0` |
| Store package version | `1.0.0.0` |
| Release status | **Unreleased / Unveröffentlicht** (legal and store approval pending) |
| Publisher | Geiger (`CN=52596601-BAB4-4F3F-B182-E8F3F273B202`) |
| Privacy policy | [PRIVACY_POLICY.md](https://github.com/entertain-and-more/rpx/blob/master/PRIVACY_POLICY.md) |
| Support | [GitHub Issues](https://github.com/entertain-and-more/rpx/issues) |
| Privacy review | `2026-08-10` |

Privacy boundary: RPX Pro has no automatic data collection or transmission. It keeps campaign data local; prompts for an external AI tool are copied or shown locally and leave the device only when the user chooses to use that tool.

> [!NOTE]
> **Local-First & Machine-Readable Architecture**: RPX Pro runs 100% offline. All campaign data, maps, audio, and rulesets remain locally in `rpx_pro_data/`. For AI agents and external LLM workflows, RPX Pro provides a zero-dependency JSON-RPC CLI (`python -m rpx_pro.app --cli`) over `stdin`/`stdout` and exports standardized `rpx-campaign-bundle-v1` ZIP files readable by the offline PWA companion in `web_companion/`.

---

## Quick Navigation

1. [Overview](#1-overview)
2. [Key Features](#2-key-features)
3. [Target Personas & Discoverability](#3-target-personas--discoverability)
4. [Comparative Matrix vs. Alternatives](#4-comparative-matrix-vs-alternatives)
5. [Governance & Runtime Invariants](#5-governance--runtime-invariants)
6. [Visual Architecture](#6-visual-architecture)
7. [Session Lifecycle & Workflow](#7-session-lifecycle--workflow)
8. [Player Screen (Dual Monitor)](#8-player-screen-dual-monitor)
9. [CLI & API for LLM Integration](#9-cli--api-for-llm-integration)
10. [Web Companion PWA](#10-web-companion-pwa)
11. [Simulation & Game Mechanics](#11-simulation--game-mechanics)
12. [Ruleset System & Templates](#12-ruleset-system--templates)
13. [Installation & Quickstart](#13-installation--quickstart)
14. [Development & Test Suite](#14-development--test-suite)
15. [Sibling Ecosystem Matrix](#15-sibling-ecosystem-matrix)
16. [Third-Party Licenses & Governance](#16-third-party-licenses--governance)
17. [Security & Release Metadata](#17-security--release-metadata)
18. [License & Liability](#18-license--liability)

---

<a id="1-overview"></a>
## 1. Overview

RPX Pro (RolePlay Xtreme Professional Edition) is a comprehensive, open-source desktop control center designed for Game Masters (GMs / DMs) running tabletop pen & paper roleplaying games. Built with Python 3.10+ and PySide6 (Qt6), RPX Pro eliminates the chaos of juggling multiple browser tabs, PDF rulebooks, cloud subscriptions, and soundboard tools during live sessions.

The software operates on an uncompromising local-first architectural principle: every campaign world, map image, sound effect, character stat sheet, and transaction log is stored exclusively on your local filesystem in `rpx_pro_data/`. No account is required, no external server is queried, and no campaign notes ever leave your machine without your explicit export command.

![RPX Pro Main Window](README/screenshots/main.png)

---

<a id="2-key-features"></a>
## 2. Key Features

| Feature | Description |
|---------|-------------|
| **World System** | Multi-map world hierarchies, exterior and interior location views, nation lore, species, trigger automation |
| **Soundboard** | Multi-backend audio engine (Qt Multimedia, pygame, winsound fallback) with drag-and-drop triggers |
| **Light Effects** | Dynamic lightning flashes, strobe effects, day/night ambient color grading (mirrored to player display) |
| **Combat Engine** | Initiative tracking, multi-dice rolling (d4–d100), critical hit calculations, armor mitigation, weapons & spells |
| **Player Screen** | Dedicated 2nd-monitor display with tile, map, rotation, and image modes keeping GM notes secret |
| **Ruleset Importer** | Bundled D&D 5e (SRD 5.1), DSA 5 (abstracted), and Generic Fantasy templates, plus custom JSON imports |
| **AI Integration** | Prompt generator with 7 specialized RPG personas; copyable prompts with zero automated cloud transmission |
| **CLI / API for Agents** | Zero-dependency JSON-RPC CLI protocol over `stdin`/`stdout` for autonomous AI agents and headless automation |
| **PWA Web Companion** | Static client-side PWA reading local `rpx-campaign-bundle-v1` ZIP archives offline on mobile devices |
| **Session Manager** | Quest/mission logging, party grouping, round advancement, automated chat command logging |
| **Character Management**| Detailed attribute tracking, inventory modal with weight and gold limits, avatar previews, hunger/thirst meters |
| **Living Simulation** | Configurable time progression ratio, hunger/thirst decay rates, and random natural disaster events |

---

<a id="3-target-personas--discoverability"></a>
<a id="target-personas--discoverability"></a>
## 3. Target Personas & Discoverability

RPX Pro is engineered to address the specific requirements of four primary user personas across the tabletop gaming and development community:

| Persona ID | Target Audience | Primary Need | Key RPX Pro Architectural Solution |
|---|---|---|---|
| `[PERSONA-01]` | **Tabletop Pen & Paper Game Masters (GMs / DMs)** | All-in-one local control desk for live sessions with instant map projection, dynamic light/audio atmosphere, and party tracking. | Built-in soundboard, multi-map manager with exterior/interior locations, combat and dice roller, dynamic light effects, and dedicated 2nd-monitor player kiosk. |
| `[PERSONA-02]` | **Privacy-Conscious Players & Homebrew Lore Creators** | Absolute data privacy, local data sovereignty, and offline resilience for custom world lore, character sheets, and campaigns. | Strict 100% offline zero-network-egress design (`rpx_pro_data/`), MIT open-source license, and portable `rpx-campaign-bundle-v1` ZIP exports. |
| `[PERSONA-03]` | **Autonomous AI Agent Engineers & LLM Tool Builders** | Programmatic headless API to orchestrate AI dungeon masters, automated NPC dialogues, or campaign state inspection. | Standardized JSON-RPC CLI protocol over `stdin`/`stdout` (`python -m rpx_pro.app --cli`) exposing typed methods with zero GUI dependencies. |
| `[PERSONA-04]` | **Mobile Session Companions & Tablet Users** | Inspect character inventory, spell slots, and quest logs at the physical gaming table without complex server setups or subscriptions. | Zero-cloud static PWA companion (`web_companion/`) parsing `rpx-campaign-bundle-v1` ZIP files client-side with offline Service Worker caching. |

### High-Intent Search Queries

To facilitate technical discoverability across developer directories, package managers, and search engines:
- `open source tabletop RPG control center python pyside6` — Complete offline workstation for pen & paper game masters.
- `offline game master tools with second monitor player screen` — Multi-display session runner without subscription costs.
- `local-first virtual tabletop companion zero network egress` — Private campaign manager keeping lore strictly on local disk.
- `json-rpc cli tabletop rpg campaign manager for ai agents` — Headless programmatic backend for LLM dungeon masters.
- `rpx-campaign-bundle-v1 portable campaign format pwa` — Cross-platform campaign bundle specification and mobile viewer.
- `pyside6 qt6 roleplay xtreme pro ttrpg session manager` — Desktop application architecture featuring Qt6 signals and dataclass models.
- `dnd 5e dsa generic fantasy offline session manager` — SRD-compliant ruleset templates with JSON customizability.
- `multi-backend soundboard and dynamic light effects tabletop rpg` — Atmospheric multimedia integration for tabletop sessions.

---

<a id="4-comparative-matrix-vs-alternatives"></a>
<a id="comparative-matrix-vs-alternatives"></a>
## 4. Comparative Matrix vs. Alternatives

The following matrix compares RPX Pro against common virtual tabletop solutions and ad-hoc tools across 10 core technical dimensions directly mapped to our governance invariants:

| Technical Dimension | Governance Invariant | RPX Pro | Roll20 (Cloud SaaS VTT) | Foundry VTT (Self-Hosted Node.js) | Fantasy Grounds (Commercial Desktop) | Ad-Hoc Pen & Paper / Tools (Paper, Obsidian, Syrinscape) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. Offline-First & Zero Egress** | `INV-LOCAL-01` | **100% Offline (Local disk in `rpx_pro_data/`, zero telemetry)** | None (Mandatory cloud connection & remote asset hosting) | Partial (Requires local web server daemon & port forwarding) | Partial (Desktop app with mandatory cloud license checks) | High (Physical paper or offline markdown notes) |
| **2. Unprivileged Execution** | `INV-USER-02` | **Strict RunAsInvoker (Zero root/admin privilege required)** | Browser sandbox | Node.js daemon (potential port bind & firewall prompts) | Windows installer with admin privilege requests | Manual file edits |
| **3. Dual-Screen Player Display** | `INV-DUAL-03` | **Native Second Monitor (Kiosk/Tiles/Rotation with GM isolation)** | None (Requires second browser tab logged in as player) | None (Requires second browser window logged in as player) | Partial (Second instance connected over localhost) | None (Manual cardboard DM screen) |
| **4. Headless JSON-RPC for AI** | `INV-RPC-04` | **Built-in stdin/stdout JSON-RPC (`python -m rpx_pro.app --cli`)** | None (Closed web interface, API behind subscription) | Partial (JavaScript macros / third-party community modules) | None (Proprietary Lua engine without external CLI) | None (Purely manual) |
| **5. Deterministic Campaign Bundles** | `INV-BUNDLE-05` | **Standardized `rpx-campaign-bundle-v1` ZIP Specification** | None (Cloud-locked campaigns, no raw bundle export) | Partial (Complex world folders with database files) | Proprietary `.mod` / `.xml` campaign archives | Unstructured loose folders of docs and images |
| **6. Static Offline PWA Companion** | `INV-PWA-06` | **Zero-Cloud PWA (`web_companion/`) with Service Worker** | Closed mobile app requiring cloud account | None (Mobile browser access requires running server) | None (Desktop only) | Third-party note apps / PDF readers |
| **7. License & Pricing Model** | `INV-COPYLEFT-07` | **100% Free & Open Source (MIT License, zero subscriptions)** | Freemium with recurring monthly subscriptions ($5–$10/mo) | Commercial one-time purchase ($50 license fee) | Commercial software ($39–$149 + ruleset purchases) | Variable (physical books and stationery) |
| **8. Privacy-Guarded AI Integration** | `INV-LLM-08` | **7 Structured AI Roles with Zero Automatic Transmission** | None / Closed cloud AI betas | Third-party API plugins (external API key required) | None | Manual copy-paste to web LLMs |
| **9. Atmospheric Audio & Lights** | `INV-ECO-09` | **Integrated Soundboard (Qt/pygame) + Lightning/Strobe/Day-Night FX** | Basic web Jukebox (storage limited) | Module-based ambient audio playlists | Sound links via external Syrinscape integration | External Bluetooth speakers / separate apps |
| **10. Security SLA & Multi-OS CI** | `INV-SLA-10` | **48h SLA / 5d Triage + GitHub Actions CI (Ubuntu/macOS/Windows)** | SaaS platform customer ticket queue | Community Discord / vendor support | Proprietary vendor support forum | None (unmaintained personal tools) |

---

<a id="5-governance--runtime-invariants"></a>
<a id="governance--runtime-invariants"></a>
## 5. Governance & Runtime Invariants

RPX Pro enforces ten formal governance and runtime invariants across its architecture:

| Invariant ID | Canonical Name | Verification Mechanism | Architectural Rule |
|---|---|---|---|
| `INV-LOCAL-01` | **100% Offline & Local-First Zero-Egress** | Runtime isolation & test contract | All world, session, and character data remain in `rpx_pro_data/`. Zero remote phone-home or analytics. |
| `INV-USER-02` | **Unprivileged User-Mode & Non-Elevation** | Process security model | Operates strictly under `RunAsInvoker`; zero administrator elevation required for standard execution. |
| `INV-DUAL-03` | **Dual-Screen State Isolation & Mirroring** | Signal-based display router | GM prep, hidden monster stats, and unrevealed map fog never project to the 2nd monitor player view. |
| `INV-RPC-04` | **Headless JSON-RPC CLI Interface** | Stdio contract suite | Exposes programmatic `stdin`/`stdout` JSON-RPC protocol (`rpx_pro.cli`) for agentic and CLI operation. |
| `INV-BUNDLE-05` | **Deterministic Campaign Bundle Export** | Checksummed ZIP schema (`v1`) | Full export of worlds, sessions, and rulesets into portable `rpx-campaign-bundle-v1` format. |
| `INV-PWA-06` | **Zero-Cloud Client-Side PWA Companion** | Service Worker test suite | Static Web/PWA companion operates 100% in-browser with offline caching and zero server requests. |
| `INV-COPYLEFT-07` | **Permissive Licensing & Dynamic Linking** | SPDX license audit | Core MIT; PySide6 (LGPL-3.0) and pygame (LGPL-2.1) are dynamically linked under LGPLv3 §4 compliance. |
| `INV-LLM-08` | **Privacy-Guarded AI Prompt Generation** | Prompt generator unit tests | 7 AI personas generate copyable prompt text locally; zero automatic transmission to cloud LLM APIs. |
| `INV-ECO-09` | **Modular Sibling Ecosystem Interoperability** | Ecosystem matrix tests | Full interoperability with `entertain-and-more` and `open-bricks` sibling tools (e.g. KlangpultLight). |
| `INV-SLA-10` | **Contractual Security SLA & Multi-Platform CI** | Multi-OS GitHub Actions CI | 48h response / 5d triage commitment with continuous CI across Ubuntu, macOS, and Windows. |

---

<a id="6-visual-architecture"></a>
<a id="visual-architecture"></a>
## 6. Visual Architecture

```mermaid
flowchart TD
    subgraph UI["1. Desktop GUI Layer (PySide6 / Qt6)"]
        MW["MainWindow (Lean Orchestrator)"]
        T1["Chat Tab (Roles & Commands)"]
        T2["Views Tab (Locations, Ambience, PlayerScreen)"]
        T3["World Tab (Multi-Map, Locations Tree)"]
        T4["Characters Tab (Inventory, Stats)"]
        T5["Combat Tab (Dice Roller, Spells)"]
        T6["Missions & Settings Tabs"]
        MW --> T1 & T2 & T3 & T4 & T5 & T6
    end

    subgraph ENGINE["2. Business Logic & Managers"]
        DM["DataManager (JSON Persistence)"]
        AM["AudioManager (QtMultimedia / pygame)"]
        LM["LightManager (Lightning, Day/Night)"]
        PG["PromptGenerator (7 AI Personas)"]
        DR["DiceRoller (d4 - d100 Systems)"]
        API["RPXProAPI (Typed Contract Layer)"]
        MW <--> API
        API --> DM & AM & LM & PG & DR
    end

    subgraph HARDWARE["3. Hardware & Display Output"]
        M1["Primary Monitor (GM Control Desk)"]
        M2["Secondary Monitor (Player Screen Kiosk)"]
        SND["Audio Output (Speakers / Surround)"]
        MW --> M1
        T2 -->|Isolated Projector| M2
        AM --> SND
    end

    subgraph PROGRAMMATIC["4. External Agent & Programmatic Layer"]
        CLI["CLI Runner (rpx_pro.cli)"]
        STDIO["stdin / stdout JSON-RPC Protocol"]
        AGENTS["AI Agents / LLM Swarms (Claude, GPT, Gemini)"]
        AGENTS <-->|JSON-RPC| STDIO <--> CLI <--> API
    end

    subgraph STORAGE["5. Local Storage & Mobile Companion"]
        DATA["Local Directory (rpx_pro_data/)"]
        ZIP["rpx-campaign-bundle-v1 (.zip)"]
        PWA["Web PWA Companion (web_companion/)"]
        SW["Service Worker Cache (100% Offline)"]
        DM <--> DATA
        API -->|Export Bundle| ZIP
        ZIP -->|Import File| PWA <--> SW
    end
```

---

<a id="7-session-lifecycle--workflow"></a>
## 7. Session Lifecycle & Workflow

```mermaid
sequenceDiagram
    autonumber
    actor GM as Game Master
    participant GUI as RPX Desktop GUI
    participant API as RPXProAPI & Managers
    participant DISP as 2nd Monitor Player Screen
    participant CLI as JSON-RPC CLI / Agent
    participant PWA as Offline PWA Companion

    Note over GM,GUI: Session Setup Phase
    GM->>GUI: Launch RPX Pro (or START.bat)
    GUI->>API: Initialize DataManager (rpx_pro_data/)
    API-->>GUI: Local worlds & sessions loaded
    GM->>GUI: Open Player Screen on 2nd Display
    GUI->>DISP: Project clean player kiosk (maps & party)

    Note over GM,CLI: Live Session & AI Interaction
    GM->>GUI: Roll combat attack or trigger trap
    GUI->>API: DiceRoller.roll(2, 20)
    API-->>GUI: Combat results calculated
    GUI->>DISP: Broadcast damage overlay & play sound FX
    opt Programmatic AI Assistant
        CLI->>API: {"method": "generate_context_update", "params": {"role": "plot_twist"}}
        API-->>CLI: Formatted structured prompt
        CLI-->>GM: Narrative twist suggestion via chat
    end

    Note over GM,PWA: Campaign Export & Mobile Companion
    GM->>GUI: Export Campaign Bundle
    GUI->>API: Package rpx-campaign-bundle-v1.zip
    API-->>GM: Download bundle to USB / device
    GM->>PWA: Load ZIP bundle via drag-and-drop
    PWA->>PWA: Parse JSON manifest & cache offline
    PWA-->>GM: Mobile party status & map viewer ready
```

---

<a id="8-player-screen-dual-monitor"></a>
## 8. Player Screen (Dual Monitor)

The Player Screen is a dedicated, secondary monitor display designed to face the players at the table or stream via virtual webcam:
- **4 Display Modes**:
  - *Image*: Full-screen location concept art, NPC portraits, or item illustrations.
  - *Map*: Interactive world or dungeon map with pan, zoom, and player-revealed markers.
  - *Rotation*: Automatically cycles through active tiles on a configurable timer.
  - *Tiles*: Multi-panel dashboard displaying character party status, mission log, and current scene.
- **Dynamic View Toggles**: Checkboxes allow the GM to toggle party HP bars, active quests, chat log, turn order, location art, and inventory on the fly.
- **Atmospheric Mirroring**: Ambient lightning flashes, day/night color grading, and environmental strobe effects mirror instantaneously from the GM desk.
- **Complete Information Boundary**: GM notes, monster statblocks, encounter preparation, and unrevealed locations are strictly isolated and never shown on the player display.

---

<a id="9-cli--api-for-llm-integration"></a>
## 9. CLI & API for LLM Integration

RPX Pro provides a zero-dependency JSON-RPC protocol over standard input/output for automated testing and agentic integration:

```bash
python -m rpx_pro.app --cli
```

### Protocol Example

```json
{"id": 1, "method": "roll_dice", "params": {"count": 2, "sides": 20}}
{"id": 1, "result": {"dice": "2d20", "rolls": [14, 7], "total": 21}}
```

### Available Methods
- **Worlds & Sessions**: `create_world`, `list_worlds`, `load_world`, `create_session`, `list_sessions`, `load_session`
- **Party & Combat**: `create_character`, `get_character`, `heal_character`, `damage_character`, `get_inventory`, `give_item`, `roll_dice`
- **Chat & Logging**: `send_chat_message`, `get_chat_history`, `create_mission`, `complete_mission`
- **AI Personas**: `generate_start_prompt`, `generate_context_update`
- **Portable Bundles**: `export_campaign_bundle`, `import_campaign_bundle`

---

<a id="10-web-companion-pwa"></a>
## 10. Web Companion PWA

The static Web/PWA companion (`web_companion/`) provides a mobile interface for tablets and phones without needing a server daemon:
- **Zero-Cloud & 100% Client-Side**: Operates entirely in the browser using HTML5, CSS3, and modern JavaScript.
- **Service Worker Offline Cache**: Once loaded, the shell caches locally; subsequent visits load with zero network connectivity.
- **Bundle Restore**: Remembers and restores the last loaded `rpx-campaign-bundle-v1` ZIP archive across mobile restarts.
- **Safe-Area Layout**: Tailored for iOS and Android displays with responsive touch controls.

Local preview:
```bash
cd web_companion
python -m http.server 8765
```

---

<a id="11-simulation--game-mechanics"></a>
## 11. Simulation & Game Mechanics

- **Hunger & Thirst Progression**: Real-time simulation calculated in proportions to game time. Generates warnings at 50% and 75% thresholds with configurable race multipliers.
- **Dynamic Time Ratios**: Game time runs proportionally to real-world session time, triggering day/night visual overlays and day advancement announcements.
- **Natural Disasters**: Configurable environmental events (earthquakes, flash floods, storms, volcanic eruptions) accompanied by visual strobe flashes and chat logs.

---

<a id="12-ruleset-system--templates"></a>
## 12. Ruleset System & Templates

RPX Pro ships with three generic open-license templates:
1. **D&D 5e (SRD 5.1)** — 9 standard races, 19 weapons, 12 armor sets, 14 core spells.
2. **DSA 5 (Abstracted)** — 12 peoples, 15 weapons, 7 armor classifications, 12 spells.
3. **Generic Fantasy** — 5 fantasy archetypes, 10 weapons, 5 armor sets, 10 elemental spells.

Custom rulesets can be authored in JSON and imported via `File > Import Ruleset`.

---

<a id="13-installation--quickstart"></a>
## 13. Installation & Quickstart

```bash
# Clone repository
git clone https://github.com/entertain-and-more/rpx.git
cd rpx

# Install dependencies
pip install -r requirements.txt

# Launch GUI
python RPX_Pro_1.py
# or:
python -m rpx_pro.app
```

On Windows, simply double-click `START.bat`.

### Quickstart Guide
1. **Create a World**: Navigate to *World* tab > click *New World* > enter a realm name.
2. **Assign a Map**: Click *Load Map...* and select any image file (PNG/JPG/SVG).
3. **Add Locations**: Click *Add Location* to define towns, castles, or dungeons with exterior/interior views.
4. **Create a Session**: Select *File > New Session* and attach your world.
5. **Add Characters**: Under the *Characters* tab, create party members and NPCs.
6. **Launch Player Display**: Under *Views > Player Screen*, open the 2nd-monitor display for your players.

---

<a id="14-development--test-suite"></a>
## 14. Development & Test Suite

```bash
# Run Python contract and unit test suite
pytest

# Verify platform source smoke
pytest tests/test_source_platform_smoke.py

# Verify release metadata alignment
python _scripts/verify_release_metadata.py

# Run Web Companion PWA test suite
node --test web_companion/tests/*.mjs

# Code quality and linter checks
ruff check .
python -m compileall -q RPX_Pro_1.py rpx_pro tests
```

---

<a id="15-sibling-ecosystem-matrix"></a>
<a id="sibling-ecosystem-matrix"></a>
## 15. Sibling Ecosystem Matrix

RPX Pro functions as the entertainment and tabletop workstation anchor within the `entertain-and-more` and `open-bricks` ecosystem:

| Repository | Scope / Purpose | Synergy with RPX Pro |
|---|---|---|
| [`entertain-and-more/rpx`](https://github.com/entertain-and-more/rpx) | Tabletop RPG Session Control Center & GM Workstation | Primary application host |
| [`entertain-and-more/KlangpultLight`](https://github.com/entertain-and-more/KlangpultLight) | Lightweight Soundboard & Staging Audio Companion | Specialized companion for standalone live sound effects |
| [`file-bricks/SoftwareCenter`](https://github.com/file-bricks/SoftwareCenter) | Desktop Software & Portable Tool Launcher | One-click distribution and launch hub for RPX Pro |
| [`file-bricks/file-commander`](https://github.com/file-bricks/file-commander) | Local-First File & Asset Management Suite | High-speed campaign asset and sound library organizer |
| [`doc-bricks/FormularErstellen`](https://github.com/doc-bricks/FormularErstellen) | Offline Form & PDF Document Generator | Printable character sheet and handouts generator |
| [`ellmos-ai/ellmos-homebase-mcp`](https://github.com/ellmos-ai/ellmos-homebase-mcp) | Local-First Memory & Campaign Knowledge MCP | AI agent campaign memory backend |
| [`ellmos-ai/open-compute`](https://github.com/ellmos-ai/open-compute) | Desktop Automation & OS World Interaction Engine | Autonomous OS-level workflow orchestration |
| [`open-bricks`](https://github.com/open-bricks) | Umbrella Ecosystem for Modular Local-First Tools | Global open-source architectural standards |

---

<a id="16-third-party-licenses--governance"></a>
<a id="third-party-licenses--governance"></a>
## 16. Third-Party Licenses & Governance

RPX Pro is committed to total licensing transparency:
- **Core License**: [MIT License](LICENSE).
- **PySide6 (Qt6)**: LGPL-3.0 via official dynamic linking in full compliance with **LGPLv3 Section 4**. No modifications to Qt source libraries.
- **pygame**: LGPL-2.1 dynamic audio fallback.
- **Python Standard Library**: PSFL-2.0.
- **Full License Inventory**: See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) and [THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt).

---

<a id="17-security--release-metadata"></a>
<a id="security--release-metadata"></a>
## 17. Security & Release Metadata

- **Security Response SLA**: Contractual 48-hour acknowledgment, 5-day triage commitment (see [SECURITY.md](SECURITY.md)).
- **Unprivileged Execution**: Built for standard user execution (`RunAsInvoker`).
- **Release Status**: Currently **Unreleased / Unveröffentlicht** pending store and packaging sign-off.

---

<a id="18-license--liability"></a>
<a id="license--liability"></a>
## 18. License & Liability

MIT License — see [LICENSE](LICENSE).

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed. The MIT License disclaimer also applies.

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gilt der Haftungsausschluss der MIT-Lizenz.
