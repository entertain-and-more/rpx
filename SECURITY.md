# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

---

## English

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

### Reporting a Vulnerability

We take the security and privacy of **RPX Pro** and tabletop gaming campaigns seriously. If you discover a security vulnerability or exploit (including local path traversal, unsanitized rule set deserialization, unintentional network egress, or display leakage between GM and player screens), please report it responsibly.

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security issues through one of the following channels:
- **Email**: [security@open-bricks.org](mailto:security@open-bricks.org), [security@ellmos.ai](mailto:security@ellmos.ai), [support@lukasgeiger.com](mailto:support@lukasgeiger.com), or [lukas@open-bricks.org](mailto:lukas@open-bricks.org)
- **GitHub Security Advisory**: Open a private advisory via the [Security tab](https://github.com/entertain-and-more/rpx/security/advisories/new)

Please include:
1. Description of the vulnerability and affected subsystems (e.g. data manager, JSON-RPC CLI, bundle exporter, or PWA companion).
2. Step-by-step reproduction steps or proof-of-concept payload/bundle.
3. Potential impact on local file integrity, host privacy, or game master secrecy.

### Response Commitments & SLA

- **48-Hour Acknowledgment SLA**: We will acknowledge receipt of your report within 48 hours.
- **5-Business-Day Triage SLA**: Our maintainers will perform an initial technical triage, severity rating, and remediation estimate within 5 business days.
- **Regular Progress Updates**: We provide status updates every 7 business days until resolution.

### Security Invariants & Principles

- **Zero-Egress Data Protection (`INV-LOCAL-01`)**: All campaign data, maps, audio, characters, and configs remain strictly on local disk in `rpx_pro_data/`. Zero telemetry, zero analytics, zero external network requests.
- **Unprivileged Execution (`INV-USER-02`)**: Operates under standard OS user token (`RunAsInvoker`) without requiring administrator or root elevation.
- **Dual-Screen State Isolation (`INV-DUAL-03`)**: Strict window boundary isolation between the GM control dashboard and player screen (second monitor). Secret notes and monster stats never leak to player display without explicit GM action.
- **Headless CLI Boundaries (`INV-RPC-04`)**: Headless JSON-RPC CLI binds strictly to `stdin`/`stdout` without listening on network sockets.
- **Deterministic Bundle Export (`INV-BUNDLE-05`)**: Campaign bundles (`rpx-campaign-bundle-v1`) use safe ZIP decompression with strict path traversal checks.
- **Zero-Copyleft Isolation (`INV-COPYLEFT-07`)**: Core under MIT; PySide6 and pygame dynamically linked under LGPLv3 §4; campaign content remains 100% proprietary to the user.
- **Binding 48h Security SLA (`INV-SLA-10`)**: Continuous automated CI verification across Windows, Linux, and macOS.

### Statutory Disclaimer (§ 521 BGB)

This software is provided as an unremunerated open-source donation. In accordance with statutory law (§ 521 of the German Civil Code - BGB), liability of the author is strictly limited to intent and gross negligence. Use at your own risk.

---

## Deutsch

### Unterstützte Versionen

| Version | Unterstützt        |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

### Melden einer Sicherheitslücke

Wir nehmen die Sicherheit und den Datenschutz von **RPX Pro** und Pen-&-Paper-Kampagnen sehr ernst. Sollten Sie eine Sicherheitslücke oder Schwachstelle entdecken (z. B. Pfad-Traversal bei ZIP-Bündeln, Deserialisierungsrisiken, ungewollten Netzwerkabfluss oder Datenlecks zwischen Spielleiter- und Spieler-Bildschirm), melden Sie diese bitte verantwortungsvoll.

**Bitte melden Sie Sicherheitslücken NICHT über öffentliche GitHub Issues.**

Nutzen Sie stattdessen folgende vertrauliche Kanäle:
- **E-Mail**: [security@open-bricks.org](mailto:security@open-bricks.org), [security@ellmos.ai](mailto:security@ellmos.ai), [support@lukasgeiger.com](mailto:support@lukasgeiger.com) oder [lukas@open-bricks.org](mailto:lukas@open-bricks.org)
- **GitHub Security Advisory**: Erstellen Sie einen privaten Hinweis über den [Sicherheits-Reiter](https://github.com/entertain-and-more/rpx/security/advisories/new)

Bitte übermitteln Sie:
1. Beschreibung der Schwachstelle und betroffener Subsysteme (z. B. Datenverwaltung, JSON-RPC CLI, Bündel-Export oder PWA-Companion).
2. Schritt-für-Schritt-Anleitung zur Reproduktion oder Proof-of-Concept-Dateien.
3. Mögliche Auswirkungen auf Dateiintegrität, Privatsphäre oder Spielleiter-Geheimhaltung.

### Reaktionszusagen & Service-Level-Agreements (SLA)

- **48-Stunden-Eingangsbestätigung (SLA)**: Wir bestätigen den Eingang Ihres Hinweises garantiert innerhalb von 48 Stunden.
- **Verbindliche 5-Werktage-Triage-Zusage**: Innerhalb von 5 Werktagen schließen wir die technische Ersteinschätzung und Schweregrad-Einstufung ab.
- **Transparente Fehlerbehebung**: Sie erhalten regelmäßige Status-Updates bis zum Release des Sicherheits-Patches.

### Sicherheitsinvariante & Prinzipien

- **Zero-Egress Datenschutz (`INV-LOCAL-01`)**: Sämtliche Kampagnendaten, Karten, Töne, Charaktere und Konfigurationen verbleiben ausschließlich lokal im Verzeichnis `rpx_pro_data/`. Keine Telemetrie, keine Analyse, keine externen Netzwerkaufrufe.
- **Keine Privilegienerweiterung (`INV-USER-02`)**: Die Anwendung läuft strikt im Standard-Benutzerkontext (`RunAsInvoker`) ohne Administrator- oder Root-Rechte.
- **Bildschirm-Zustandsisolation (`INV-DUAL-03`)**: Strikte Fenstertrennung zwischen Spielleiter-Pult und Spieler-Bildschirm (Zweitmonitor). Spielleiter-Notizen und Monsterwerte lecken niemals unbefugt in die Spieleransicht.
- **Headless-CLI-Schutzgrenzen (`INV-RPC-04`)**: Die JSON-RPC-Schnittstelle arbeitet rein über Standard-I/O (`stdin`/`stdout`) ohne Netzwerk-Sockets.
- **Sicherer Bündel-Export (`INV-BUNDLE-05`)**: Kampagnenbündel (`rpx-campaign-bundle-v1`) nutzen validierte ZIP-Routinen mit Pfadtraversal-Schutz.
- **Zero-Copyleft-Isolation (`INV-COPYLEFT-07`)**: Kern unter MIT; PySide6 und pygame dynamisch gebunden gemäß LGPLv3 §4; Kampagneninhalte bleiben 100% Eigentum des Nutzers.
- **Verbindliche 48h-Sicherheits-SLA (`INV-SLA-10`)**: Kontinuierliche Testabsicherung über automatische GitHub Actions CI-Matrizen auf Windows, Linux und macOS.

### Gesetzlicher Haftungshinweis (§ 521 BGB)

Dieses Projekt ist eine unentgeltliche Open-Source-Schenkung im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gilt der Haftungsausschluss der MIT-Lizenz.
