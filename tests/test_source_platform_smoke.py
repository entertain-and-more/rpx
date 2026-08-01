import importlib.util
import inspect
import py_compile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def _load_constants_for_platform(platform_name: str):
    module_name = f"_rpx_constants_smoke_{platform_name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(
        module_name,
        ROOT / "rpx_pro" / "constants.py",
    )
    module = importlib.util.module_from_spec(spec)
    with patch.object(sys, "platform", platform_name):
        assert spec.loader is not None
        spec.loader.exec_module(module)
    return module


class SourcePlatformSmokeDefinitionTests(unittest.TestCase):
    def test_application_entry_points_import_without_starting_qt_loop(self):
        import rpx_pro.app as app_module
        import RPX_Pro_1 as script_entry

        self.assertTrue(callable(app_module.main))
        self.assertIs(script_entry.main, app_module.main)

    def test_non_windows_constants_never_expose_winsound_backend(self):
        for platform_name in ("linux", "darwin"):
            constants = _load_constants_for_platform(platform_name)
            self.assertFalse(constants._HAS_WINSOUND, platform_name)

    def test_player_screen_source_keeps_monitor_and_fullscreen_routing(self):
        from rpx_pro import main_window
        from rpx_pro.tabs.views_tab import ViewsTab

        main_source = inspect.getsource(main_window.RPXProMainWindow._toggle_player_screen)
        views_source = inspect.getsource(ViewsTab._create_player_screen_view)

        self.assertIn("QApplication.screens()", main_source)
        self.assertIn("setGeometry(screen.geometry())", main_source)
        self.assertIn("showFullScreen()", main_source)
        self.assertIn("player_screen_monitor_changed", views_source)
        self.assertIn("fullscreen_check", views_source)

    def test_image_selection_uses_native_qt_file_dialogs(self):
        from rpx_pro import main_window
        from rpx_pro.tabs.views_tab import ViewsTab

        self.assertIn("QFileDialog.getOpenFileName", inspect.getsource(ViewsTab._load_image_for_ps))
        self.assertIn("QFileDialog.getOpenFileName", inspect.getsource(main_window.RPXProMainWindow._ps_load_image))

    def test_core_source_files_compile_for_source_distribution(self):
        for relative_path in (
            "RPX_Pro_1.py",
            "rpx_pro/app.py",
            "rpx_pro/constants.py",
            "rpx_pro/managers/audio_manager.py",
            "rpx_pro/tabs/views_tab.py",
            "rpx_pro/widgets/player_screen.py",
        ):
            py_compile.compile(str(ROOT / relative_path), doraise=True)


if __name__ == "__main__":
    unittest.main()
