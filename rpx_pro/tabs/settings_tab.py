"""SettingsTab: Session- und Welt-Einstellungen."""

import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QGroupBox, QCheckBox, QSpinBox, QDoubleSpinBox,
)
from PySide6.QtCore import Signal

logger = logging.getLogger("RPX")


class SettingsTab(QWidget):
    """Einstellungen: Session- und Welt-Einstellungen."""

    round_mode_changed = Signal(bool)
    status_message = Signal(str)

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Session-Einstellungen
        session_group = QGroupBox("Session-Einstellungen")
        session_layout = QFormLayout(session_group)

        self.round_based_check = QCheckBox("Rundenbasiert")
        self.round_based_check.stateChanged.connect(self._on_round_mode_changed)
        session_layout.addRow("Spielmodus:", self.round_based_check)

        self.actions_spin = QSpinBox()
        self.actions_spin.setRange(0, 10)
        self.actions_spin.setSpecialValueText("Unbegrenzt")
        session_layout.addRow("Aktionen pro Runde:", self.actions_spin)

        self.gm_human_check = QCheckBox("Spielleiter ist Mensch")
        self.gm_human_check.setChecked(True)
        session_layout.addRow("", self.gm_human_check)

        self.gm_name_edit = QLineEdit()
        session_layout.addRow("Spielleiter-Name:", self.gm_name_edit)

        layout.addWidget(session_group)

        # Welt-Einstellungen
        world_group = QGroupBox("Welt-Einstellungen")
        world_layout = QFormLayout(world_group)

        self.time_ratio_spin = QDoubleSpinBox()
        self.time_ratio_spin.setRange(0.1, 100)
        self.time_ratio_spin.setValue(1.0)
        world_layout.addRow("Zeitverhaeltnis (1h real = X Spielstunden):", self.time_ratio_spin)

        self.day_hours_spin = QSpinBox()
        self.day_hours_spin.setRange(1, 100)
        self.day_hours_spin.setValue(24)
        world_layout.addRow("Stunden pro Tag:", self.day_hours_spin)

        self.daylight_spin = QSpinBox()
        self.daylight_spin.setRange(1, 100)
        self.daylight_spin.setValue(12)
        world_layout.addRow("Davon hell:", self.daylight_spin)

        self.hunger_check = QCheckBox("Hunger/Durst simulieren")
        world_layout.addRow("", self.hunger_check)

        self.disasters_check = QCheckBox("Naturkatastrophen")
        world_layout.addRow("", self.disasters_check)

        layout.addWidget(world_group)

        layout.addStretch()

    # --- Public ---

    def load_from_session(self):
        """Laedt Session-/Welt-Einstellungen."""
        session = self.data_manager.current_session
        world = self.data_manager.current_world

        if session:
            self.round_based_check.setChecked(session.is_round_based)
            self.actions_spin.setValue(session.actions_per_turn)
            self.actions_spin.setEnabled(session.is_round_based)
            self.gm_human_check.setChecked(session.gm_is_human)
            self.gm_name_edit.setText(session.gm_player_name)

        if world:
            self.time_ratio_spin.setValue(world.settings.time_ratio)
            self.day_hours_spin.setValue(world.settings.day_hours)
            self.daylight_spin.setValue(world.settings.daylight_hours)
            self.hunger_check.setChecked(world.settings.simulate_hunger)
            self.disasters_check.setChecked(world.settings.simulate_disasters)

    def save_to_world(self, world):
        """Speichert Welt-Einstellungen zurueck."""
        world.settings.time_ratio = self.time_ratio_spin.value()
        world.settings.day_hours = self.day_hours_spin.value()
        world.settings.daylight_hours = self.daylight_spin.value()
        world.settings.simulate_hunger = self.hunger_check.isChecked()
        world.settings.simulate_disasters = self.disasters_check.isChecked()

    # --- Private ---

    def _on_round_mode_changed(self, state):
        is_round_based = self.round_based_check.isChecked()
        self.actions_spin.setEnabled(is_round_based)
        session = self.data_manager.current_session
        if session:
            session.is_round_based = is_round_based
            self.data_manager.save_session(session)
        self.round_mode_changed.emit(is_round_based)
