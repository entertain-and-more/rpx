"""CharacterInventoryDialog: Inventar-Dialog fuer einzelne Charaktere."""

from functools import partial
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QComboBox, QSpinBox, QGroupBox, QDialogButtonBox,
    QMessageBox,
)
from PySide6.QtCore import Qt


class CharacterInventoryDialog(QDialog):
    """Zeigt und verwaltet das Inventar eines Charakters."""

    def __init__(self, character, world, data_manager, parent=None):
        super().__init__(parent)
        self.character = character
        self.world = world
        self.data_manager = data_manager
        self.setWindowTitle(f"Inventar: {character.name}")
        self.setMinimumSize(600, 500)
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Charakter-Info
        info = QLabel(f"<h3>{self.character.name}</h3> "
                      f"<span style='color:#f1c40f;'>Gold: {self.character.gold}</span>")
        info.setStyleSheet("padding: 5px;")
        layout.addWidget(info)
        self.info_label = info

        # Gold bearbeiten
        gold_layout = QHBoxLayout()
        gold_layout.addWidget(QLabel("Gold:"))
        self.gold_spin = QSpinBox()
        self.gold_spin.setRange(0, 999999)
        self.gold_spin.setValue(self.character.gold)
        self.gold_spin.valueChanged.connect(self._on_gold_changed)
        gold_layout.addWidget(self.gold_spin)
        gold_layout.addStretch()
        layout.addLayout(gold_layout)

        # Inventar-Tabelle
        self.inv_table = QTableWidget()
        self.inv_table.setColumnCount(5)
        self.inv_table.setHorizontalHeaderLabels(["Gegenstand", "Anzahl", "Gewicht", "Wert", ""])
        self.inv_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.inv_table)

        # Gesamtgewicht
        self.weight_label = QLabel("Gesamtgewicht: 0.0")
        self.weight_label.setStyleSheet("font-weight: bold; color: #3498db; padding: 5px;")
        layout.addWidget(self.weight_label)

        # Item hinzufuegen
        add_group = QGroupBox("Item hinzufuegen")
        add_layout = QHBoxLayout(add_group)
        self.item_combo = QComboBox()
        self.item_combo.setMinimumWidth(200)
        # Befuelle mit Items aus der Welt-Bibliothek
        if self.world:
            for item_id, item in self.world.typical_items.items():
                self.item_combo.addItem(f"{item.name} (Wert: {item.value})", item_id)
        add_layout.addWidget(self.item_combo)

        self.add_count_spin = QSpinBox()
        self.add_count_spin.setRange(1, 99)
        self.add_count_spin.setValue(1)
        add_layout.addWidget(QLabel("Anzahl:"))
        add_layout.addWidget(self.add_count_spin)

        add_btn = QPushButton("Hinzufuegen")
        add_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        add_btn.clicked.connect(self._add_item)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _refresh(self):
        """Aktualisiert die Inventar-Tabelle."""
        inv = self.character.inventory
        self.inv_table.setRowCount(len(inv))
        total_weight = 0.0
        total_value = 0

        for row, (item_id, count) in enumerate(inv.items()):
            # Item-Name aufloesen
            name = item_id
            weight = 0.0
            value = 0
            if self.world and item_id in self.world.typical_items:
                item = self.world.typical_items[item_id]
                name = item.name
                weight = item.weight
                value = item.value

            self.inv_table.setItem(row, 0, QTableWidgetItem(name))
            self.inv_table.setItem(row, 1, QTableWidgetItem(str(count)))

            row_weight = weight * count
            total_weight += row_weight
            self.inv_table.setItem(row, 2, QTableWidgetItem(f"{row_weight:.1f}"))

            row_value = value * count
            total_value += row_value
            self.inv_table.setItem(row, 3, QTableWidgetItem(str(row_value)))

            # Entfernen-Button
            remove_btn = QPushButton("Entfernen")
            remove_btn.setStyleSheet("background-color: #c0392b; color: white;")
            remove_btn.clicked.connect(partial(self._remove_item, item_id))
            self.inv_table.setCellWidget(row, 4, remove_btn)

        self.weight_label.setText(f"Gesamtgewicht: {total_weight:.1f} | Gesamtwert: {total_value} Gold")
        self.info_label.setText(f"<h3>{self.character.name}</h3> "
                                f"<span style='color:#f1c40f;'>Gold: {self.character.gold}</span>")

    def _add_item(self):
        if self.item_combo.count() == 0:
            QMessageBox.information(self, "Info", "Keine Items in der Welt-Bibliothek vorhanden.")
            return
        item_id = self.item_combo.currentData()
        count = self.add_count_spin.value()
        self.character.inventory[item_id] = self.character.inventory.get(item_id, 0) + count
        self._save_and_refresh()

    def _remove_item(self, item_id: str):
        if item_id in self.character.inventory:
            current = self.character.inventory[item_id]
            if current <= 1:
                del self.character.inventory[item_id]
            else:
                self.character.inventory[item_id] -= 1
            self._save_and_refresh()

    def _on_gold_changed(self, value):
        self.character.gold = value
        self._save_and_refresh()

    def _save_and_refresh(self):
        session = self.data_manager.current_session
        if session:
            self.data_manager.save_session(session)
        self._refresh()
