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

        self.assertRegex(content, r"actions/checkout@v[0-9]+")
        self.assertRegex(content, r"actions/setup-python@v[0-9]+")
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

    def test_ci_lifecycle_and_dependabot_workflows(self):
        dependabot = ROOT / ".github" / "dependabot.yml"
        self.assertTrue(dependabot.exists(), ".github/dependabot.yml must exist")
        dep_content = dependabot.read_text(encoding="utf-8")
        self.assertIn("package-ecosystem: \"github-actions\"", dep_content)
        self.assertIn("interval: \"weekly\"", dep_content)
        self.assertIn("timezone: \"Europe/Berlin\"", dep_content)
        self.assertIn("open-pull-requests-limit: 3", dep_content)

        auto_assign = ROOT / ".github" / "workflows" / "auto-assign.yml"
        self.assertTrue(auto_assign.exists(), "auto-assign.yml must exist")
        aa_content = auto_assign.read_text(encoding="utf-8")
        self.assertRegex(aa_content, r"actions/github-script@v[0-9]+")
        self.assertIn("timeout-minutes: 5", aa_content)
        self.assertIn("cancel-in-progress: true", aa_content)

        label_sync = ROOT / ".github" / "workflows" / "label-sync.yml"
        self.assertTrue(label_sync.exists(), "label-sync.yml must exist")
        ls_content = label_sync.read_text(encoding="utf-8")
        self.assertIn("EndBug/label-sync@v2", ls_content)
        self.assertIn("config-file: .github/labels.yml", ls_content)
        self.assertIn("timeout-minutes: 5", ls_content)

        labels_yml = ROOT / ".github" / "labels.yml"
        self.assertTrue(labels_yml.exists(), ".github/labels.yml must exist")
        labels_content = labels_yml.read_text(encoding="utf-8")
        self.assertIn("name: bug", labels_content)
        self.assertIn("name: enhancement", labels_content)
        self.assertIn("name: documentation", labels_content)

    def test_pyproject_pep621_compliance(self):
        pyproject_path = ROOT / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml must exist")

        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        self.assertEqual(project.get("name"), "rpx-pro")
        self.assertEqual(project.get("version"), "1.0.0")
        self.assertIn("license-files", project)
        self.assertEqual(
            project["license-files"],
            ["CONTRIBUTING.md", "LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"],
        )
        self.assertEqual(len(project.get("keywords", [])), 20)

        classifiers = project.get("classifiers", [])
        self.assertIn("Programming Language :: Python :: 3.13", classifiers)

        urls = project.get("urls", {})
        expected_urls = [
            "Homepage",
            "Documentation",
            "Repository",
            "Contributing",
            "Issues",
            "Changelog",
            "Security",
            "Notice",
            "LLM Ready",
            "Marketing Log",
            "Third-Party Licenses",
            "Level 1 SBOM",
            "Plain-Text License",
            "Third-Party Licenses (Text)",
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
        self.assertIn(".nyc_output", pytest_config.get("norecursedirs", []))
        self.assertIn(".tox", pytest_config.get("norecursedirs", []))
        self.assertIn(".turbo", pytest_config.get("norecursedirs", []))
        self.assertIn("--basetemp=.pytest_temp", pytest_config.get("addopts", ""))

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
            "*-IDEAPAD*",
            "*-IDEAPAD-GEI*",
            "*-IDEAPAD-GEI.*",
            "*-Mac Studio*",
            "*-MacBook*",
            "LOCK",
            "LOCK.*",
            "LOCK.user.*",
            "LOCK.until.*",
            "LOCK.condition.*",
            "LOCK.dev.*",
            "LOCK.antigravity.*",
            "LOCK.bugsearch.*",
            "LOCK.permissions.json",
            "uv.lock",
            "!package-lock.json",
            ".automation-lock",
            "TASKPLAN_*.md",
            "*-TASKPLAN*",
            "ehthumbs.db",
            "desktop.ini",
            "thumbs.db",
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

            sec_id = f"sec-{i:02d}"
            self.assertIn(f'id="{sec_id}"', readme_en, f"README.md missing anchor {sec_id}")
            self.assertIn(f'id="{sec_id}"', readme_de, f"README_de.md missing anchor {sec_id}")
            self.assertIn(f"(#{sec_id})", readme_en, f"README.md quick navigation missing target #{sec_id}")
            self.assertIn(f"(#{sec_id})", readme_de, f"README_de.md quick navigation missing target #{sec_id}")

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

    def test_contributing_bilingual_parity_and_invariants(self):
        contrib_path = ROOT / "CONTRIBUTING.md"
        self.assertTrue(contrib_path.exists(), "CONTRIBUTING.md must exist")
        content = contrib_path.read_text(encoding="utf-8")

        self.assertIn("# Contributing to RPX Pro", content)
        self.assertIn("[English](#english)", content)
        self.assertIn("[Deutsch](#deutsch)", content)

        invariants = [
            "INV-LOCAL-01",
            "INV-USER-02",
            "INV-DUAL-03",
            "INV-RPC-04",
            "INV-BUNDLE-05",
            "INV-PWA-06",
            "INV-COPYLEFT-07",
            "INV-LLM-08",
            "INV-ECO-09",
            "INV-SLA-10",
        ]
        for inv in invariants:
            self.assertIn(inv, content, f"CONTRIBUTING.md missing invariant {inv}")

        self.assertIn("RunAsInvoker", content)
        self.assertIn("Plan D", content)
        self.assertIn("521", content)
        self.assertIn("48h", content)
        self.assertIn("T-20260920-167562623", content)
        self.assertIn("1.0.0", content)

    def test_llms_txt_structure_and_parity(self):
        llms_path = ROOT / "llms.txt"
        self.assertTrue(llms_path.exists(), "llms.txt must exist")
        content = llms_path.read_text(encoding="utf-8")

        self.assertTrue(content.startswith("## Last-checked: 2026-10-04"), "llms.txt must have current date")
        self.assertIn("[PERSONA-01]", content)
        self.assertIn("INV-LOCAL-01", content)
        self.assertIn("CONTRIBUTING.md", content)
        self.assertIn("THIRD_PARTY_LICENSES.md", content)
        self.assertIn("THIRD_PARTY_LICENSES.txt", content)
        self.assertIn("NOTICE", content)

    def test_changelog_recent_pfad_a_and_b_entries(self):
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## [Unreleased]", changelog)
        self.assertIn("Pfad A", changelog)
        self.assertIn("2026-10-04", changelog)
        self.assertIn("Pfad B", changelog)
        self.assertIn("2026-09-30", changelog)

    def test_canonical_root_notice(self):
        notice_path = ROOT / "NOTICE"
        self.assertTrue(notice_path.exists(), "Root NOTICE file must exist")
        content = notice_path.read_text(encoding="utf-8")
        self.assertIn("RPX Pro", content)
        self.assertIn("Lukas Geiger", content)
        self.assertIn("entertain-and-more", content)
        self.assertIn("open-bricks", content)
        self.assertIn("MIT License", content)
        self.assertIn("THIRD_PARTY_LICENSES.txt", content)

    def test_level_1_sbom_matrix_and_compliance(self):
        licenses_md = ROOT / "THIRD_PARTY_LICENSES.md"
        content_md = licenses_md.read_text(encoding="utf-8")
        self.assertIn("Audited", content_md)
        self.assertIn("2026-10-04", content_md)
        self.assertIn("CONTRIBUTING.md", content_md)
        self.assertIn("Canonical Notice", content_md)
        self.assertIn("[NOTICE](NOTICE)", content_md)
        self.assertIn("THIRD_PARTY_LICENSES.txt", content_md)
        self.assertIn("Level 1 SBOM Invariant Cross-Reference Matrix", content_md)
        invariants = [
            "INV-LOCAL-01",
            "INV-USER-02",
            "INV-DUAL-03",
            "INV-RPC-04",
            "INV-BUNDLE-05",
            "INV-PWA-06",
            "INV-COPYLEFT-07",
            "INV-LLM-08",
            "INV-ECO-09",
            "INV-SLA-10",
        ]
        for inv in invariants:
            self.assertIn(inv, content_md)

    def test_ascii_four_view_architectural_topology_projection(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

        en_views = [
            "VIEW 1: CLIENT RUNTIMES, USER INTERFACES & AUTOMATION ENTRY POINTS",
            "VIEW 2: RPX PRO SOVEREIGN CORE ENGINE & ORCHESTRATION PIPELINE",
            "VIEW 3: RUNTIME PERSISTENCE, CAMPAIGN BUNDLES & LOCAL VAULT",
            "VIEW 4: AIR-GAP DEFENSE PERIMETER, RUNASINVOKER & GOVERNANCE",
        ]
        for view in en_views:
            self.assertIn(view, readme_en, f"README.md missing ASCII topology view: {view}")

        de_views = [
            "SICHT 1: CLIENT-LAUFZEITEN, BEDIENOBERFLÄCHEN & AUTOMATIONSSCHNITTSTELLEN",
            "SICHT 2: RPX PRO KERN-ENGINE & ORCHESTRIERUNGS-PIPELINE",
            "SICHT 3: RUNTIME-PERSISTENZ, KAMPAGNEN-BUNDLES & LOKALER SPEICHER",
            "SICHT 4: AIR-GAP SCHUTZPERIMETER, RUNASINVOKER & GOVERNANCE",
        ]
        for view in de_views:
            self.assertIn(view, readme_de, f"README_de.md missing ASCII topology view: {view}")

    def test_level_1_sbom_plain_text_companion_invariants(self):
        licenses_txt = ROOT / "THIRD_PARTY_LICENSES.txt"
        self.assertTrue(licenses_txt.exists(), "THIRD_PARTY_LICENSES.txt must exist")
        content = licenses_txt.read_text(encoding="utf-8")

        invariants = [
            "INV-LOCAL-01",
            "INV-USER-02",
            "INV-DUAL-03",
            "INV-RPC-04",
            "INV-BUNDLE-05",
            "INV-PWA-06",
            "INV-COPYLEFT-07",
            "INV-LLM-08",
            "INV-ECO-09",
            "INV-SLA-10",
        ]
        for inv in invariants:
            self.assertIn(inv, content, f"THIRD_PARTY_LICENSES.txt missing {inv}")

        self.assertIn("2026-10-04", content)
        self.assertIn("CONTRIBUTING.md", content)
        self.assertIn("RunAsInvoker", content)
        self.assertIn("Zero-Copyleft", content)
        self.assertIn("521", content)
        self.assertIn("48", content)
        self.assertIn("MIT License", content)
        self.assertIn("Python Software Foundation License", content)
        self.assertIn("LGPL-3.0", content)
        self.assertIn("LGPL-2.1", content)

    def test_marketing_log_recency_and_pfad_a(self):
        marketing_log = (ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
        self.assertIn("2026-10-04", marketing_log)
        self.assertIn("Pfad A", marketing_log)
        self.assertIn("2026-09-30", marketing_log)
        self.assertIn("Pfad B", marketing_log)
        self.assertIn("ASCII Four-View Architectural Topology Projection", marketing_log)
        self.assertIn("Plain-Text Level 1 SBOM Companion", marketing_log)

    def test_statutory_disclaimer_and_security_sla(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
        security_md = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        marketing_log = (ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

        for doc, name in [
            (readme_en, "README.md"),
            (readme_de, "README_de.md"),
            (security_md, "SECURITY.md"),
            (marketing_log, "MARKETING-LOG.txt"),
        ]:
            self.assertIn("521", doc, f"{name} missing § 521 BGB disclaimer")
            self.assertIn("48", doc, f"{name} missing 48-hour SLA")
            self.assertIn("open-bricks.org", doc, f"{name} missing security reporting channel")

    def test_gitignore_internal_file_hygiene(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        patterns = [
            "BEFUNDE.md",
            "DECISIONS.md",
            "PORTIERUNGSPLAN.md",
            "TODO.md",
            "DONE.md",
            "TASKPLAN_STATUS_*.md",
            "_after-care/",
        ]
        for pattern in patterns:
            self.assertIn(pattern, gitignore, f".gitignore must contain {pattern}")


if __name__ == "__main__":
    unittest.main()
