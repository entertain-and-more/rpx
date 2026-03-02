"""PromptGeneratorWidget: Widget fuer KI-Prompt-Generierung."""

from typing import Dict

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QGroupBox, QMessageBox, QApplication,
)

from rpx_pro.models.entities import Character
from rpx_pro.managers.data_manager import DataManager
from rpx_pro.managers.prompt_generator import PromptGenerator


class PromptGeneratorWidget(QWidget):
    """Widget fuer KI-Prompt-Generierung"""

    prompt_generated = Signal(str)

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("KI-Promptgenerator")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #9b59b6;")
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.character_combo = QComboBox()
        form_layout.addRow("Charakter:", self.character_combo)

        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "Freie Aktion", "Ort betreten", "Ort verlassen", "Kampf",
            "Dialog", "Suchen", "Handwerk", "Magie"
        ])
        form_layout.addRow("Aktion:", self.action_combo)

        layout.addLayout(form_layout)

        ki_group = QGroupBox("KI-Auftraege")
        ki_layout = QGridLayout(ki_group)

        ki_buttons = [
            ("Storyteller", "storyteller"),
            ("Plottwist", "plottwist"),
            ("Spielleiter", "gamemaster"),
            ("Gegner", "enemy"),
            ("NPCs", "npc"),
            ("Landschaft", "landscape"),
            ("Fauna/Flora", "fauna_flora"),
        ]

        for i, (text, role) in enumerate(ki_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, r=role: self.generate_role_prompt(r))
            ki_layout.addWidget(btn, i // 4, i % 4)

        layout.addWidget(ki_group)

        layout.addWidget(QLabel("Generierter Prompt:"))
        self.prompt_preview = QTextEdit()
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setMinimumHeight(150)
        layout.addWidget(self.prompt_preview)

        btn_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Generieren")
        self.generate_btn.clicked.connect(self.generate_prompt)
        btn_layout.addWidget(self.generate_btn)

        self.copy_btn = QPushButton("In Zwischenablage")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.copy_btn)

        self.start_btn = QPushButton("Spielstart-Prompt")
        self.start_btn.clicked.connect(self.generate_start_prompt)
        btn_layout.addWidget(self.start_btn)

        self.update_btn = QPushButton("Update-Prompt")
        self.update_btn.clicked.connect(self.generate_update_prompt)
        btn_layout.addWidget(self.update_btn)

        layout.addLayout(btn_layout)

    def update_characters(self, characters: Dict[str, Character]):
        """Aktualisiert Charakter-Auswahl"""
        self.character_combo.clear()
        for char in characters.values():
            self.character_combo.addItem(f"{char.name} ({char.race})", char.id)

    def generate_prompt(self):
        """Generiert einen Aktions-Prompt"""
        session = self.data_manager.current_session
        world = self.data_manager.current_world

        if not session or not world:
            QMessageBox.warning(self, "Fehler", "Keine aktive Session!")
            return

        char_id = self.character_combo.currentData()
        if char_id and char_id in session.characters:
            char = session.characters[char_id]
            action = self.action_combo.currentText()

            location = None
            if session.current_location_id and session.current_location_id in world.locations:
                location = world.locations[session.current_location_id]

            prompt = PromptGenerator.generate_action_prompt(char, action, location)
            self.prompt_preview.setPlainText(prompt)
            self.prompt_generated.emit(prompt)

    def generate_role_prompt(self, role: str):
        """Generiert einen Rollen-Prompt"""
        session = self.data_manager.current_session
        world = self.data_manager.current_world

        if not session or not world:
            QMessageBox.warning(self, "Fehler", "Keine aktive Session!")
            return

        prompt = PromptGenerator.generate_role_prompt(role, session, world)
        self.prompt_preview.setPlainText(prompt)
        self.prompt_generated.emit(prompt)

    def generate_start_prompt(self):
        """Generiert Spielstart-Prompt"""
        session = self.data_manager.current_session
        world = self.data_manager.current_world

        if not session or not world:
            QMessageBox.warning(self, "Fehler", "Keine aktive Session!")
            return

        prompt = PromptGenerator.generate_game_start_prompt(session, world)
        self.prompt_preview.setPlainText(prompt)
        self.prompt_generated.emit(prompt)

    def generate_update_prompt(self):
        """Generiert Update-Prompt"""
        session = self.data_manager.current_session

        if not session:
            QMessageBox.warning(self, "Fehler", "Keine aktive Session!")
            return

        prompt = PromptGenerator.generate_context_update_prompt(session)
        self.prompt_preview.setPlainText(prompt)

        session.last_clipboard_index = len(session.chat_history)
        self.data_manager.save_session(session)

        self.prompt_generated.emit(prompt)

    def copy_to_clipboard(self):
        """Kopiert Prompt in Zwischenablage"""
        text = self.prompt_preview.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Kopiert", "Prompt wurde in die Zwischenablage kopiert!")
