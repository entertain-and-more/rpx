"""Contract tests for Windows Store Readiness & Packaging Compliance."""

import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.check_store_readiness import run_all_checks

ROOT = Path(__file__).resolve().parents[1]


class StoreReadinessContractTests(unittest.TestCase):
    def test_store_readiness_auditor_zero_findings(self):
        exit_code = run_all_checks(ROOT)
        self.assertEqual(exit_code, 0, "check_store_readiness.py must report 0 findings")

    def test_appx_manifest_structure_and_capabilities(self):
        manifest_path = ROOT / "store_package" / "RPX Pro" / "AppxManifest.xml"
        self.assertTrue(manifest_path.exists())
        tree = ET.parse(manifest_path)
        root = tree.getroot()

        identity = root.find(".//{*}Identity")
        self.assertIsNotNone(identity)
        self.assertEqual(identity.attrib.get("Name"), "Geiger.RPXPro")
        self.assertEqual(identity.attrib.get("Publisher"), "CN=52596601-BAB4-4F3F-B182-E8F3F273B202")
        self.assertEqual(identity.attrib.get("Version"), "1.0.0.0")
        self.assertEqual(identity.attrib.get("ProcessorArchitecture"), "x64")

        props = root.find(".//{*}Properties")
        logo = props.find(".//{*}Logo")
        self.assertIsNotNone(logo)
        self.assertEqual(logo.text, r"icons\StoreLogo.png")

        cap = root.find(".//{*}Capability[@Name='runFullTrust']")
        self.assertIsNotNone(cap, "runFullTrust capability must be present")

        target = root.find(".//{*}TargetDeviceFamily")
        self.assertIsNotNone(target)
        self.assertEqual(target.attrib.get("Name"), "Windows.Desktop")
        self.assertEqual(target.attrib.get("MaxVersionTested"), "10.0.26100.0")

    def test_tile_icons_dimensions_and_presence(self):
        icons_dir = ROOT / "store_package" / "RPX Pro" / "icons"
        self.assertTrue((icons_dir / "StoreLogo.png").exists())
        self.assertTrue((icons_dir / "Square44x44Logo.png").exists())
        self.assertTrue((icons_dir / "Square50x50Logo.png").exists())
        self.assertTrue((icons_dir / "Square150x150Logo.png").exists())
        self.assertTrue((icons_dir / "Wide310x150Logo.png").exists())
        self.assertTrue((icons_dir / "Square310x310Logo.png").exists())

    def test_staging_directory_and_settings(self):
        staging = ROOT / "releases" / "windowsstore"
        self.assertTrue((staging / "BUILD.md").exists())
        self.assertTrue((staging / "WACK_PROTOCOL.md").exists())
        self.assertTrue((staging / "store_settings.json").exists())
        self.assertTrue((staging / "store_listing_de.md").exists())
        self.assertTrue((staging / "store_listing_en.md").exists())
        self.assertTrue((staging / "StoreLogo.png").exists())

        settings = json.loads((staging / "store_settings.json").read_text(encoding="utf-8"))
        self.assertEqual(settings.get("identity_name"), "Geiger.RPXPro")
        self.assertEqual(settings.get("version"), "1.0.0.0")
        self.assertIn("runFullTrust", settings.get("capabilities", ""))

    def test_wack_preflight_reports_valid(self):
        reports_dir = ROOT / "releases" / "windowsstore" / "test_reports"
        jsons = list(reports_dir.glob("wack_preflight_*.json"))
        self.assertGreaterEqual(len(jsons), 1, "At least one WACK preflight report must exist")
        data = json.loads(jsons[0].read_text(encoding="utf-8"))
        self.assertEqual(data.get("overall_result"), "PASS")
        self.assertEqual(data.get("fail_count"), 0)
        self.assertGreaterEqual(data.get("pass_count"), 6)

    def test_store_package_json_tier2_six_languages(self):
        pkg_file = ROOT / "store_package.json"
        self.assertTrue(pkg_file.exists())
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
        langs = set(data.get("languages", []))
        expected = {"de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"}
        self.assertTrue(expected.issubset(langs), f"Missing languages: {expected - langs}")

    def test_appx_manifest_tier2_resources(self):
        manifest_path = ROOT / "store_package" / "RPX Pro" / "AppxManifest.xml"
        self.assertTrue(manifest_path.exists())
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        resources = root.find(".//{*}Resources")
        self.assertIsNotNone(resources, "Resources element must be present in AppxManifest")
        langs = {r.attrib.get("Language") for r in resources.findall(".//{*}Resource") if r.attrib.get("Language")}
        expected = {"de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"}
        self.assertTrue(expected.issubset(langs), f"Missing Resource languages: {expected - langs}")

    def test_store_listing_has_tier2_six_languages(self):
        listing_path = ROOT / "STORE_LISTING.md"
        self.assertTrue(listing_path.exists())
        text = listing_path.read_text(encoding="utf-8")
        self.assertIn("## Deutsch", text)
        self.assertIn("## English", text)
        self.assertIn("## Español", text)
        self.assertIn("## 简体中文", text)
        self.assertIn("## 日本語", text)
        self.assertIn("## Русский", text)

    def test_staging_directory_has_six_language_listings(self):
        staging = ROOT / "releases" / "windowsstore"
        for lang in ["de", "en", "es", "zh", "ja", "ru"]:
            fpath = staging / f"store_listing_{lang}.md"
            self.assertTrue(fpath.exists(), f"Missing staging listing for {lang}: {fpath.name}")

    def test_plan_d_pointer_integrity(self):
        pointer = ROOT / "REPO.pointer.json"
        self.assertTrue(pointer.exists())
        data = json.loads(pointer.read_text(encoding="utf-8"))
        self.assertEqual(data.get("schema"), "ellmos-repo-pointer-v1")
        self.assertEqual(data.get("repo_id"), "entertain-and-more/rpx")
        self.assertEqual(data.get("local_locator", {}).get("repo_name"), "rpx")


if __name__ == "__main__":
    unittest.main()
