import sys
import unittest
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from rpx_pro.tabs.settings_tab import SettingsTab
from translator import get_translator


class TestI18nUiIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.mock_data_manager = MagicMock()
        self.mock_data_manager.current_session = None
        self.mock_data_manager.current_world = None
        self.translator = get_translator()
        self.original_lang = self.translator.get_language()

    def tearDown(self):
        self.translator.set_language(self.original_lang)

    def test_settings_tab_language_combo_contains_all_six_languages(self):
        tab = SettingsTab(self.mock_data_manager)
        items = [tab.language_combo.itemData(i) for i in range(tab.language_combo.count())]
        self.assertEqual(items, ["de", "en", "es", "zh-Hans", "ja", "ru"])

    def test_settings_tab_language_combo_emits_signal(self):
        for target_lang in ["es", "zh-Hans", "ja", "ru"]:
            tab = SettingsTab(self.mock_data_manager)
            received_signals = []
            tab.language_changed.connect(lambda lang, sigs=received_signals: sigs.append(lang))

            idx_found = -1
            for idx in range(tab.language_combo.count()):
                if tab.language_combo.itemData(idx) == target_lang:
                    idx_found = idx
                    break

            self.assertNotEqual(idx_found, -1)
            tab.language_combo.setCurrentIndex(idx_found)

            self.assertEqual(received_signals, [target_lang])
            self.assertEqual(self.translator.get_language(), target_lang)

    def test_settings_tab_set_language_selection_does_not_loop(self):
        tab = SettingsTab(self.mock_data_manager)

        received_signals = []
        tab.language_changed.connect(lambda lang: received_signals.append(lang))

        tab.set_language_selection("en")
        self.assertEqual(received_signals, [])  # BlockSignals prevented signal loop
        self.assertEqual(tab.language_combo.currentData(), "en")

        tab.set_language_selection("zh-Hans")
        self.assertEqual(received_signals, [])
        self.assertEqual(tab.language_combo.currentData(), "zh-Hans")

if __name__ == "__main__":
    unittest.main()
