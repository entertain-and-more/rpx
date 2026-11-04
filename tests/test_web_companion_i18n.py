"""Tests for RPX Pro Web Companion Tier-2 i18n & PWA Architecture."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = PROJECT_ROOT / "web_companion"


def test_web_companion_core_files_exist():
    required_files = [
        WEB_DIR / "index.html",
        WEB_DIR / "styles.css",
        WEB_DIR / "app.js",
        WEB_DIR / "library.js",
        WEB_DIR / "i18n.js",
        WEB_DIR / "sw.js",
        WEB_DIR / "manifest.webmanifest",
        WEB_DIR / "README.md",
        WEB_DIR / "tests" / "i18n.test.mjs",
    ]
    for fp in required_files:
        assert fp.exists(), f"Missing required file: {fp.name}"
        assert fp.stat().st_size > 0, f"File is empty: {fp.name}"


def test_zero_egress_and_local_first_in_html():
    html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    # No external scripts, stylesheets or CDNs
    external_urls = re.findall(r'src=["\'](https?://[^"\']+)["\']', html)
    external_styles = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
    assert not external_urls, f"External scripts found: {external_urls}"
    assert not external_styles, f"External stylesheets found: {external_styles}"


def test_language_buttons_in_index_html():
    html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    for lang in ["de", "en", "es", "zh", "ja", "ru"]:
        assert f'data-lang="{lang}"' in html, f"Missing data-lang='{lang}' in index.html"


def test_i18n_module_contract_and_parity():
    code = (WEB_DIR / "i18n.js").read_text(encoding="utf-8")
    assert 'SUPPORTED_LOCALES = ["de", "en", "es", "zh", "ja", "ru"]' in code
    assert 'DEFAULT_LOCALE = "de"' in code
    assert 'STORAGE_KEY = "rpx-companion:language"' in code

    for lang in ["de:", "en:", "es:", "zh:", "ja:", "ru:"]:
        assert lang in code, f"Missing dictionary section for {lang}"


def test_service_worker_caches_i18n():
    sw = (WEB_DIR / "sw.js").read_text(encoding="utf-8")
    assert "./i18n.js" in sw, "sw.js must cache ./i18n.js"
    assert "./app.js" in sw
    assert "./library.js" in sw


def test_web_companion_node_test_suite_passes():
    res = subprocess.run(
        ["node", "--test", "tests/i18n.test.mjs"],
        cwd=WEB_DIR,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Node tests failed:\n{res.stdout}\n{res.stderr}"
    assert "fail 0" in res.stdout
