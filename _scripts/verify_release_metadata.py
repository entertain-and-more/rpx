"""Verify that release, publisher, privacy, and store metadata stay aligned.

This check deliberately validates documentation and package descriptors only. It
does not infer legal approval or a release from matching metadata; the explicit
``Unreleased`` status remains part of the contract until an authorised release
process changes it.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_VERSION = "1.0.0"
STORE_VERSION = "1.0.0.0"
PUBLISHER = "Geiger"
PUBLISHER_ID = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
PRIVACY_URL = "https://github.com/entertain-and-more/rpx/blob/master/PRIVACY_POLICY.md"
SUPPORT_URL = "https://github.com/entertain-and-more/rpx/issues"
PRIVACY_REVIEWED = "2026-08-10"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify(root: Path = ROOT) -> dict[str, Any]:
    """Return a compact readback summary or raise for the first mismatch."""

    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    constants = (root / "rpx_pro" / "constants.py").read_text(encoding="utf-8")
    package = json.loads((root / "store_package.json").read_text(encoding="utf-8"))
    privacy = (root / "PRIVACY_POLICY.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    readme_de = (root / "README_de.md").read_text(encoding="utf-8")
    listing = (root / "STORE_LISTING.md").read_text(encoding="utf-8")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    manifest_path = root / "store_package" / "RPX Pro" / "AppxManifest.xml"
    manifest_raw = manifest_path.read_text(encoding="utf-8")
    manifest = ET.fromstring(manifest_raw)

    pyproject_version = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    constants_version = re.search(r'^VERSION\s*=\s*"([^"]+)"', constants, re.MULTILINE)
    _require(pyproject_version is not None, "pyproject.toml has no project version")
    _require(constants_version is not None, "rpx_pro/constants.py has no VERSION")
    _require(pyproject_version.group(1) == APP_VERSION, "pyproject version drift")
    _require(constants_version.group(1) == APP_VERSION, "runtime version drift")

    _require(package["version"] == STORE_VERSION, "store package version drift")
    _require(package["publisher"] == PUBLISHER_ID, "store publisher identity drift")
    _require(package["publisher_display"] == PUBLISHER, "store publisher display drift")
    _require(package["privacy_url"] == PRIVACY_URL, "store privacy URL drift")
    _require(package["support_url"] == SUPPORT_URL, "store support URL drift")
    _require(package["release_status"] == "Unreleased", "store release status must remain Unreleased")
    _require(package["privacy_last_reviewed"] == PRIVACY_REVIEWED, "store privacy review date drift")

    ns = {"f": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}
    identity = manifest.find("f:Identity", ns)
    _require(identity is not None, "AppxManifest has no Identity")
    _require(identity.attrib.get("Publisher") == PUBLISHER_ID, "manifest publisher identity drift")
    _require(identity.attrib.get("Version") == STORE_VERSION, "manifest version drift")
    _require("Release status: Unreleased" in manifest_raw, "manifest release status note missing")

    _require(f"Last updated: {PRIVACY_REVIEWED}" in privacy, "privacy review date drift")
    _require("Release status: Unreleased" in privacy, "privacy release status missing")
    _require(PUBLISHER in privacy and PUBLISHER_ID in privacy, "privacy publisher metadata missing")
    _require(PRIVACY_URL in privacy and SUPPORT_URL in privacy, "privacy contact metadata drift")

    for name, document in (("README.md", readme), ("README_de.md", readme_de), ("STORE_LISTING.md", listing)):
        _require(APP_VERSION in document, f"{name} is missing application version")
        _require(STORE_VERSION in document, f"{name} is missing store version")
        _require(PUBLISHER in document and PUBLISHER_ID in document, f"{name} is missing publisher metadata")
        _require(PRIVACY_URL in document and SUPPORT_URL in document, f"{name} has stale contact metadata")
        _require("Unreleased" in document, f"{name} is missing English release status")
        _require("Unveröffentlicht" in document, f"{name} is missing German release status")
        _require(PRIVACY_REVIEWED in document, f"{name} is missing privacy review date")
        _require("no automatic data collection or transmission" in document or "keine automatische Datenerhebung oder Übertragung" in document,
                 f"{name} has no qualified data-transmission statement")
        _require("external AI" in document or "externen KI" in document,
                 f"{name} has no external-AI boundary statement")

    _require("## [Unreleased]" in changelog, "changelog Unreleased section missing")
    _require("release metadata" in changelog.lower(), "changelog metadata alignment entry missing")

    return {
        "application_version": APP_VERSION,
        "store_version": STORE_VERSION,
        "publisher": PUBLISHER,
        "publisher_id": PUBLISHER_ID,
        "privacy_reviewed": PRIVACY_REVIEWED,
        "release_status": "Unreleased",
    }


def main() -> int:
    try:
        result = verify()
    except (AssertionError, OSError, KeyError, json.JSONDecodeError, ET.ParseError) as exc:
        print(f"release metadata verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
