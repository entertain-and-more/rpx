"""Store Readiness Preflight Check for RPX Pro.

Validates that all necessary metadata, documentation files, licenses,
manifests, packaging staging, and icon/screenshot assets required for
Windows Store release are present, valid, and fully compliant with
Microsoft Store Policies (including Policy 10.1.3 Keyword Limits).
"""

from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
from typing import List, Tuple
import xml.etree.ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_KEYWORDS = {
    "microsoft",
    "windows",
    "word",
    "excel",
    "office",
    "powerpoint",
    "adobe",
    "acrobat",
    "apple",
    "google",
    "d&d",
    "dsa",
    "dungeons and dragons",
    "das schwarze auge",
}


def _png_size(path: Path) -> Tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if not header.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"{path.name} is not a PNG file")
    return struct.unpack(">II", header[16:24])


def check_store_package_json(project_root: Path) -> List[str]:
    errors = []
    file_path = project_root / "store_package.json"
    if not file_path.exists():
        errors.append("store_package.json is missing.")
        return errors

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"store_package.json is invalid JSON: {e}")
        return errors

    required_fields = [
        "app_name",
        "publisher",
        "publisher_display",
        "identity_name",
        "version",
        "description",
        "executable",
        "capabilities",
        "category",
        "age_rating",
        "license",
        "privacy_url",
        "support_url",
        "logo",
        "languages",
    ]
    for field in required_fields:
        val = data.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            errors.append(f"store_package.json field '{field}' is missing or empty.")
        elif field == "publisher" and not val.startswith("CN=52596601-BAB4-4F3F-B182-E8F3F273B202"):
            errors.append(f"store_package.json publisher '{val}' does not match canonical publisher DN.")

    return errors


def check_appx_manifest(project_root: Path) -> List[str]:
    errors = []
    manifest_path = project_root / "store_package" / "RPX Pro" / "AppxManifest.xml"
    if not manifest_path.exists():
        errors.append("store_package/RPX Pro/AppxManifest.xml is missing.")
        return errors

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
    except Exception as e:
        errors.append(f"AppxManifest.xml is invalid XML: {e}")
        return errors

    identity = root.find(".//{*}Identity")
    if identity is None:
        errors.append("AppxManifest.xml missing Identity element.")
    else:
        name = identity.attrib.get("Name", "")
        pub = identity.attrib.get("Publisher", "")
        ver = identity.attrib.get("Version", "")
        arch = identity.attrib.get("ProcessorArchitecture", "")
        if name != "Geiger.RPXPro":
            errors.append(f"AppxManifest Identity Name is '{name}', expected 'Geiger.RPXPro'.")
        if pub != "CN=52596601-BAB4-4F3F-B182-E8F3F273B202":
            errors.append("AppxManifest Identity Publisher mismatch.")
        if ver != "1.0.0.0":
            errors.append(f"AppxManifest Identity Version is '{ver}', expected '1.0.0.0'.")
        if arch != "x64":
            errors.append(f"AppxManifest Identity ProcessorArchitecture is '{arch}', expected 'x64'.")

    props = root.find(".//{*}Properties")
    if props is not None:
        logo = props.find(".//{*}Logo")
        if logo is None or logo.text != r"icons\StoreLogo.png":
            errors.append("AppxManifest Properties/Logo is not 'icons\\StoreLogo.png'.")

    cap = root.find(".//{*}Capability[@Name='runFullTrust']")
    if cap is None:
        errors.append("AppxManifest missing runFullTrust capability.")

    app = root.find(".//{*}Application")
    if app is not None:
        exec_name = app.attrib.get("Executable", "")
        if exec_name != "RPXPro.exe":
            errors.append(f"AppxManifest Executable is '{exec_name}', expected 'RPXPro.exe'.")

    return errors


def check_tile_assets(project_root: Path) -> List[str]:
    errors = []
    icons_dir = project_root / "store_package" / "RPX Pro" / "icons"
    if not icons_dir.exists():
        errors.append(f"Icons directory {icons_dir} does not exist.")
        return errors

    expected_sizes = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square50x50Logo.png": (50, 50),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "Square310x310Logo.png": (310, 310),
    }

    for name, expected in expected_sizes.items():
        file_path = icons_dir / name
        if not file_path.exists():
            errors.append(f"Tile icon missing: {name} in {icons_dir}")
            continue
        try:
            actual = _png_size(file_path)
            if actual != expected:
                errors.append(f"Tile icon {name} dimensions {actual} != expected {expected}")
        except Exception as e:
            errors.append(f"Tile icon {name} invalid PNG: {e}")

    return errors


def check_staging_directory(project_root: Path) -> List[str]:
    errors = []
    staging = project_root / "releases" / "windowsstore"
    if not staging.exists():
        errors.append(f"Staging directory missing: {staging}")
        return errors

    required_files = [
        "BUILD.md",
        "WACK_PROTOCOL.md",
        "store_settings.json",
        "store_listing_de.md",
        "store_listing_en.md",
        "StoreLogo.png",
    ]
    for fn in required_files:
        if not (staging / fn).exists():
            errors.append(f"Staging file missing: {fn}")

    settings_file = staging / "store_settings.json"
    if settings_file.exists():
        try:
            s_data = json.loads(settings_file.read_text(encoding="utf-8"))
            if s_data.get("identity_name") != "Geiger.RPXPro":
                errors.append("store_settings.json identity_name mismatch")
            if s_data.get("version") != "1.0.0.0":
                errors.append("store_settings.json version mismatch")
        except Exception as e:
            errors.append(f"store_settings.json invalid JSON: {e}")

    return errors


def check_screenshots(project_root: Path) -> List[str]:
    errors = []
    staging_screenshots = project_root / "releases" / "windowsstore" / "screenshots"
    if not staging_screenshots.exists():
        errors.append(f"Screenshots directory missing: {staging_screenshots}")
        return errors

    pngs = list(staging_screenshots.glob("*.png"))
    if len(pngs) < 4:
        errors.append(f"Store submission requires at least 4 screenshots, found {len(pngs)}.")

    for png in pngs:
        try:
            w, h = _png_size(png)
            if w < 1366 or h < 768:
                errors.append(f"Screenshot {png.name} resolution {w}x{h} below minimum 1366x768.")
        except Exception as e:
            errors.append(f"Screenshot {png.name} invalid PNG: {e}")

    return errors


def check_keyword_compliance(project_root: Path) -> List[str]:
    errors = []
    for fn in ["store_listing_de.md", "store_listing_en.md"]:
        fpath = project_root / "releases" / "windowsstore" / fn
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        kw_section = False
        keywords = []
        for line in text.splitlines():
            if "schlüsselwörter" in line.lower() or "keywords" in line.lower():
                kw_section = True
                continue
            if kw_section and line.strip():
                keywords = [k.strip() for k in line.split(",") if k.strip()]
                break

        if len(keywords) != 7:
            errors.append(f"{fn}: Expected exactly 7 keywords (Partner Center 10.1.3), found {len(keywords)}.")

        for kw in keywords:
            if len(kw) > 30:
                errors.append(f"{fn}: Keyword '{kw}' exceeds 30 characters.")
            for fb in FORBIDDEN_KEYWORDS:
                if fb in kw.lower():
                    errors.append(f"{fn}: Keyword '{kw}' contains trademarked/forbidden word '{fb}'.")

    return errors


def check_wack_reports(project_root: Path) -> List[str]:
    errors = []
    reports_dir = project_root / "releases" / "windowsstore" / "test_reports"
    if not reports_dir.exists():
        errors.append("test_reports directory missing in staging.")
        return errors

    xmls = list(reports_dir.glob("wack_preflight_*.xml"))
    jsons = list(reports_dir.glob("wack_preflight_*.json"))
    if not xmls:
        errors.append("No WACK preflight XML reports found.")
    if not jsons:
        errors.append("No WACK preflight JSON summaries found.")

    for j in jsons:
        try:
            data = json.loads(j.read_text(encoding="utf-8"))
            if data.get("overall_result") != "PASS":
                errors.append(f"WACK report {j.name} overall_result is not PASS: {data.get('overall_result')}")
            if data.get("fail_count", 0) > 0:
                errors.append(f"WACK report {j.name} contains failures: {data.get('fail_count')}")
        except Exception as e:
            errors.append(f"WACK JSON report {j.name} invalid: {e}")

    return errors


def check_mandatory_documents(project_root: Path) -> List[str]:
    errors = []
    required_docs = [
        "PRIVACY_POLICY.md",
        "SUPPORT.md",
        "LICENSE",
        "THIRD_PARTY_LICENSES.txt",
        "WINDOWS_STORE_PREP.md",
    ]
    for doc in required_docs:
        if not (project_root / doc).exists():
            errors.append(f"Mandatory document missing: {doc}")

    return errors


def check_plan_d_pointer(project_root: Path) -> List[str]:
    errors = []
    pointer_file = project_root / "REPO.pointer.json"
    if not pointer_file.exists():
        errors.append("REPO.pointer.json is missing.")
        return errors

    try:
        data = json.loads(pointer_file.read_text(encoding="utf-8"))
        if data.get("schema") != "ellmos-repo-pointer-v1":
            errors.append(f"REPO.pointer.json schema is '{data.get('schema')}', expected 'ellmos-repo-pointer-v1'.")
        if data.get("repo_id") != "entertain-and-more/rpx":
            errors.append(f"REPO.pointer.json repo_id is '{data.get('repo_id')}', expected 'entertain-and-more/rpx'.")
    except Exception as e:
        errors.append(f"REPO.pointer.json invalid JSON: {e}")

    return errors


def run_all_checks(project_root: Path = PROJECT_ROOT) -> int:
    all_errors = []
    print(f"Auditing Windows Store Readiness for: {project_root.name}...")

    checks = [
        ("Store Package JSON", check_store_package_json),
        ("AppxManifest", check_appx_manifest),
        ("Tile Assets", check_tile_assets),
        ("Staging Directory", check_staging_directory),
        ("Screenshots", check_screenshots),
        ("Keyword Compliance (10.1.3)", check_keyword_compliance),
        ("WACK Reports", check_wack_reports),
        ("Mandatory Documents", check_mandatory_documents),
        ("Plan D Pointer", check_plan_d_pointer),
    ]

    for name, check_fn in checks:
        errs = check_fn(project_root)
        if errs:
            print(f"  [FAIL] {name}:")
            for e in errs:
                print(f"    - {e}")
            all_errors.extend(errs)
        else:
            print(f"  [PASS] {name}")

    print("-" * 60)
    if all_errors:
        print(f"STORE READINESS: FAILED with {len(all_errors)} findings.")
        return 1
    else:
        print("STORE READINESS: OK — All 0 findings. Ready for packaging and Store submission.")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_checks())
