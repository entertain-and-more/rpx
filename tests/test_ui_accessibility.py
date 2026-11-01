"""Accessibility, Keyboard Navigation, and Dialog Contract Tests for RPX Pro (WCAG 2.1 AA / BITV 2.0).

Verifies keyboard accelerators, tab switching shortcuts, hierarchical shortcut guide,
metadata dialogs, search filtering, and escape-key handling.
"""

import sys
import unittest

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QDialog

from rpx_pro.constants import VERSION
from rpx_pro.widgets.dialogs import AboutDialog, ShortcutsDialog
from translator import get_translator


class TestUiAccessibilityAndDialogs(unittest.TestCase):
    """Test suite for keyboard navigation, accessibility features, and dialogs."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.translator = get_translator()
        self.original_lang = self.translator.get_language()
        self.translator.set_language("de")

    def tearDown(self):
        self.translator.set_language(self.original_lang)

    def test_shortcuts_dialog_structure_and_accessibility(self):
        """ShortcutsDialog must define accessible roles, tree structure, and WCAG hints."""
        dialog = ShortcutsDialog()
        self.assertTrue(dialog.isModal())
        self.assertIn("Tastaturkürzel", dialog.windowTitle())
        self.assertEqual(dialog.accessibleName(), dialog.windowTitle())
        self.assertTrue(len(dialog.accessibleDescription()) > 0)

        # Check tree widget configuration
        tree = dialog.tree
        self.assertEqual(tree.columnCount(), 3)
        self.assertGreaterEqual(tree.topLevelItemCount(), 4)

        categories = [
            tree.topLevelItem(i).text(0) for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("Navigation & Registerkarten", categories)
        self.assertIn("Menü & Session", categories)
        self.assertIn("Spieler-Bildschirm", categories)
        self.assertIn("Kampf & Rundensteuerung", categories)

        # Verify child items exist in categories
        for i in range(tree.topLevelItemCount()):
            top = tree.topLevelItem(i)
            self.assertGreater(top.childCount(), 0)

        # Test escape key closes dialog
        escape_event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier,
        )
        dialog.keyPressEvent(escape_event)
        self.assertEqual(dialog.result(), int(QDialog.DialogCode.Accepted))

    def test_about_dialog_structure_and_metadata(self):
        """AboutDialog must provide structured metadata, version parity, and local-first invariants."""
        dialog = AboutDialog()
        self.assertTrue(dialog.isModal())
        self.assertIn("Über RPX Pro", dialog.windowTitle())
        self.assertEqual(dialog.accessibleName(), dialog.windowTitle())

        # Content must contain version and local-first reassurance
        text_content = ""
        for child in dialog.findChildren(object):
            if hasattr(child, "text"):
                text_content += " " + child.text()

        self.assertIn(f"v{VERSION}", text_content)
        self.assertIn("Local-First", text_content)
        self.assertIn("Zero-Egress", text_content)
        self.assertIn("MIT-Lizenz", text_content)

        # Test escape key closes dialog
        escape_event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier,
        )
        dialog.keyPressEvent(escape_event)
        self.assertEqual(dialog.result(), int(QDialog.DialogCode.Accepted))

    def test_main_window_keyboard_navigation_and_shortcuts(self):
        """RPXProMainWindow must configure tab shortcuts and menu mnemonics correctly."""
        from rpx_pro.main_window import RPXProMainWindow

        window = RPXProMainWindow()

        # Check tab navigation shortcuts
        self.assertGreaterEqual(len(window._tab_shortcuts), 12)
        total_tabs = window.tabs.count()
        self.assertGreaterEqual(total_tabs, 8)

        # Test direct tab switching helper
        window._switch_tab(2)
        self.assertEqual(window.tabs.currentIndex(), 2)
        window._switch_tab(0)
        self.assertEqual(window.tabs.currentIndex(), 0)

        # Test cyclic next tab
        window.tabs.setCurrentIndex(total_tabs - 1)
        window._next_tab()
        self.assertEqual(window.tabs.currentIndex(), 0)

        # Test cyclic prev tab
        window.tabs.setCurrentIndex(0)
        window._prev_tab()
        self.assertEqual(window.tabs.currentIndex(), total_tabs - 1)

        # Test menu accelerators and mnemonics
        self.assertEqual(window.new_session_action.shortcut().toString(), "Ctrl+N")
        self.assertEqual(window.load_session_action.shortcut().toString(), "Ctrl+O")
        self.assertEqual(window.save_session_action.shortcut().toString(), "Ctrl+S")
        self.assertEqual(window.import_ruleset_action.shortcut().toString(), "Ctrl+I")
        self.assertEqual(window.exit_action.shortcut().toString(), "Ctrl+Q")

        self.assertEqual(window.ps_open_action.shortcut().toString(), "F11")
        self.assertEqual(window.ps_black_action.shortcut().toString(), "Ctrl+B")
        self.assertEqual(window.ps_map_action.shortcut().toString(), "Ctrl+M")
        self.assertEqual(window.ps_image_action.shortcut().toString(), "Ctrl+Shift+I")

        self.assertEqual(window.shortcuts_action.shortcut().toString(), "F1")
        self.assertEqual(window.about_action.shortcut().toString(), "Shift+F1")

        # Test dynamic retranslation without exception
        window.retranslate_ui()
        self.assertIn("&Datei", window.file_menu.title())
        self.assertIn("&Hilfe", window.help_menu.title())

        # Test language switch to English
        self.translator.set_language("en")
        window.retranslate_ui()
        self.assertIn("&File", window.file_menu.title())
        self.assertIn("&Help", window.help_menu.title())


if __name__ == "__main__":
    unittest.main()
