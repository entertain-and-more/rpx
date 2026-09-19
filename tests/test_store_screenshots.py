import json
import os
import tempfile
import unittest
from pathlib import Path

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from generate_store_screenshots import (
    SCREENSHOT_FILES,
    SUMMARY_FILE,
    _assert_store_font_rendering,
    generate_store_screenshots,
)


class StoreScreenshotGenerationTests(unittest.TestCase):
    def test_generator_uses_native_text_rendering_for_store_captures(self):
        source = Path(__file__).resolve().parents[1] / "generate_store_screenshots.py"
        content = source.read_text(encoding="utf-8")

        self.assertIn('os.environ.pop("QT_QPA_PLATFORM", None)', content)
        self.assertIn("WA_DontShowOnScreen", content)
        self.assertNotIn('setdefault("QT_QPA_PLATFORM", "offscreen")', content)

        player_screen = Path(__file__).resolve().parents[1] / "rpx_pro" / "widgets" / "player_screen.py"
        player_content = player_screen.read_text(encoding="utf-8")
        self.assertNotIn("QFrame {{", player_content)
        self.assertIn("QScrollArea::viewport", player_content)
        self.assertIn('tile_chars_container.setStyleSheet("background-color: #111;")', player_content)
        self.assertIn('tile_miss_container.setStyleSheet("background-color: #111;")', player_content)
        self.assertIn("background-color: transparent", player_content)

    def test_offscreen_qt_is_rejected_before_screenshots_are_written(self):
        app = QApplication.instance()
        if app is None or app.platformName() != "offscreen":
            self.skipTest("kein offscreen-Qt-Kontext")
        with self.assertRaises(RuntimeError):
            _assert_store_font_rendering(app)

    def test_generator_writes_all_expected_pngs_and_summary(self):
        if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
            self.skipTest("native Font-Renderings sind unter offscreen nicht prüfbar")
        with tempfile.TemporaryDirectory(prefix="rpx-store-test-") as tmpdir:
            output_dir = Path(tmpdir)

            summary = generate_store_screenshots(output_dir)

            expected_names = list(SCREENSHOT_FILES.values())
            self.assertEqual(
                sorted(entry["name"] for entry in summary["files"]),
                sorted(expected_names),
            )

            summary_path = output_dir / SUMMARY_FILE
            self.assertTrue(summary_path.exists())
            summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(
                sorted(entry["name"] for entry in summary_data["files"]),
                sorted(expected_names),
            )

            for filename in expected_names:
                path = output_dir / filename
                self.assertTrue(path.exists(), filename)
                image = QImage(str(path))
                self.assertFalse(image.isNull(), filename)
                self.assertGreaterEqual(image.width(), 1400, filename)
                self.assertGreaterEqual(image.height(), 900, filename)


if __name__ == "__main__":
    unittest.main()
