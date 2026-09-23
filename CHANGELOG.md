# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### CLI/LLM Game Master Interface & High-End Expansion (TW-RPG-08 / U2) - 2026-09-23
- Programmatic Game Master API (`RPXProAPI`):
  - **Soundboard & Audio Management**: Added `list_sounds`, `play_sound`, `list_music`, `play_music`, `stop_music`, and `set_volume` with multi-format audio discovery (`.mp3`, `.wav`, `.ogg`).
  - **Turn-Based Combat & Initiative Engine**: Added `start_combat` (with optional dexterity-based initiative ordering), `get_combat_state`, `next_turn` (with automatic round wrapping), `end_combat`, and `execute_attack` (supporting weapon accuracy thresholds, strength/dexterity skill bonuses, critical multipliers, armor reduction, character HP tracking, defeat detection, and automatic chat history logging).
  - **Worlds, Locations & Environment**: Added `get_world` (detailed world metadata), `create_location`, `list_locations`, `set_location`, `set_environment` (`WeatherType`, `TimeOfDay`), and `get_session_state` (comprehensive LLM context snapshot).
- Headless & CLI Execution (`rpx_pro.cli` & `rpx_pro.app`):
  - Added CLI dispatch for all new methods over JSON-RPC.
  - Added standalone headless runner supporting `--command '<JSON>'` and `--interactive` streaming stdin/stdout for headless agent execution.
  - Wired `audio_manager`, `dice_roller`, and `light_manager` through to `RPXProAPI` in GUI CLI mode.
- Test Coverage & Quality Gates:
  - Added comprehensive automated test suite `tests/test_api_cli_extended.py` covering audio, combat mechanics, world/location lifecycle, environment updates, and CLI JSON-RPC dispatch (total 57 passing tests).
  - 100% clean `ruff check` and `compileall`.

### Repository Hygiene, CI Matrix & Multi-Host Hardening (Pfad A) - 2026-09-21
- Linter & Code Hygiene: Resolved 6 unused imports in `tests/test_data_manager_persistence.py` (`json`, `tempfile`, `pathlib.Path`, `World`, `WorldSettings`, `Session`), achieving 100% clean `ruff check .` across the entire repository.
- CI Workflow Modernization & Guardrails: Fixed GitHub Actions versions in `.github/workflows/tests.yml` to official stable releases (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`), hardened `.github/workflows/stale.yml` with `timeout-minutes: 10`, and upgraded `.github/workflows/welcome.yml` to `actions/first-interaction@v3` with `timeout-minutes: 5` and concurrency cancellation.
- Multi-Host Cloud-Sync & Canonical Lock Defense: Hardened `.gitignore` with comprehensive multi-host conflict patterns (`*-WORKSTATION-LG*`, `*-LAPTOP*`, `*-ASUS-GEI*`, `*-Mac Studio*`, `*-MacBook*`), canonical lock protections (`LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`, `LOCK.permissions.json`), and test cache entries (`.hypothesis/`, `.nyc_output/`).
- Tooling & Packaging Hardening: Added `norecursedirs` to `pyproject.toml` `[tool.pytest.ini_options]` for isolated test execution, strictly preserving version freeze discipline (`version = 1.0.0` unchanged).
- Automated Contract Test Suite Expansion: Expanded `tests/test_metadata_contract.py` with contract tests verifying CI timeouts, action versions, stale/welcome guardrails, multi-host lock protections, and changelog/metadata recency.
- Documentation & Context Parity: Synchronized `llms.txt` (`Last-checked: 2026-09-21`), updated Pytest badges (48 passed) across `README.md` and `README_de.md`, and registered Pfad A audit in `MARKETING-LOG.txt`.

### Accessibility - 2026-09-17
- Die kompakte Hauptnavigation erklärt nun jeden Reiter per Tooltip und
  Accessible Name/Description. Dadurch bleiben die zehn textbasierten Reiter
  platzsparend, sind aber für Tastatur- und Screenreader-Nutzung besser einordenbar.

### Windows Store search terms - 2026-09-16
- Replaced third-party product titles in the German and English Store search terms with seven relevant phrases per language, each within the submission API's 30-character limit.

### Marketing, Discoverability, Visual Architecture & License Governance (Pfad B) - 2026-09-14
- Bilingual Quick Navigation & Anchor Parity: Implemented 18-point numbered quick navigation in both `README.md` and `README_de.md` with 100% mutual anchor parity and direct jump targets.
- Target Personas & High-Intent SEO Queries: Formulated 4 target personas (`[PERSONA-01]` to `[PERSONA-04]`) with detailed pain points, value propositions, and curated English and German high-intent search queries.
- 10-Dimension Comparative Matrix vs. 4 Alternatives: Mapped RPX Pro against Roll20, Foundry VTT, Fantasy Grounds, and Ad-Hoc Pen & Paper across 10 core architectural dimensions tied directly to formal governance invariants.
- 10 Governance & Runtime Invariants (`INV-LOCAL-01` to `INV-SLA-10`): Codified strict guarantees spanning 100% offline zero-egress, unprivileged `RunAsInvoker` execution, dual-screen isolation, headless JSON-RPC CLI, deterministic campaign bundles, static PWA companion, LGPL-3.0 dynamic linking, private AI prompts, sibling ecosystem synergy, and contractual security SLA.
- Visual Architecture & Session Lifecycle: Added dual Mermaid diagrams: system architecture flowchart and end-to-end game master session lifecycle sequence diagram with automated numbering.
- Third-Party License Audit & PEP 621 Alignment: Created `THIRD_PARTY_LICENSES.md` auditing PySide6 (LGPL-3.0 dynamic linking under LGPLv3 §4), pygame (LGPL-2.1), Python standard library (PSFL-2.0), and dev tooling, updated `pyproject.toml` URLs with "Third-Party Licenses", and refreshed `THIRD_PARTY_LICENSES.txt`.
- Contract Test Suite Expansion: Expanded `tests/test_metadata_contract.py` with 5 automated contract tests validating bilingual navigation parity, persona consistency, comparative matrix integrity, license documentation, and PEP 621 URLs.

### Repository Hygiene & CI Hardening (Pfad A) - 2026-09-12
- CI Workflow Hardening: Added concurrency cancellation (`cancel-in-progress: true`), job-level `timeout-minutes: 15` guardrails, Python 3.13 matrix extension, ruff lint step, full pytest run, and Web Companion PWA test job in `.github/workflows/tests.yml`.
- PEP 621 Standard-Metadaten & Linter-Konfiguration: Standardized `pyproject.toml` with `license-files = ["LICENSE"]`, extended `[project.urls]` (`Changelog`, `Security`, `LLM Ready`, `Parent Organization`, `Umbrella Ecosystem`, `Marketing Log`), Python 3.13 classifier, and formal `[tool.ruff]` / `[tool.ruff.lint]` configuration (`line-length = 100`, rule sets `["E", "F", "W", "B", "SIM", "C4"]`).
- Code Hygiene & Linter Cleanliness: Cleaned unused imports and resolved ruff issues across `rpx_pro/` and tools (100% clean across all rule sets).
- Multi-Host Cloud-Sync & Gitignore Hardening: Hardened `.gitignore` against cloud synchronization conflicts (`* (kopie)*`, `* (Kopie)*`, `*conflicted copy*`, `*-WORKSTATION*`, `*-ASUS*`, `*.orig`, `*.rej`), canonical lock files (`LOCK`, `LOCK.*`, `uv.lock`, `.automation-lock`), and test/build caches (`.tox/`, `.turbo/`).
- Contract Test Suite: Added automated contract tests in `tests/test_metadata_contract.py` validating CI timeouts, concurrency, PEP 621 URLs, gitignore patterns, and ruff configuration (27 passed total in Python test suite).
- Discoverability & Marketing Audit: Created comprehensive `MARKETING-LOG.txt`, updated `llms.txt` (`Last-checked: 2026-09-12`), and synchronized Pytest badges (27 passed) across `README.md` and `README_de.md`.

### Fixed
- Store-Screenshots verwenden jetzt native Qt-Glyphen mit
  `Qt.WA_DontShowOnScreen` statt des fehlerhaften offscreen-Renderers. Ein
  Selbsttest blockiert Tofu-Ausgaben; Statusleisten-Überlagerungen und helle
  Label-Hintergründe im Capture-Pfad sind beseitigt.
- Der `source-smoke`-Job installiert auf Linux jetzt die Qt-Systembibliotheken
  (`libegl1`, `libgl1`, `libxkbcommon-x11-0`, `libdbus-1-3`) und läuft mit
  `QT_QPA_PLATFORM=offscreen`. Der PySide6-Import scheiterte dort an
  `libEGL.so.1`; der Workflow war seit dem 2026-08-01 rot.

### Added
- Defined the macOS/Linux source smoke in `SOURCE_SMOKE_TEST.md`, added
  `tests/test_source_platform_smoke.py`, and wired a GitHub Actions
  `source-smoke` matrix for `ubuntu-latest` and `macos-latest`.
- Aligned release metadata across the privacy policy, store package,
  AppxManifest, README files, and store listing. The application remains
  explicitly **Unreleased** pending legal/store approval; no release is
  implied by this documentation check.

### Marketing & Discoverability
- Synchronized Shields.io badges in `README.md` and `README_de.md` with `entertain-and-more` organization and `open-bricks` ecosystem badges.
- Verified test suite status across Python Pytest (15 passed) and Node.js Web Companion PWA tests (17 passed, 32 total).
- Updated `llms.txt` header to `Last-checked: 2026-08-03` with updated test verification notes.

## [1.0.1] - 2026-07-25

### Marketing & Discoverability
- Integrated standard PEP 621 `pyproject.toml` with project metadata, dependencies, classifiers, and pytest configuration (`pythonpath = "."`).
- Added German landing page `README_de.md` with full parity, language switcher, badges, callouts, and Mermaid architecture diagram.
- Updated `README.md` with Shields.io badges (Pytest 9 passed, Web Companion 17 passed, PySide6, License, Python, Privacy, LLM Ready), language switcher, GitHub Alert Note callout, and Mermaid architecture & data flow diagram.
- Updated `llms.txt` header with `Last-checked: 2026-07-25`, verification status notes (26 passing tests), and link to `README_de.md`.

## [1.0.0] - 2026-07-23

### Documentation
- Added a README audience/use-case entry section and refreshed `llms.txt` discovery phrases for tabletop RPG, local-first game-master, PWA companion, and JSON-RPC LLM API searches.
- Restructured README.md to English-first; German documentation retained as collapsible secondary section.
- Added `llms.txt` with project description, tools, install instructions, audience, and search phrases.
- Standardized `llms.txt`: moved `Last-checked` header to first line, converted Search Phrases to fenced
  code block, added canonical repository URL and two additional search phrases.

### Maintenance
- Added `web_companion_FINAL_*/`, `*PREFIXBAK*`, and `docs/` to `.gitignore` to prevent stale build artifacts from being tracked.

### web_companion

- Bundle-Daten werden in den dynamischen Companion-Ansichten jetzt per
  `textContent`/DOM-Knoten statt per HTML-String gerendert.
- Fixed `skipWaiting()` race condition: moved into the `waitUntil` promise chain so the SW only advances to activate after all shell files are cached.
- Player Mode: Spieler können nach Bundle-Import ihren Charakter wählen und sehen eine portrait-optimierte Karte mit HP/Mana-Balken, Gold und aktiven Missionen.
- Neue `library.js`-Funktionen: `getCharacterList(bundle)` + `getPlayerView(bundle, sessionId, characterId)`.
- `apple-touch-icon` von SVG auf PNG korrigiert, weil iOS SVG dort ignoriert.
- Testsuite von 7 auf 10 Tests erweitert (`player.test.mjs` mit 5 Unit-Tests für neue library-Funktionen).
- Zuletzt geladenes Kampagnen-Bundle wird jetzt lokal gespeichert und bei Offline-Neustarts wiederhergestellt.
- Android-/iOS-PWA-Härtung ergänzt: `viewport-fit=cover`, Installhinweise, Safe-Area-Abstände und 44px-Touch-Ziele.
- Neuer `web_companion/PWA_TESTPLAN.md` beschreibt Bundle-Import, Touch-Layout, Installation und Offline-Start für Android/iOS.

### Store

- Reproduzierbaren Screenshot-Generator `generate_store_screenshots.py` für den Windows-Store-Strang ergänzt.
- Neues Screenshot-Set unter `README/screenshots/store/`: Hauptfenster, Weltkarte, Spieler-Bildschirm, Soundboard und KI-Prompts.
- Regressionstest `tests/test_store_screenshots.py` deckt PNG-Erzeugung, Mindestgröße und `summary.json` ab.

### Hinzugefügt / Added
- README-Hinweise für Screenshot, EXE-Build, lokales Datenschutzmodell und aktuelles GitHub-Repository ergänzt.
- GitHub Actions Syntax-Smoke-Test für Python 3.10-3.12 ergänzt.
- `EXPORTFORMAT.md` für `rpx-campaign-bundle-v1` ergänzt.
- Backend-Export für Kampagnen-Bundles mit Welten, Sessions, Regelwerken und optionalen Medien ergänzt.
- JSON-RPC-/API-Methode `export_campaign_bundle` ergänzt.
- JSON-RPC-/API-Methode `import_campaign_bundle` mit Konfliktstrategien `rename`, `replace` und `skip` ergänzt.
- Regressionstests für Bundle-Import, Medienextraktion und Legacy-Pfade ergänzt.
- Statischer Offline-Web/PWA-Companion unter `web_companion/` ergänzt: lokaler ZIP-Import für `rpx-campaign-bundle-v1`, Kampagnenübersicht, Welten-, Sessions-, Missions- und Regelwerk-Ansicht sowie Medienhinweise.
- PWA-Grundlagen mit `manifest.webmanifest`, Service Worker, SVG-Icons und Node-Regressionstests für ZIP-Leser und Shell-Dateien ergänzt.

### Geändert / Changed
- Store-Listing und Paketbeschreibung mit echten deutschen Umlauten abgeglichen.
- Portierungsplan für Windows Store, Web/PWA-Companion, Android/iOS-PWA-Testlinie sowie macOS-/Linux-Smoke-Tests ergänzt.
- README, `AUFGABEN.txt` und `PORTIERUNGSPLAN.md` auf den jetzt vorhandenen Web/PWA-Prototyp nachgezogen.
- `_WARTUNG/` und lokale Secret-/Cache-/Build-Artefakte werden ignoriert; bereits getrackte MSIX-Staging-Artefakte wurden aus dem Index entfernt.
- Security-, Privacy-, Contributing- und Code-of-Conduct-Dateien auf aktuelle Repository-Links und öffentliche Meldewege aktualisiert.
- Exportierte Welt- und Session-JSONs schreiben Medienpfade jetzt relativ als `media/...`, damit spätere Companion-Importer keine Desktop-Pfade voraussetzen.

### Behoben / Fixed
- Veraltete Legacy-Clone-Links und breit formulierte GPL/MIT/Apache-Haftungspassage bereinigt.
- Campaign-Bundle-Import normalisiert Bundle-Medienpfade jetzt auf lokale Desktop-Pfade und unterstützt auch ältere relative Pfade wie `maps/...` oder `images/...`.
