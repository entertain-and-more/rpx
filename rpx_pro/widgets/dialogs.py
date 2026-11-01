"""
rpx_pro/widgets/dialogs.py - Barrierefreie Hilfs- und Informationsdialoge
========================================================================
WCAG 2.1 AA / BITV 2.0 Tastatur-Ergonomie & Dialogstrukturen fuer RPX Pro.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from rpx_pro.constants import APP_TITLE, VERSION
from translator import get_translator


class ShortcutsDialog(QDialog):
    """Barrierefreier Referenzdialog fuer alle globalen Tastenkombinationen (WCAG 2.1 AA / BITV 2.0)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.tr = get_translator()
        title = self.tr.t("shortcuts_dialog_title") or "Tastaturkürzel & Barrierefreiheit"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        desc = (
            self.tr.t("shortcuts_dialog_desc")
            or "Übersicht aller verfügbaren Tastenkombinationen und Navigationshilfen."
        )
        self.setAccessibleDescription(desc)
        self.setMinimumSize(660, 520)
        self.resize(720, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header_label = QLabel(f"<h3>⌨️ {title}</h3>")
        layout.addWidget(header_label)

        sub_label = QLabel(desc)
        sub_label.setWordWrap(True)
        sub_label.setStyleSheet("color: #555555; margin-bottom: 6px;")
        layout.addWidget(sub_label)

        # Tree widget with grouped categories
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            "Bereich",
            "Tastenkürzel",
            "Aktion",
        ])
        self.tree.setColumnCount(3)
        self.tree.setAccessibleName(title)
        self.tree.setAccessibleDescription(desc)
        self.tree.setAlternatingRowColors(True)

        shortcuts_data = [
            (
                self.tr.t("cat_navigation") or "Navigation & Registerkarten",
                [
                    ("Ctrl+1", "Chatverlauf und Nachrichten"),
                    ("Ctrl+2", "Ansichten & Spieler-Bildschirm-Steuerung"),
                    ("Ctrl+3", "Welten, Orte und Karten verwalten"),
                    ("Ctrl+4", "Charaktere verwalten"),
                    ("Ctrl+5", "Kampf, Würfel und Rundensteuerung"),
                    ("Ctrl+6", "Missionen planen und verfolgen"),
                    ("Ctrl+7", "Inventar und Gegenstände"),
                    ("Ctrl+8", "Soundboard & Atmosphäre"),
                    ("Ctrl+9", "KI-Prompts generieren"),
                    ("Ctrl+0", "Einstellungen"),
                    ("Ctrl+Tab", "Zur nächsten Registerkarte wechseln"),
                    ("Ctrl+Shift+Tab", "Zur vorherigen Registerkarte wechseln"),
                ],
            ),
            (
                self.tr.t("cat_menu") or "Menü & Session",
                [
                    ("Ctrl+N", "Neue Spielsitzung anlegen"),
                    ("Ctrl+O", "Gespeicherte Session laden"),
                    ("Ctrl+S", "Aktuelle Session speichern"),
                    ("Ctrl+I", "Regelwerk importieren"),
                    ("Ctrl+Q", "Anwendung beenden"),
                ],
            ),
            (
                self.tr.t("cat_player_screen") or "Spieler-Bildschirm",
                [
                    ("F11", "Spieler-Bildschirm öffnen oder umschalten"),
                    ("Ctrl+B", "Schwarzbild ein-/ausschalten"),
                    ("Ctrl+M", "Aktive Karte auf Spieler-Bildschirm anzeigen"),
                    ("Ctrl+Shift+I", "Bild für Spieler-Bildschirm laden"),
                ],
            ),
            (
                self.tr.t("cat_combat") or "Kampf & Rundensteuerung",
                [
                    ("F1", "Tastaturkürzel & Barrierefreiheit (dieser Dialog)"),
                    ("Shift+F1", "Über RPX Pro (Version & Lizenz)"),
                    ("Esc", "Aktiven Dialog schließen"),
                ],
            ),
        ]

        for cat_name, items in shortcuts_data:
            cat_item = QTreeWidgetItem(self.tree)
            cat_item.setText(0, cat_name)
            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)

            for key, action in items:
                child = QTreeWidgetItem(cat_item)
                child.setText(1, key)
                child.setText(2, action)
                child_font = child.font(1)
                child_font.setBold(True)
                child.setFont(1, child_font)

            cat_item.setExpanded(True)

        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
        layout.addWidget(self.tree)

        # Bottom Button Box
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.close_btn = QPushButton(self.tr.t("btn_schliessen") or "Schließen")
        self.close_btn.setDefault(True)
        self.close_btn.setAutoDefault(True)
        self.close_btn.setAccessibleName(self.tr.t("btn_schliessen") or "Schließen")
        self.close_btn.clicked.connect(self.accept)
        btn_box.addWidget(self.close_btn)

        layout.addLayout(btn_box)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.accept()
            return
        super().keyPressEvent(event)


class AboutDialog(QDialog):
    """Barrierefreier Ueber-Dialog mit Version, Lizenz, Architektur und Barrierefreiheit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.tr = get_translator()
        title = self.tr.t("about_dialog_title") or f"Über {APP_TITLE}"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        desc = f"Informationen über {APP_TITLE} v{VERSION}, Lizenz und Local-First Architektur."
        self.setAccessibleDescription(desc)
        self.setMinimumSize(540, 390)
        self.resize(580, 430)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        header_layout = QHBoxLayout()
        icon_label = QLabel()
        icon = QApplication.windowIcon()
        if not icon.isNull():
            pixmap = icon.pixmap(48, 48)
            icon_label.setPixmap(pixmap)
        header_layout.addWidget(icon_label)

        title_vbox = QVBoxLayout()
        app_title = QLabel(f"<h2>{APP_TITLE} v{VERSION}</h2>")
        title_vbox.addWidget(app_title)
        subtitle = QLabel(self.tr.t("about_subtitle") or "Ein umfassendes Pen & Paper Spielleiter-Toolkit.")
        subtitle.setStyleSheet("color: #444444; font-weight: bold;")
        title_vbox.addWidget(subtitle)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        info_group = QGroupBox("System & Architektur")
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(8)

        lbl_license = QLabel(self.tr.t("about_license") or "Lizenz: MIT-Lizenz (Open Source)")
        lbl_arch = QLabel(
            self.tr.t("about_architecture")
            or "Architektur: 100% Local-First & Zero-Egress (keine Datensammlung, keine Telemetrie)"
        )
        lbl_arch.setWordWrap(True)
        lbl_a11y = QLabel(
            self.tr.t("about_a11y")
            or "Barrierefreiheit: WCAG 2.1 AA / BITV 2.0 Tastatur-Ergonomie"
        )
        lbl_platform = QLabel("Plattform: Python 3.10+ & PySide6 / Qt6 (Windows, Linux, macOS)")

        for lbl in (lbl_license, lbl_arch, lbl_a11y, lbl_platform):
            info_layout.addWidget(lbl)

        layout.addWidget(info_group)

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.close_btn = QPushButton(self.tr.t("btn_schliessen") or "Schließen")
        self.close_btn.setDefault(True)
        self.close_btn.setAutoDefault(True)
        self.close_btn.setAccessibleName(self.tr.t("btn_schliessen") or "Schließen")
        self.close_btn.clicked.connect(self.accept)
        btn_box.addWidget(self.close_btn)

        layout.addLayout(btn_box)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.accept()
            return
        super().keyPressEvent(event)
