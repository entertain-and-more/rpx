"""Contract tests for repository hygiene, CI/CD guardrails, PEP 621 metadata, and Pfad B governance."""

import re
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_ci_workflows_have_concurrency_and_timeouts(self):
        tests_workflow = ROOT / ".github" / "workflows" / "tests.yml"
        self.assertTrue(tests_workflow.exists(), "tests.yml workflow must exist")
        content = tests_workflow.read_text(encoding="utf-8")

        self.assertIn("actions/checkout@v4", content)
        self.assertIn("actions/setup-python@v5", content)
        self.assertIn("concurrency:", content)
        self.assertIn("cancel-in-progress: true", content)
        self.assertIn("timeout-minutes: 15", content)
        self.assertIn("ruff check .", content)
        self.assertIn("web-companion:", content)

    def test_stale_workflow_present_and_configured(self):
        stale_workflow = ROOT / ".github" / "workflows" / "stale.yml"
        self.assertTrue(stale_workflow.exists(), "stale.yml workflow must exist")
        content = stale_workflow.read_text(encoding="utf-8")

        self.assertIn("actions/stale", content)
        self.assertIn("stale-issue-label", content)
        self.assertIn("timeout-minutes: 10", content)

    def test_welcome_workflow_present_and_configured(self):
        welcome_workflow = ROOT / ".github" / "workflows" / "welcome.yml"
        self.assertTrue(welcome_workflow.exists(), "welcome.yml workflow must exist")
        content = welcome_workflow.read_text(encoding="utf-8")

        self.assertIn("actions/first-interaction@v3", content)
        self.assertIn("timeout-minutes: 5", content)
        self.assertIn("concurrency:", content)
        self.assertIn("cancel-in-progress: true", content)

    def test_pyproject_pep621_compliance(self):
        pyproject_path = ROOT / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml must exist")

        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        self.assertEqual(project.get("name"), "rpx-pro")
        self.assertEqual(project.get("version"), "1.0.0")
        self.assertIn("license-files", project)
        self.assertEqual(project["license-files"], ["LICENSE"])

        classifiers = project.get("classifiers", [])
        self.assertIn("Programming Language :: Python :: 3.13", classifiers)

        urls = project.get("urls", {})
        expected_urls = [
            "Homepage",
            "Documentation",
            "Repository",
            "Issues",
            "Changelog",
            "Security",
            "LLM Ready",
            "Marketing Log",
            "Third-Party Licenses",
            "Parent Organization",
            "Umbrella Ecosystem",
        ]
        for key in expected_urls:
            self.assertIn(key, urls, f"pyproject.toml urls missing key: {key}")

        ruff = data.get("tool", {}).get("ruff", {})
        self.assertEqual(ruff.get("line-length"), 100)
        self.assertEqual(ruff.get("target-version"), "py310")
        lint = ruff.get("lint", {})
        self.assertIn("select", lint)
        self.assertIn("ignore", lint)

        pytest_config = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
        self.assertIn("norecursedirs", pytest_config)

    def test_gitignore_cloud_sync_and_lock_defense(self):
        gitignore_path = ROOT / ".gitignore"
        self.assertTrue(gitignore_path.exists(), ".gitignore must exist")
        content = gitignore_path.read_text(encoding="utf-8")

        expected_patterns = [
            "* (kopie)*",
            "* (Kopie)*",
            "*conflicted copy*",
            "*-WORKSTATION*",
            "*-WORKSTATION-LG*",
            "*-LAPTOP*",
            "*-ASUS*",
            "*-ASUS-GEI*",
            "*-Mac Studio*",
            "*-MacBook*",
            "LOCK",
            "LOCK.*",
            "LOCK.user.*",
            "LOCK.until.*",
            "LOCK.condition.*",
            "LOCK.permissions.json",
            "uv.lock",
            "!package-lock.json",
            ".automation-lock",
        ]
        for pattern in expected_patterns:
            self.assertIn(pattern, content, f".gitignore missing pattern: {pattern}")

    def test_bilingual_navigation_parity(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

        for i in range(1, 19):
            en_match = re.search(rf"^##\s+{i}\.\s+", readme_en, re.MULTILINE)
            de_match = re.search(rf"^##\s+{i}\.\s+", readme_de, re.MULTILINE)
            self.assertIsNotNone(en_match, f"README.md missing section ## {i}.")
            self.assertIsNotNone(de_match, f"README_de.md missing section ## {i}.")

        shared_anchors = [
            "target-personas--discoverability",
            "comparative-matrix-vs-alternatives",
            "governance--runtime-invariants",
            "visual-architecture",
            "third-party-licenses--governance",
            "sibling-ecosystem-matrix",
        ]
        for anchor in shared_anchors:
            self.assertIn(f'id="{anchor}"', readme_en, f"README.md missing anchor {anchor}")
            self.assertIn(f'id="{anchor}"', readme_de, f"README_de.md missing anchor {anchor}")

    def test_target_personas_and_high_intent_queries(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
        marketing_log = (ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

        personas = [
            "[PERSONA-01]",
            "[PERSONA-02]",
            "[PERSONA-03]",
            "[PERSONA-04]",
        ]
        for persona in personas:
            self.assertIn(persona, readme_en, f"README.md missing {persona}")
            self.assertIn(persona, readme_de, f"README_de.md missing {persona}")
            self.assertIn(persona, marketing_log, f"MARKETING-LOG.txt missing {persona}")

        self.assertIn("High-Intent Search Queries", readme_en)
        self.assertIn("Suchbegriffe & Auffindbarkeit", readme_de)
        self.assertIn("High-Intent English Search Queries", marketing_log)
        self.assertIn("High-Intent German Search Queries", marketing_log)

    def test_comparative_matrix_and_governance_invariants(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
        licenses_md = (ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
        marketing_log = (ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

        invariants = ["INV-LOCAL-01", "INV-USER-02", "INV-DUAL-03", "INV-RPC-04", "INV-BUNDLE-05",
                      "INV-PWA-06", "INV-COPYLEFT-07", "INV-LLM-08", "INV-ECO-09", "INV-SLA-10"]

        for inv in invariants:
            self.assertIn(inv, readme_en, f"README.md missing invariant {inv}")
            self.assertIn(inv, readme_de, f"README_de.md missing invariant {inv}")
            self.assertIn(inv, licenses_md, f"THIRD_PARTY_LICENSES.md missing invariant {inv}")
            self.assertIn(inv, marketing_log, f"MARKETING-LOG.txt missing invariant {inv}")

        alternatives = ["Roll20", "Foundry VTT", "Fantasy Grounds"]
        for alt in alternatives:
            self.assertIn(alt, readme_en, f"README.md missing alternative {alt}")
            self.assertIn(alt, readme_de, f"README_de.md missing alternative {alt}")
            self.assertIn(alt, marketing_log, f"MARKETING-LOG.txt missing alternative {alt}")

    def test_third_party_licenses_governance_and_compliance(self):
        licenses_md = ROOT / "THIRD_PARTY_LICENSES.md"
        licenses_txt = ROOT / "THIRD_PARTY_LICENSES.txt"
        self.assertTrue(licenses_md.exists(), "THIRD_PARTY_LICENSES.md must exist")
        self.assertTrue(licenses_txt.exists(), "THIRD_PARTY_LICENSES.txt must exist")

        content_md = licenses_md.read_text(encoding="utf-8")
        self.assertIn("PySide6", content_md)
        self.assertIn("LGPL-3.0", content_md)
        self.assertIn("Section 4", content_md)
        self.assertIn("pygame", content_md)
        self.assertIn("LGPL-2.1", content_md)
        self.assertIn("RunAsInvoker", content_md)

        content_txt = licenses_txt.read_text(encoding="utf-8")
        self.assertIn("THIRD_PARTY_LICENSES.md", content_txt)
        self.assertIn("PySide6", content_txt)

    def test_llms_txt_structure_and_parity(self):
        llms_path = ROOT / "llms.txt"
        self.assertTrue(llms_path.exists(), "llms.txt must exist")
        content = llms_path.read_text(encoding="utf-8")

        self.assertTrue(content.startswith("## Last-checked: 2026-09-21"), "llms.txt must have current date")
        self.assertIn("[PERSONA-01]", content)
        self.assertIn("INV-LOCAL-01", content)
        self.assertIn("THIRD_PARTY_LICENSES.md", content)

    def test_changelog_recent_pfad_a_entry(self):
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## [Unreleased]", changelog)
        self.assertIn("Pfad A", changelog)
        self.assertIn("2026-09-21", changelog)


if __name__ == "__main__":
    unittest.main()
