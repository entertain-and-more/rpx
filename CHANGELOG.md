# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Repository Hygiene, CI Matrix Hardening & Invariant Governance (Pfad A) - 2026-10-04
- **Bilingual Contributing Guidelines & Invariants (`CONTRIBUTING.md`)**:
  - Implemented comprehensive bilingual (EN/DE) contributor guidelines specifying all 10 governance and runtime invariants (`INV-LOCAL-01` through `INV-SLA-10`), unprivileged user-mode `RunAsInvoker` non-elevation mode (`INV-USER-02`), Plan D local development workflow (`C:\_Local_DEV\repos\rpx`), § 521 BGB Gefälligkeitsrecht statutory limitation of liability, and binding 48h Security Response SLA (`security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`).
- **CI Lifecycle Automation Workflows & Dependabot Guard**:
  - Provisioned `.github/dependabot.yml` for automated weekly updates of `github-actions` (Monday 06:00 Europe/Berlin, limit 3 open PRs).
  - Provisioned `.github/workflows/auto-assign.yml` with concurrency and 5m timeout controls.
  - Provisioned `.github/workflows/label-sync.yml` and canonical `.github/labels.yml` with standard 11 governance labels.
- **Multi-Host Cloud-Sync, Lock & Desktop Defense (`.gitignore`)**:
  - Hardened `.gitignore` against Windows OS artifacts (`desktop.ini`, `ehthumbs.db`, `thumbs.db`), agent coordination artifacts (`TASKPLAN_*.md`, `*-TASKPLAN*`), multi-host conflict patterns (`*-IDEAPAD*`, `*-IDEAPAD-GEI*`, `*-IDEAPAD-GEI.*`), and canonical lock prefixes (`LOCK.dev.*`, `LOCK.antigravity.*`, `LOCK.bugsearch.*`).
- **PEP 621 Metadata Standardization & License Whitelist (`pyproject.toml`)**:
  - Whitelisted `CONTRIBUTING.md` in `license-files`.
  - Added canonical `Contributing` URL under `[project.urls]`.
  - Hardened pytest `norecursedirs` and ruff `exclude` with `.nyc_output`, `.tox`, `.turbo`.
  - Retained application version `1.0.0` strictly frozen per release discipline `T-20260920-167562623`.
- **Level 1 SBOM Re-Audit Stand 2026-10-04 (`THIRD_PARTY_LICENSES.txt`, `THIRD_PARTY_LICENSES.md`)**:
  - Re-audited Level 1 SBOM Stand 2026-10-04 with cross-reference to `CONTRIBUTING.md`, confirming 10 runtime invariants, zero-copyleft guarantee, and unprivileged execution.
- **Contract Test Suite Expansion (`tests/test_metadata_contract.py`)**:
  - Expanded automated contract test suite with tests validating bilingual `CONTRIBUTING.md` parity and invariants, CI lifecycle workflows, PEP 621 Contributing metadata, Level 1 SBOM recency, and multi-host lock defenses.

### Security & License Contract Audit - 2026-10-03
- **Dependency Security Floors & CVE Protection (`pyproject.toml`, `requirements-dev.txt`)**:
  - Hardened `pytest` version floor to `>=9.1.1` in `pyproject.toml` and new `requirements-dev.txt` to eliminate vulnerability CVE-2025-7117 / GHSA-6w46-j5rx-g56g.
  - Hardened `[tool.pytest.ini_options]` `minversion` from `7.0` to `9.1.1`.
  - Added structured `[project.optional-dependencies]` with explicit `dev` (`pytest>=9.1.1`, `ruff>=0.9.0`) and `build` (`pyinstaller>=6.10.0`, `pyinstaller-hooks-contrib>=2024.0`, `altgraph>=0.17.4`, `packaging>=24.0`, `setuptools>=61.0`) toolchain floors.
  - Added maintainer contact email (`support@lukasgeiger.com`) and direct GitHub `Security Advisories` URL to `pyproject.toml`.
- **Standardized 5-Field SBOM Software Inventory (`THIRD_PARTY_LICENSES.txt`)**:
  - Upgraded component and toolchain entries to the standardized 5-field schema (`Package:`, `License:`, `SPDX:`, `URL:`, `Notice:`) covering 14 components (`python-stdlib`, `PySide6`, `pygame`, `web-companion`, `pytest`, `pluggy`, `iniconfig`, `ruff`, `pyinstaller`, `pyinstaller-hooks-contrib`, `altgraph`, `packaging`, `setuptools`, `PowerShell`).
- **Repository Hygiene & `.gitignore` Hardening**:
  - Added explicit patterns for secrets and certificates (`secrets.*`, `*.cer`, `*.crt`), test output logs (`pytest_out.txt`, `pytest*.txt`), and multi-device cloud synchronization conflicts (`*.conflict`, `*-conflict-*`).
- **Automated Security & License Contract Test Suite (`tests/test_security_license_contract.py`)**:
  - Implemented 8 hermetic automated contract tests verifying dependency vulnerability floors, pytest minversion, 5-field SBOM completeness, bilingual security reporting SLAs, gitignore hygiene, zero hardcoded user paths or plaintext secrets, license parity, and local-first zero-egress invariants (8/8 passed).

### Bugsweep & Headless API/CLI Resilience Hardening - 2026-10-02
- **CLI JSON-RPC Request Validation & Thread Stability (`rpx_pro/cli.py`)**:
  - `CLIInterface.execute_command` now strictly validates incoming requests as dictionaries; non-dict payloads (strings, arrays, numbers, null) return clean JSON-RPC errors rather than raising unhandled `AttributeError: 'str' object has no attribute 'get'`.
  - In `CLIWorker._read_loop`, non-dict JSON lines are caught and reported without breaking out of the loop, preventing permanent termination of the background stdin listener thread.
  - Hardened `_dispatch` against `params: null` (None) and added support for JSON-RPC 2.0 array/positional parameters (`*params`), preventing `TypeError: argument after ** must be a mapping`. Zero-argument method wrappers (`list_worlds`, `list_locations`, `list_sessions`, etc.) now safely accept both positional and keyword arguments.
  - Headless CLI `--command` argument parser now strips surrounding shell quotes cleanly.
- **Character & Inventory Data Integrity (`rpx_pro/api.py`)**:
  - In `damage_character`, negative amounts (`amount < 0`) are defensively rejected with an error, preventing uncapped healing exploits where character HP could exceed `max_health`.
  - In `heal_character`, negative amounts (`amount < 0`) are defensively rejected, preventing unintended HP reductions.
  - In `give_item`, removing items (`count < 0`) is clamped so inventory counts cannot become negative, and items reaching count 0 are cleanly purged from the character's inventory dictionary.
- **Combat Logic & Skill Definition Resilience (`rpx_pro/api.py`)**:
  - In `execute_attack`, defeated characters (`health <= 0`) are guarded: dead attackers cannot execute attacks, and dead defenders cannot be repeatedly targeted.
  - In `execute_attack`, skill bonus evaluation defensively verifies `isinstance(skill_def, dict)` and `isinstance(affects, (dict, list, set, tuple))`, preventing unhandled `AttributeError` crashes when worlds contain non-dict skill definitions.
- **Audio & Dice Fallback Resilience (`rpx_pro/api.py`)**:
  - In `play_sound` and `play_music`, empty or whitespace paths are rejected immediately, and target path resolution enforces `.is_file()`, preventing empty string inputs from resolving to the parent directory (`SOUNDS_DIR` / `MUSIC_DIR`) and attempting directory audio playback.
  - In `roll_dice`, fallback execution when `dice_roller` is `None` enforces `count = max(1, int(count))` and `sides = max(1, int(sides))`, preventing unhandled `ValueError` crashes on zero or negative dice sides.
- **Automated Regression Test Suite**:
  - Added 9 hermetic regression tests in `tests/test_bugsweep_api_and_cli_resilience_20261002.py` (all 9 passed; full suite 90 passed, 1 skipped).

### Discoverability, ASCII 4-View Topology Projection & Plain-Text Level 1 SBOM Companion (Pfad B) - 2026-09-30
- **ASCII Four-View Architectural Topology Projection**:
  - Implemented comprehensive bilingual ASCII Four-View Topology projection in Section 6 of `README.md` and `README_de.md` (`VIEW 1: CLIENT RUNTIMES, USER INTERFACES & AUTOMATION ENTRY POINTS`, `VIEW 2: RPX PRO SOVEREIGN CORE ENGINE & ORCHESTRATION PIPELINE`, `VIEW 3: RUNTIME PERSISTENCE, CAMPAIGN BUNDLES & LOCAL VAULT`, `VIEW 4: AIR-GAP DEFENSE PERIMETER, RUNASINVOKER & GOVERNANCE`; German `SICHT 1..SICHT 4`).
- **Plain-Text Level 1 SBOM Companion (`THIRD_PARTY_LICENSES.txt`)**:
  - Completely expanded canonical plain-text companion file with comprehensive dependency catalog, Level 1 SBOM Invariant Cross-Reference Matrix mapping all 10 governance and runtime invariants (`INV-LOCAL-01` through `INV-SLA-10`, all VERIFIED), unprivileged `RunAsInvoker` non-elevation certification, Zero-Copyleft isolation guarantee, full license texts (MIT, LGPL-3.0 dynamic linking terms, LGPL-2.1 dynamic linking terms, PSFL-2.0, Apache-2.0, BSD-3-Clause), statutory disclaimer (§ 521 BGB Gefälligkeitsrecht), and binding 48h Security Response SLA.
- **Level 1 SBOM in `THIRD_PARTY_LICENSES.md` & Canonical `NOTICE`**:
  - Re-audited `THIRD_PARTY_LICENSES.md` Stand 2026-09-30 with formal reciprocal linkage to `THIRD_PARTY_LICENSES.txt`.
  - Updated `NOTICE` to explicitly cite `THIRD_PARTY_LICENSES.txt`.
- **PEP 621 Metadata Expansion (`pyproject.toml`)**:
  - Added `Level 1 SBOM`, `Plain-Text License`, and `Third-Party Licenses (Text)` to `[project.urls]`.
  - Added `--basetemp=.pytest_temp` to pytest `addopts` for isolated build runs.
  - Retained version `1.0.0` frozen per release discipline T-20260920-167562623.
- **Context Index & Marketing Log (`llms.txt`, `MARKETING-LOG.txt`)**:
  - Updated `llms.txt` header to `## Last-checked: 2026-09-30` with Level 1 SBOM companion references.
  - Appended Section 8 audit log in `MARKETING-LOG.txt` Stand 2026-09-30.
- **Documentation Badges & Contract Tests**:
  - Synchronized Shields.io badges in `README.md` and `README_de.md` (`Verified-2026--09--30`, `Level 1 SBOM: Plain Text`).
  - Added 4 new contract tests to `tests/test_metadata_contract.py` validating ASCII 4-view topology projection, plain-text Level 1 SBOM invariant matrix and license texts, extended project URLs, and recency verification (all 82 tests passing, 100% green).

### Windows Store Readiness & Packaging Staging - 2026-09-29
- **Packaging Manifest & Desktop Bridge Hardening**:
  - Enhanced `store_package/RPX Pro/AppxManifest.xml` with `ProcessorArchitecture="x64"`, `TargetDeviceFamily Windows.Desktop` (10.0.17763.0 to 10.0.26100.0), `<Logo>icons\\StoreLogo.png</Logo>`, and declared restricted capability `<rescap:Capability Name="runFullTrust"/>`.
  - Enriched `store_package.json` with `store_id: TBD`, `execution_alias: rpx.exe`, `logo: icons/StoreLogo.png`, and `languages: ["de-DE", "en-US", "es-ES"]`.
- **Packaging Staging (`releases/windowsstore/`)**:
  - Established dedicated release staging structure including `BUILD.md`, `WACK_PROTOCOL.md`, `store_settings.json`, `store_listing_de.md`, and `store_listing_en.md`.
  - Harmonized Microsoft Partner Center Policy 10.1.3 search terms to exactly 7 trademark-free keywords per language (DE: `pen and paper, rollenspiel, spielleiter, soundboard, virtueller spieltisch, charakterbogen, wuerfelsystem`; EN: `pen and paper, role playing game, game master, soundboard, virtual tabletop, character sheet, dice roller`).
  - Staged verified 1600x960 high-resolution presentation screenshots (`01-main-window.png` to `05-ai-prompts.png`).
- **Store Tile Assets & Icons**:
  - Populated all canonical tile assets in dual naming convention (`StoreLogo.png` 50x50, `Square44x44Logo.png`, `Square50x50Logo.png`, `Square150x150Logo.png`, `Wide310x150Logo.png`, `Square310x310Logo.png`).
- **Tooling & Preflight Automation**:
  - Implemented `scripts/run_windows_wack.py` with automatic Windows SDK detection, admin check, dry-run, and XML/JSON report generator.
  - Implemented 9-point store readiness auditor `scripts/check_store_readiness.py` reporting 0 findings (PASS).
  - Generated hermetic WACK preflight report `releases/windowsstore/test_reports/wack_preflight_20260929.xml` and `.json` (6 PASS, 0 FAIL).
  - Added contract tests in `tests/test_store_readiness.py` validating packaging, tile assets, manifest, and WACK preflight integrity.
- **Plan-D Anchor & Governance Documentation**:
  - Created canonical `REPO.pointer.json` (`ellmos-repo-pointer-v1`) linking to `entertain-and-more/rpx`.
  - Created bilingual `SUPPORT.md` and comprehensive `WINDOWS_STORE_PREP.md`.

### Security & Resilience Hardening: Campaign Bundle Zip-Slip Prevention & Persistence Isolation - 2026-09-29
- **Zip-Slip & Path Traversal Prevention in Campaign Bundles**:
  - Hardened `DataManager._prepare_import_media_target`, `_normalize_bundle_media_path`, `_build_bundle_media_path` and `_bundle_media_candidates` to strictly forbid directory traversal components (`..`), absolute anchors, and drive specifications, ensuring all extracted media files resolve strictly inside `MEDIA_DIR`.
  - Added strict validation to `import_campaign_bundle` for entity IDs (`world_id`, `session_id`), preventing directory traversal via malicious identifiers.
  - Hardened `_resolve_ruleset_target` to require `.json` extension, reject path traversal, and verify JSON payload validity before disk extraction.
- **Archive Integrity & Error Handling**:
  - `_load_bundle_manifest` and `_load_bundle_json` now defensively check archive membership and catch decode/syntax errors, raising descriptive `ValueError` rather than unhandled `KeyError` or `JSONDecodeError`.
- **Atomic Config Persistence & Cascading Cleanup**:
  - `save_config` now writes atomically via temporary file and `os.replace` to prevent config corruption during unexpected termination, and preserves active world/session pointers during headless invocations.
  - `delete_world` and `delete_session` now persist pointer resets (`last_world_id`, `last_session_id`) to disk via `save_config`.
  - `_write_snapshot` and `_create_unique_backup` validate `object_id` against directory traversal characters.
- **Automated Regression Test Suite**:
  - Added 7 dedicated security and resilience regression tests in `tests/test_campaign_bundle_security_and_resilience.py`.
  - Pytest test suite expanded to 72 passed, 1 skipped (100% green).

### Discoverability, 18-Point Bilingual Navigation & Level 1 SBOM Governance (Pfad B) - 2026-09-28
- **Bilingual 18-Point Quick Navigation Parity & Anchor Alignment**:
  - Implemented reciprocal dual HTML anchors `<a id="sec-01"></a>` through `<a id="sec-18"></a>` across all 18 primary documentation sections in both `README.md` and `README_de.md`.
  - Harmonized table of contents links to standardized `#sec-01` .. `#sec-18` targets, ensuring 1:1 cross-language navigation parity while preserving existing legacy anchors.
- **Canonical Root NOTICE & Attribution**:
  - Established canonical root `NOTICE` attribution file declaring Lukas Geiger, `entertain-and-more`, and `open-bricks` ecosystem under MIT license.
  - Linked `NOTICE` in `pyproject.toml` `license-files` whitelist and `[project.urls]`, `llms.txt`, and synchronized documentation badges.
- **PEP 621 Keywords Saturation & Topic Alignment**:
  - Saturated `pyproject.toml` keywords to 20 topics matching remote GitHub topics: `ai-integration`, `campaign-manager`, `desktop-app`, `game-master`, `json-rpc`, `local-first`, `offline-first`, `pen-and-paper`, `pwa-companion`, `pyside6`, `python`, `roleplay-xtreme`, `rpg`, `rpg-tools`, `rpx-pro`, `soundboard`, `tabletop`, `ttrpg`, `virtual-tabletop`, `zero-egress`.
  - Enhanced pytest configuration `norecursedirs` with `.pytest_temp`, `.pytest_tmp*`, `.hypothesis`.
  - Strictly preserved version freeze discipline (`version = 1.0.0` unchanged).
- **Level 1 SBOM Invariant Cross-Reference Matrix**:
  - Re-audited `THIRD_PARTY_LICENSES.md` as of 2026-09-28 with formal Level 1 SBOM Invariant Cross-Reference Matrix mapping all 10 governance invariants (`INV-LOCAL-01` to `INV-SLA-10`).
  - Formally certified unprivileged execution (`RunAsInvoker`), LGPL-3.0 dynamic linking compliance (LGPLv3 §4), and zero copyleft contamination for campaign data.
- **Statutory Liability Disclaimer & Binding 48h Security SLA**:
  - Integrated German statutory disclaimer under § 521 BGB (Gefälligkeitsrecht) into Section 18 of `README.md` and `README_de.md`, and updated `SECURITY.md`.
  - Formalized binding 48-Hour Acknowledgment and 5-Business-Day Triage Security Response SLA table in Section 18 and `SECURITY.md`.
- **Quality Gates & Contract Test Expansion**:
  - Expanded `tests/test_metadata_contract.py` with contract tests verifying canonical `NOTICE`, dual reciprocal HTML anchors `sec-01` .. `sec-18`, 20 PEP 621 keywords, Level 1 SBOM recency, and § 521 BGB / 48h SLA integrity.

### Tier-2 Multi-Language Expansion & Spanish Pen-&-Paper Localization (TW-RPG-10 / TW-RPG-11) - 2026-09-25
- Multi-Language Architecture & Policy P-006 Tier-2 Expansion:
  - Curated Spanish (s) Translation: Full curated Spanish localization for 100% of UI elements (171 catalog keys) covering Tabletop RPG terminology (Director de juego, Tirar dados, Control de rondas, Misiones, Inventario, Hechizos, Combate, etc.).
  - Preserved 6-Language Slot Contract: All 171 UI entries structured with complete 6-slot schemas (de, n, s, zh-Hans, ja, 
u).
  - Strict UI vs. Content Separation (TW-RPG-11): Static UI text is localized through 	ranslate_ui() / 	(), while dynamic campaign content, character sheets, lore, notes, chat, and imported rulesets remain strictly untranslated and user-governed (	ranslate_content(text) -> text).
- Encoding Hardening & Mojibake Resolution:
  - Completely resolved legacy Mojibake and double-encoded UTF-8 artifacts in locales/translations.json, guaranteeing pure UTF-8 encoding across all dictionary keys and values.
  - Hardened 	ranslator.py and manage_translations.py to prevent encoding regressions.
  - Added CLI validation gate: python manage_translations.py --check for automated slot and translation completeness verification.
- GUI Integration & Runtime Controls:
  - Added dedicated Language Menu Sprache in the main window menu bar with instant switching between German, English, and Spanish.
  - Integrated Sprache / Language / Idioma settings card with synchronized QComboBox into SettingsTab.
  - Added assistive status bar feedback on language changes.
- Automated Test Suite & Quality Gates:
  - Expanded 	ests/test_translation_contract.py with 6 automated contract tests covering catalog normalization, Spanish TTRPG terms, content preservation, and 100% catalog integrity.
  - Added 	ests/test_i18n_ui_integration.py for Qt signal and combobox UI integration.
  - Full pytest suite expanded to 62 passed, 1 skipped, 2 subtests (100% green).

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
