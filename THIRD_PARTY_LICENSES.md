# Third-Party Licenses & Transparency Notice

> **Project:** `entertain-and-more/rpx` (RPX Pro — RolePlay Xtreme Professional Edition)<br>
> **Audited:** 2026-09-14<br>
> **Repository License:** [MIT License](LICENSE)<br>
> **Architecture & Privacy:** 100% Local-First, Zero-Egress by default, Unprivileged User-Mode (`RunAsInvoker`)

---

## Executive Summary & Compliance Assurance

RPX Pro is an open-source, local-first tabletop pen & paper RPG control center. The core software is licensed under the permissive [MIT License](LICENSE).

All runtime and development dependencies utilized in RPX Pro are distributed under recognized open-source licenses (MIT, Apache-2.0, PSFL, LGPL-3.0, LGPL-2.1). 

- **PySide6 (Qt6 Python bindings)** is licensed under **LGPL-3.0**. PySide6 is used exclusively via dynamic linking (standard PyPI distribution / shared objects). No modifications to the Qt or PySide6 libraries are made. In full compliance with **LGPLv3 Section 4**, users and downstream developers are free to inspect, replace, and dynamically relink the Qt/PySide6 binaries.
- **pygame** is licensed under **LGPL-2.1** and is dynamically linked as an optional audio backend fallback.
- **Zero-Copyleft Contagion:** User campaigns, world maps, custom character sheets, JSON rulesets, and campaign bundles (`rpx-campaign-bundle-v1`) remain 100% proprietary to the user and are never subject to copyleft or relicensing.
- **Zero Egress & Unprivileged Execution:** RPX Pro executes with standard user privileges (`RunAsInvoker`) without requiring administrative elevation and performs zero automated outbound network requests.

Furthermore, RPX Pro affirms the ten governance and runtime invariants:
1. **INV-LOCAL-01 (100% Offline & Local-First Zero-Egress):** All campaign data, maps, audio, characters, and configs remain strictly on local disk in `rpx_pro_data/`. Zero telemetry, zero analytics, zero external network requests.
2. **INV-USER-02 (Unprivileged User-Mode & Non-Elevation):** Operates under strict `RunAsInvoker` security without requiring administrator privileges or root access.
3. **INV-DUAL-03 (Dual-Screen State Isolation & Mirroring):** Strict isolation between the GM control dashboard and the player screen (second monitor). Hidden GM notes, monster stats, and secret locations never leak to the player view without explicit action.
4. **INV-RPC-04 (Headless JSON-RPC CLI Interface):** Zero-dependency JSON-RPC interface via `stdin`/`stdout` (`python -m rpx_pro.app --cli`) enabling programmatic AI agent interaction, unit testing, and automation without opening the GUI.
5. **INV-BUNDLE-05 (Deterministic Campaign Bundle Export):** `rpx-campaign-bundle-v1` ZIP specification with checksums and manifest validation, enabling lossless cross-platform exchange between desktop and mobile companions.
6. **INV-PWA-06 (Zero-Cloud Client-Side PWA Companion):** Static PWA web companion running completely client-side in the browser via Service Worker; restores bundles from cache offline without internet access.
7. **INV-COPYLEFT-07 (Permissive Licensing & Dynamic Linking):** Core code under MIT; PySide6 (LGPL-3.0) and pygame (LGPL-2.1) dynamically linked under LGPLv3 §4; zero copyleft contamination for user campaigns.
8. **INV-LLM-08 (Privacy-Guarded AI Prompt Generation):** AI prompt generator formats structured prompts locally across 7 specialized RPG roles; prompts are copied to clipboard or read via CLI; zero automated data transmission to cloud AI endpoints.
9. **INV-ECO-09 (Modular Sibling Ecosystem Interoperability):** Full alignment with `entertain-and-more` and `open-bricks` ecosystem (e.g. KlangpultLight sound staging, shared JSON data interchange).
10. **INV-SLA-10 (Contractual Security SLA & Multi-Platform CI):** Formal commitment to 48-hour response / 5-day triage SLA, validated by automated GitHub Actions CI matrices across Ubuntu, Windows, and macOS on Python 3.10, 3.11, 3.12, and 3.13.

---

## Runtime Dependency Matrix

| Package | Version Range | Role / Functional Scope | License | Project Repository / Upstream | Compliance Mechanism |
|:---|:---|:---|:---|:---|:---|
| **Python Standard Library** | 3.10+ | Core desktop application, dataclass models, JSON serialization, SQLite persistence, CLI protocol | [PSFL-2.0](https://docs.python.org/3/license.html) | [python/cpython](https://github.com/python/cpython) | Standard library distribution |
| **PySide6** | >=6.5.0 | Desktop GUI framework (Qt6), widgets, multi-monitor display, Qt Multimedia audio | [LGPL-3.0](https://www.gnu.org/licenses/lgpl-3.0.html) | [Qt Project / PySide6](https://code.qt.io/cgit/pyside/pyside-setup.git/) | Dynamic linking (LGPLv3 §4), unprivileged user-mode |
| **pygame** | >=2.5.0 | Optional secondary audio playback fallback backend | [LGPL-2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html) | [pygame/pygame](https://github.com/pygame/pygame) | Dynamic linking, optional import |
| **Web Companion PWA** | Vanilla JS / HTML5 | Static companion client for bundle inspection (`web_companion/`) | [MIT](LICENSE) | Internal (`web_companion/`) | Zero external npm packages, client-side only |

---

## Development & Quality Assurance Tooling

| Package | Usage & Purpose | License | Source / Upstream |
|:---|:---|:---|:---|
| **pytest** | Automated test runner, contract verification suites, mock fixtures | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| **ruff** | High-performance Python linter and code formatting enforcement | [MIT / Apache-2.0](https://github.com/astral-sh/ruff/blob/main/LICENSE-MIT) | [astral-sh/ruff](https://github.com/astral-sh/ruff) |
| **setuptools** | Standard package build backend (PEP 517 / PEP 621 compliant) | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE) | [pypa/setuptools](https://github.com/pypa/setuptools) |
| **PyInstaller** | Executable packaging (`RPX_Pro.spec`) | [GPL-2.0 with Bootloader Exception](https://pyinstaller.org/) | [pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller) |

---

## LGPL Dynamic Linking Compliance Statement

PySide6 is distributed under the GNU Lesser General Public License Version 3 (LGPL-3.0). RPX Pro complies with LGPLv3 Section 4:
1. RPX Pro links dynamically to unmodified PySide6 shared libraries distributed by the official Python Package Index (PyPI).
2. Users are entitled to inspect, modify, and replace the PySide6 shared libraries in their Python virtual environment or system installation.
3. No proprietary or closed-source modifications to Qt/PySide6 are included or distributed by this repository.

---

## Full License Texts (Excerpts & Notices)

### 1. Python Software Foundation License Version 2 (PSFL-2.0)
Python standard library modules are used under the PSF License Agreement.  
Copyright (c) 2001-2026 Python Software Foundation. All rights reserved.

### 2. MIT License (MIT)
Used for the core RPX Pro codebase, `web_companion/`, `pytest`, `ruff`, and `setuptools`.

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  
>  
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  
>  
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### 3. GNU Lesser General Public License Version 3 (LGPL-3.0)
Applies to PySide6.  
Complete terms: https://www.gnu.org/licenses/lgpl-3.0.html

### 4. GNU Lesser General Public License Version 2.1 (LGPL-2.1)
Applies to pygame.  
Complete terms: https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html

### 5. Apache License Version 2.0 (Apache-2.0)
Co-licensed by `ruff`.  
Complete terms: https://www.apache.org/licenses/LICENSE-2.0
