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

    def test_settings_tab_language_combo_emits_signal(self):
        tab = SettingsTab(self.mock_data_manager)

        received_signals = []
        tab.language_changed.connect(lambda lang: received_signals.append(lang))

        # Select Spanish (index 2: es)
        es_index = -1
        for idx in range(tab.language_combo.count()):
            if tab.language_combo.itemData(idx) == "es":
                es_index = idx
                break

        self.assertNotEqual(es_index, -1)
        tab.language_combo.setCurrentIndex(es_index)

        self.assertEqual(received_signals, ["es"])
        self.assertEqual(self.translator.get_language(), "es")

    def test_settings_tab_set_language_selection_does_not_loop(self):
        tab = SettingsTab(self.mock_data_manager)

        received_signals = []
        tab.language_changed.connect(lambda lang: received_signals.append(lang))

        tab.set_language_selection("en")
        self.assertEqual(received_signals, [])  # BlockSignals prevented signal loop
        self.assertEqual(tab.language_combo.currentData(), "en")


if __name__ == "__main__":
    unittest.main()
