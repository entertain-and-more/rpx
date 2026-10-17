"""CombatTab: Kampfsystem mit Wuerfeln, Angriffen, Waffen und Zaubern."""

import contextlib
import random
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox,
    QListWidget, QSpinBox, QMessageBox, QInputDialog,
)
from PySide6.QtCore import Qt, Signal

from rpx_pro.constants import generate_short_id
from rpx_pro.models.entities import Weapon, Spell
from rpx_pro.managers.dice_roller import DiceRoller

logger = logging.getLogger("RPX")

DEFAULT_UNARMED_CRIT_THRESHOLD = 20


class CombatTab(QWidget):
    """Kampfsystem: Wuerfel, Angriffe, Waffen, Zauber."""

    dice_rolled = Signal(str)  # result text
    attack_executed = Signal(dict)  # attack result data for PlayerScreen
    status_message = Signal(str)

    def __init__(self, data_manager, dice_roller: DiceRoller):
        super().__init__()
        self.data_manager = data_manager
        self.dice_roller = dice_roller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Würfelsystem
        dice_group = QGroupBox("Würfelsystem")
        dice_layout = QVBoxLayout(dice_group)

        dice_ctrl = QHBoxLayout()
        dice_ctrl.addWidget(QLabel("Anzahl:"))
        self.dice_count_spin = QSpinBox()
        self.dice_count_spin.setRange(1, 10)
        self.dice_count_spin.setValue(1)
        dice_ctrl.addWidget(self.dice_count_spin)

        dice_ctrl.addWidget(QLabel("Seiten:"))
        self.dice_sides_combo = QComboBox()
        self.dice_sides_combo.addItems(["W4", "W6", "W8", "W10", "W12", "W20", "W100"])
        self.dice_sides_combo.setCurrentText("W20")
        dice_ctrl.addWidget(self.dice_sides_combo)

        roll_btn = QPushButton("Würfeln!")
        roll_btn.setMinimumHeight(50)
        roll_btn.clicked.connect(self.roll_dice)
        dice_ctrl.addWidget(roll_btn)

        dice_layout.addLayout(dice_ctrl)

        self.dice_result_label = QLabel("Ergebnis: -")
        self.dice_result_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f1c40f;")
        self.dice_result_label.setAlignment(Qt.AlignCenter)
        dice_layout.addWidget(self.dice_result_label)

        layout.addWidget(dice_group)

        # Kampf-Angriff
        attack_group = QGroupBox("Angriff (mit Waffen-Interpretation)")
        attack_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #e74c3c; border-radius: 5px; margin-top: 5px; padding-top: 12px; } QGroupBox::title { color: #e74c3c; }")
        attack_layout = QVBoxLayout(attack_group)
        att_row = QHBoxLayout()
        att_row.addWidget(QLabel("Angreifer:"))
        self.attacker_combo = QComboBox()
        att_row.addWidget(self.attacker_combo, stretch=1)
        att_row.addWidget(QLabel("Verteidiger:"))
        self.defender_combo = QComboBox()
        att_row.addWidget(self.defender_combo, stretch=1)
        attack_layout.addLayout(att_row)
        attack_btn = QPushButton("Angriff würfeln!")
        attack_btn.setMinimumHeight(40)
        attack_btn.setStyleSheet("QPushButton { background: #e74c3c; color: white; font-size: 14px; font-weight: bold; }")
        attack_btn.clicked.connect(self._execute_attack)
        attack_layout.addWidget(attack_btn)
        self.attack_result_label = QLabel("")
        self.attack_result_label.setWordWrap(True)
        self.attack_result_label.setStyleSheet("font-size: 13px; color: #eee; padding: 5px;")
        attack_layout.addWidget(self.attack_result_label)
        layout.addWidget(attack_group)

        # Waffen
        weapons_group = QGroupBox("Waffen")
        weapons_layout = QVBoxLayout(weapons_group)
        self.weapons_list = QListWidget()
        weapons_layout.addWidget(self.weapons_list)
        weap_btn_layout = QHBoxLayout()
        add_weap_btn = QPushButton("+ Waffe hinzufügen")
        add_weap_btn.clicked.connect(self.add_weapon)
        weap_btn_layout.addWidget(add_weap_btn)
        weapons_layout.addLayout(weap_btn_layout)
        layout.addWidget(weapons_group)

        # Zauber
        spells_group = QGroupBox("Zauber/Magie")
        spells_layout = QVBoxLayout(spells_group)
        self.spells_list = QListWidget()
        spells_layout.addWidget(self.spells_list)
        spell_btn_layout = QHBoxLayout()
        add_spell_btn = QPushButton("+ Zauber hinzufügen")
        add_spell_btn.clicked.connect(self.add_spell)
        spell_btn_layout.addWidget(add_spell_btn)
        spells_layout.addLayout(spell_btn_layout)
        layout.addWidget(spells_group)

    # --- Public ---

    def refresh_combat_lists(self):
        """Aktualisiert Waffen- und Zauberlisten."""
        self.weapons_list.clear()
        self.spells_list.clear()
        world = self.data_manager.current_world
        if not world:
            return
        for weapon in world.weapons.values():
            self.weapons_list.addItem(f"{weapon.name} ({weapon.damage_min}-{weapon.damage_max} Schaden)")
        for spell in world.spells.values():
            self.spells_list.addItem(f"{spell.name}")

    def update_character_combos(self, characters: dict):
        """Aktualisiert Angreifer/Verteidiger ComboBoxen."""
        self.attacker_combo.blockSignals(True)
        self.defender_combo.blockSignals(True)
        self.attacker_combo.clear()
        self.defender_combo.clear()
        for cid, char in characters.items():
            self.attacker_combo.addItem(char.name, cid)
            self.defender_combo.addItem(char.name, cid)
        self.attacker_combo.blockSignals(False)
        self.defender_combo.blockSignals(False)

    # --- Private ---

    def roll_dice(self):
        count = self.dice_count_spin.value()
        sides_text = self.dice_sides_combo.currentText()
        sides = int(sides_text[1:])
        result = self.dice_roller.roll(dice_count=count, dice_sides=sides)
        rolls_str = ", ".join(map(str, result["rolls"]))
        self.dice_result_label.setText(f"{result['dice']}: [{rolls_str}] = {result['total']}")
        self.dice_rolled.emit(f"{result['dice']}: {rolls_str} = **{result['total']}**")

    def _execute_attack(self):
        session = self.data_manager.current_session
        world = self.data_manager.current_world
        if not session or not world:
            QMessageBox.warning(self, "Fehler", "Keine Session/Welt geladen!")
            return
        att_id = self.attacker_combo.currentData()
        def_id = self.defender_combo.currentData()
        if not att_id or not def_id:
            return
        if att_id == def_id:
            QMessageBox.warning(self, "Fehler", "Angreifer und Verteidiger müssen verschieden sein!")
            return
        attacker = session.characters.get(att_id)
        defender = session.characters.get(def_id)
        if not attacker or not defender:
            return

        if attacker.health <= 0:
            msg = f"{attacker.name} ist BESIEGT und kann nicht angreifen!"
            self.attack_result_label.setText(msg)
            self.status_message.emit(msg)
            return

        if defender.health <= 0:
            msg = f"{defender.name} ist bereits BESIEGT!"
            self.attack_result_label.setText(msg)
            self.status_message.emit(msg)
            return

        weapon = None
        if attacker.equipped_weapon and attacker.equipped_weapon in world.weapons:
            weapon = world.weapons[attacker.equipped_weapon]

        hit_roll = random.randint(1, 20)
        try:
            raw_acc = weapon.accuracy if weapon else 0.5
            accuracy = max(0.0, min(1.0, float(raw_acc if raw_acc is not None else 0.5)))
        except (ValueError, TypeError):
            accuracy = 0.5
        hit_threshold = max(1, int(20 - accuracy * 20))

        skill_bonus = 0
        if isinstance(world.skill_definitions, dict):
            for skill_name, skill_def in world.skill_definitions.items():
                if not isinstance(skill_def, dict):
                    continue
                affects = skill_def.get("affects", {})
                if isinstance(affects, (dict, list)) and ("strength" in affects or "dexterity" in affects):
                    skill_map = attacker.skills if isinstance(attacker.skills, dict) else {}
                    raw_val = skill_map.get(skill_name, 0)
                    with contextlib.suppress(ValueError, TypeError):
                        skill_bonus += int(raw_val or 0)

        lines = [f"--- ANGRIFF: {attacker.name} -> {defender.name} ---"]
        weapon_name = weapon.name if weapon else "Unbewaffnet"
        lines.append(f"Waffe: {weapon_name}")
        lines.append(f"Trefferwurf: W20 = {hit_roll} (+ Skill {skill_bonus}) vs. Schwelle {hit_threshold}")

        effective_roll = hit_roll + skill_bonus
        is_hit = effective_roll >= hit_threshold
        final_dmg = 0

        if not is_hit:
            lines.append("Ergebnis: VERFEHLT!")
        else:
            if weapon:
                try:
                    d_min = int(getattr(weapon, "damage_min", 1) or 1)
                    d_max = int(getattr(weapon, "damage_max", 6) or 6)
                except (ValueError, TypeError):
                    d_min, d_max = 1, 6
                if d_min > d_max:
                    d_min, d_max = d_max, d_min
                base_dmg = random.randint(d_min, d_max)
                try:
                    crit_thresh = int(getattr(weapon, "critical_threshold", 20) or 20)
                except (ValueError, TypeError):
                    crit_thresh = 20
                crit = hit_roll >= crit_thresh
                if crit:
                    try:
                        mult = float(getattr(weapon, "critical_multiplier", 2.0) or 2.0)
                    except (ValueError, TypeError):
                        mult = 2.0
                    base_dmg = int(base_dmg * mult)
                    lines.append(f"KRITISCHER TREFFER! (x{mult})")
            else:
                base_dmg = random.randint(1, 4)
                crit = hit_roll >= DEFAULT_UNARMED_CRIT_THRESHOLD
                if crit:
                    base_dmg *= 2
                    lines.append("KRITISCHER TREFFER! (x2)")

            try:
                str_val = int(getattr(attacker, "strength", 10) or 10)
            except (ValueError, TypeError):
                str_val = 10
            str_bonus = (str_val - 10) // 2
            total_dmg = max(0, base_dmg + str_bonus)

            armor_def = 0
            if defender.equipped_armor and defender.equipped_armor in world.armors:
                armor = world.armors[defender.equipped_armor]
                try:
                    armor_def = int(getattr(armor, "protection_avg", 0) or 0)
                except (ValueError, TypeError):
                    armor_def = 0
            final_dmg = max(0, total_dmg - armor_def)

            defender.health = max(0, defender.health - final_dmg)
            lines.append(f"Schaden: {base_dmg} (Basis) + {str_bonus} (Staerke) - {armor_def} (Ruestung) = {final_dmg}")
            lines.append(f"{defender.name}: {defender.health}/{defender.max_health} HP")
            if defender.health <= 0:
                lines.append(f"{defender.name} ist BESIEGT!")

        result_text = "\n".join(lines)
        self.attack_result_label.setText(result_text)

        self.data_manager.save_session(session)

        # Emit attack result with all needed data
        self.attack_executed.emit({
            "result_text": result_text,
            "is_hit": is_hit,
            "attacker_name": attacker.name,
            "defender_id": def_id,
            "defender_name": defender.name,
            "damage": final_dmg,
            "defender_health": defender.health,
            "defender_max_health": defender.max_health,
        })

    def add_weapon(self):
        world = self.data_manager.current_world
        if not world:
            return
        name, ok = QInputDialog.getText(self, "Neue Waffe", "Name der Waffe:")
        if ok and name:
            weapon_id = generate_short_id()
            weapon = Weapon(id=weapon_id, name=name)
            world.weapons[weapon_id] = weapon
            self.data_manager.save_world(world)
            self.weapons_list.addItem(f"{name}")

    def add_spell(self):
        world = self.data_manager.current_world
        if not world:
            return
        name, ok = QInputDialog.getText(self, "Neuer Zauber", "Name des Zaubers:")
        if ok and name:
            spell_id = generate_short_id()
            spell = Spell(id=spell_id, name=name)
            world.spells[spell_id] = spell
            self.data_manager.save_world(world)
            self.spells_list.addItem(f"{name}")
