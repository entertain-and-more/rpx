"""Contract tests for repository hygiene, CI/CD guardrails, PEP 621 metadata, and gitignore defense."""

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

    def test_gitignore_cloud_sync_and_lock_defense(self):
        gitignore_path = ROOT / ".gitignore"
        self.assertTrue(gitignore_path.exists(), ".gitignore must exist")
        content = gitignore_path.read_text(encoding="utf-8")

        expected_patterns = [
            "* (kopie)*",
            "* (Kopie)*",
            "*conflicted copy*",
            "*-WORKSTATION*",
            "*-ASUS*",
            "LOCK",
            "LOCK.*",
            "uv.lock",
            "!package-lock.json",
            ".automation-lock",
        ]
        for pattern in expected_patterns:
            self.assertIn(pattern, content, f".gitignore missing pattern: {pattern}")


if __name__ == "__main__":
    unittest.main()
