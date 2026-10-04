# Contributing to RPX Pro

[English](#english) | [Deutsch](#deutsch)

---

<a id="english"></a>
## English

Thank you for your interest in contributing to **RPX Pro** (RolePlay Xtreme Professional Edition)!

### Architectural Principles & Governance Invariants

RPX Pro is an open-source, local-first control center for tabletop pen & paper RPG sessions. All contributions must respect all 10 foundational governance and runtime invariants:

1. **100% Offline & Local-First Zero-Egress (`INV-LOCAL-01`)**: All campaign data, maps, audio, characters, and configurations remain strictly on local disk in `rpx_pro_data/`. Zero external network telemetry, analytics, or background sockets.
2. **Unprivileged User-Mode & Non-Elevation (`INV-USER-02`)**: Executes strictly under `RunAsInvoker` in standard user space. Code must never require root, sudo, administrative rights, or UAC elevation.
3. **Dual-Screen State Isolation & Mirroring (`INV-DUAL-03`)**: Independent display router ensures GM prep, hidden stats, and fog-of-war locations never leak to the player view (second monitor) without explicit GM action.
4. **Headless JSON-RPC CLI Interface (`INV-RPC-04`)**: Standardized `stdin`/`stdout` JSON-RPC protocol (`rpx_pro.cli`) for autonomous AI agents, script automation, and headless testing without opening the GUI.
5. **Deterministic Campaign Bundle Export (`INV-BUNDLE-05`)**: Lossless export of worlds, sessions, and rulesets into portable, checksummed `rpx-campaign-bundle-v1` ZIP archives.
6. **Zero-Cloud Client-Side PWA Companion (`INV-PWA-06`)**: Static Web/PWA companion (`web_companion/`) operates 100% in-browser with Service Worker offline caching and zero remote server requests.
7. **Permissive Licensing & Dynamic Linking (`INV-COPYLEFT-07`)**: Core codebase is licensed under MIT. PySide6 (LGPL-3.0) and pygame (LGPL-2.1) are dynamically linked under LGPLv3 §4; zero copyleft contamination for user campaign data.
8. **Privacy-Guarded AI Prompt Generation (`INV-LLM-08`)**: 7 specialized local RPG prompt roles generate structured text locally for clipboard or CLI; zero automated transmission to cloud AI endpoints.
9. **Modular Sibling Ecosystem Interoperability (`INV-ECO-09`)**: Full interoperability and shared schemas with `entertain-and-more` and `open-bricks` sibling tools (e.g. KlangpultLight sound staging).
10. **Contractual Security SLA & Multi-Platform CI (`INV-SLA-10`)**: Binding 48h response / 5-day triage vulnerability SLA, validated by automated GitHub Actions CI matrices across Ubuntu, macOS, and Windows.

### Version Freeze & Release Governance

- **Version Freeze Policy (`T-20260920-167562623`)**: Version `1.0.0` is strictly frozen. Zero arbitrary version bumps. All improvements, CI hardening, and contract test expansions are documented under `## [Unreleased]` in `CHANGELOG.md`.

### Development & Quality Gates

- **Plan D Architecture**: Development, git operations, and tests occur strictly in the local git repository clone (`C:\_Local_DEV\repos\rpx`). GitHub remote `https://github.com/entertain-and-more/rpx.git` is origin.
- **Python Version Support**: Compatible with Python 3.10 through 3.13.
- **Pre-commit Quality Gates**:
  - Bytecode compilation: `python -m compileall -q .`
  - Linting: `ruff check .`
  - Automated test suite: `python -m pytest` (100% green required)
  - Whitespace hygiene: `git diff --check`
- **Security Vulnerabilities**: Please do not report security vulnerabilities publicly. Follow our [SECURITY.md](SECURITY.md) guidelines for responsible disclosure (48h response SLA) via `security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`, or `lukas@open-bricks.org`.

### Statutory Notice (§ 521 BGB)

Provided free of charge under the MIT License as open-source software. Under German statutory law (§ 521 BGB Gefälligkeitsrecht), liability in the case of gratuitous provision is limited to intent and gross negligence.

---

<a id="deutsch"></a>
## Deutsch

Vielen Dank für Ihr Interesse an einer Mitarbeit an **RPX Pro** (RolePlay Xtreme Professional Edition)!

### Architektur-Prinzipien & Governance-Invarianten

RPX Pro ist ein lokales, offline-fähiges Kontrollzentrum für Pen-&-Paper-Rollenspiele. Alle Beiträge müssen alle 10 grundlegenden Governance- und Laufzeit-Invarianten einhalten:

1. **100% Offline & Local-First Zero-Egress (`INV-LOCAL-01`)**: Sämtliche Kampagnendaten, Karten, Audiodateien, Charaktere und Konfigurationen verbleiben lokal in `rpx_pro_data/`. Keine Telemetrie, keine externen Netzwerkverbindungen.
2. **Unprivilegierter Modus & Keine Elevation (`INV-USER-02`)**: Läuft strikt unter `RunAsInvoker` im regulären Benutzerkontext. Niemals Administrator-, Root- oder UAC-Rechte anfordern.
3. **Zweischirm-Zustandsisolation & Spiegelung (`INV-DUAL-03`)**: GM-Vorbereitungen, geheime Notizen und Fog-of-War bleiben auf dem Hauptschirm isoliert und gelangen nie versehentlich auf den Spieler-Monitor.
4. **Headless JSON-RPC CLI-Schnittstelle (`INV-RPC-04`)**: Standardisiertes JSON-RPC-Protokoll via `stdin`/`stdout` (`rpx_pro.cli`) für autonome KI-Agenten, Skripte und automatisierte Tests ohne grafische Oberfläche.
5. **Deterministischer Kampagnen-Bundle-Export (`INV-BUNDLE-05`)**: Verlustfreier Export von Welten, Sessions und Regelwerken in portable, prüfsummenbasierte `rpx-campaign-bundle-v1` ZIP-Archive.
6. **Clientseitiger Offline-PWA-Begleiter (`INV-PWA-06`)**: Statische PWA-Webanwendung (`web_companion/`) läuft vollständig im Browser mit Service-Worker-Caching und null Serveranfragen.
7. **Freie Lizenzierung & Dynamische Verlinkung (`INV-COPYLEFT-07`)**: Kerncode unter MIT-Lizenz. PySide6 (LGPL-3.0) und pygame (LGPL-2.1) dynamisch verlinkt gem. LGPLv3 §4; null Copyleft-Ansteckung für Nutzerdaten.
8. **Datenschutzsichere KI-Prompt-Generierung (`INV-LLM-08`)**: 7 spezialisierte RPG-Prompt-Rollen erzeugen strukturierte Prompts lokal für Zwischenablage oder CLI; null automatische Übertragung an Cloud-KI.
9. **Modulare Geschwister-Ökosystem-Kompatibilität (`INV-ECO-09`)**: Nahtloses Zusammenspiel und gemeinsame Datenformate mit `entertain-and-more` und `open-bricks` (z. B. KlangpultLight).
10. **Vertragliche Sicherheits-SLA & Multi-Plattform-CI (`INV-SLA-10`)**: Verbindliche 48h-Erstantwort / 5-Tage-Triage-SLA, validiert durch automatisierte GitHub Actions CI auf Ubuntu, macOS und Windows.

### Versions-Freeze & Release-Governance

- **Version-Freeze-Regel (`T-20260920-167562623`)**: Version `1.0.0` ist strikt eingefroren. Keine Versionserhöhungen. Alle Verbesserungen, CI-Härtungen und Vertragstests werden unter `## [Unreleased]` in `CHANGELOG.md` gepflegt.

### Richtlinien für Entwickler

- **Plan D Architektur**: Entwicklung und Tests erfolgen ausschließlich im lokalen Git-Repository (`C:\_Local_DEV\repos\rpx`). GitHub `https://github.com/entertain-and-more/rpx.git` ist origin.
- **Python-Unterstützung**: Python 3.10 bis 3.13.
- **Qualitäts-Tore vor Commits**:
  - Bytecode-Prüfung: `python -m compileall -q .`
  - Linter: `ruff check .`
  - Testsuite: `python -m pytest` (100% grün erforderlich)
  - Whitespace-Prüfung: `git diff --check`
- **Sicherheitsmeldungen**: Sicherheitslücken bitte nicht öffentlich melden, sondern gemäß [SECURITY.md](SECURITY.md) vertraulich einreichen (48h Reaktions-SLA) an `security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com` oder `lukas@open-bricks.org`.

### Gesetzlicher Haftungsausschluss (§ 521 BGB)

Die Bereitstellung erfolgt unentgeltlich als Open-Source-Software unter den Bedingungen der MIT-Lizenz. Gemäß § 521 BGB (Gefälligkeitsrecht) ist die Haftung bei unentgeltlicher Überlassung auf Vorsatz und grobe Fahrlässigkeit beschränkt.
