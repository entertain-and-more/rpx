"""RulesetImporter + RulesetImportDialog: Regelwerk-Import-System."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QGroupBox, QCheckBox, QDialogButtonBox, QFileDialog, QMessageBox,
)

from rpx_pro.constants import RULESETS_DIR, logger
from rpx_pro.models.enums import DamageType, SpellEffect, SpellTarget
from rpx_pro.models.entities import (
    Race, Weapon, Armor, Spell, DiceRule,
)
from rpx_pro.models.world import World
from rpx_pro.managers.data_manager import DataManager


def _parse_damage_type(val: Any) -> DamageType:
    if isinstance(val, DamageType):
        return val
    if isinstance(val, str):
        cleaned = val.strip().lower()
        for member in DamageType:
            if member.value == cleaned or member.name.lower() == cleaned:
                return member
    return DamageType.PHYSICAL


def _parse_spell_effect(val: Any) -> SpellEffect:
    if isinstance(val, SpellEffect):
        return val
    if isinstance(val, str):
        cleaned = val.strip().lower()
        for member in SpellEffect:
            if member.value == cleaned or member.name.lower() == cleaned:
                return member
    return SpellEffect.DAMAGE


def _parse_spell_target(val: Any) -> SpellTarget:
    if isinstance(val, SpellTarget):
        return val
    if isinstance(val, str):
        cleaned = val.strip().lower()
        for member in SpellTarget:
            if member.value == cleaned or member.name.lower() == cleaned:
                return member
    return SpellTarget.SINGLE_ENEMY


def _safe_int(val: Any, default: int = 0) -> int:
    try:
        if val is None or val == "":
            return default
        return int(val)
    except (ValueError, TypeError):
        return default


def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        if val is None or val == "":
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


def _normalize_range(vals: Any) -> Tuple[int, int]:
    if isinstance(vals, (int, float)):
        v = int(vals)
        return (v, v)
    if isinstance(vals, (list, tuple)):
        clean_vals = []
        for x in vals:
            try:
                clean_vals.append(int(x))
            except (ValueError, TypeError):
                continue
        if len(clean_vals) == 1:
            return (clean_vals[0], clean_vals[0])
        elif len(clean_vals) >= 2:
            return (min(clean_vals[0], clean_vals[1]), max(clean_vals[0], clean_vals[1]))
    return (1, 20)


class RulesetImporter:
    """Importiert Regelwerk-Templates in eine Welt"""

    @staticmethod
    def list_builtin_rulesets() -> List[Dict[str, str]]:
        """Listet alle eingebauten Regelwerk-Templates"""
        rulesets = []
        if RULESETS_DIR.exists():
            for path in sorted(RULESETS_DIR.glob("*.json")):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        rulesets.append({
                            "path": str(path),
                            "id": data.get("ruleset_id", path.stem),
                            "name": data.get("ruleset_name", path.stem),
                            "description": data.get("description", ""),
                        })
                except Exception as e:
                    logger.warning(f"Regelwerk-Datei konnte nicht geladen werden: {path} -- {e}")
        return rulesets

    @staticmethod
    def load_template(path: str) -> Optional[Dict]:
        """Laedt ein Regelwerk-Template"""
        if not path or not isinstance(path, (str, Path)):
            return None
        p = Path(path)
        if not p.is_file():
            return None
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, dict) else None
        except Exception as e:
            logger.error(f"Fehler beim Laden des Regelwerks: {e}")
            return None

    @staticmethod
    def preview(template: Optional[Dict]) -> Dict[str, int]:
        """Gibt eine Vorschau der importierbaren Elemente zurueck"""
        if not isinstance(template, dict):
            return {
                "races": 0, "professions": 0, "weapons": 0,
                "armors": 0, "spells": 0, "dice_rules": 0,
            }
        return {
            "races": len(template.get("races") or {}),
            "professions": len(template.get("professions") or []),
            "weapons": len(template.get("weapons") or {}),
            "armors": len(template.get("armors") or {}),
            "spells": len(template.get("spells") or {}),
            "dice_rules": len(template.get("dice_rules") or {}),
        }

    @staticmethod
    def import_ruleset(world: World, template: Optional[Dict],
                       categories: Optional[set] = None) -> Dict[str, int]:
        """Importiert ein Template in eine bestehende Welt."""
        counts: Dict[str, int] = {}
        if not isinstance(template, dict):
            return counts
        all_cats = {"races", "professions", "weapons", "armors", "spells", "dice_rules"}
        cats = categories if categories is not None else all_cats

        if "races" in cats:
            races_dict = template.get("races")
            if isinstance(races_dict, dict):
                for rid, rdata in races_dict.items():
                    if not isinstance(rdata, dict):
                        continue
                    world.races[str(rid)] = Race(
                        id=str(rid),
                        name=str(rdata.get("name") or rid),
                        description=str(rdata.get("description") or ""),
                        abilities=list(rdata.get("abilities") or []) if isinstance(rdata.get("abilities"), (list, tuple)) else ([str(rdata.get("abilities"))] if rdata.get("abilities") else []),
                        strengths=list(rdata.get("strengths") or []) if isinstance(rdata.get("strengths"), (list, tuple)) else [],
                        weaknesses=list(rdata.get("weaknesses") or []) if isinstance(rdata.get("weaknesses"), (list, tuple)) else [],
                        hunger_modifier=max(0.1, _safe_float(rdata.get("hunger_modifier"), 1.0)),
                        thirst_modifier=max(0.1, _safe_float(rdata.get("thirst_modifier"), 1.0)),
                    )
                counts["races"] = len([r for r in races_dict.values() if isinstance(r, dict)])

        if "professions" in cats:
            profs = template.get("professions")
            added = 0
            if isinstance(profs, (list, tuple)):
                for p in profs:
                    if p and isinstance(p, str) and p not in world.professions:
                        world.professions.append(p)
                        added += 1
            counts["professions"] = added

        if "weapons" in cats:
            weaps_dict = template.get("weapons")
            if isinstance(weaps_dict, dict):
                for wid, wdata in weaps_dict.items():
                    if not isinstance(wdata, dict):
                        continue
                    dt = _parse_damage_type(wdata.get("damage_type"))
                    d_min = max(0, _safe_int(wdata.get("damage_min"), 1))
                    d_max = max(0, _safe_int(wdata.get("damage_max"), 6))
                    if d_min > d_max:
                        d_min, d_max = d_max, d_min
                    d_avg = _safe_int(wdata.get("damage_avg"), (d_min + d_max) // 2)
                    acc = max(0.0, min(1.0, _safe_float(wdata.get("accuracy"), 0.8)))
                    req_str = max(0, _safe_int(wdata.get("required_strength"), 0))
                    req_lvl = max(1, _safe_int(wdata.get("required_level"), 1))
                    world.weapons[str(wid)] = Weapon(
                        id=str(wid),
                        name=str(wdata.get("name") or wid),
                        damage_min=d_min,
                        damage_max=d_max,
                        damage_avg=d_avg,
                        damage_type=dt,
                        accuracy=acc,
                        required_strength=req_str,
                        required_level=req_lvl,
                        description=str(wdata.get("description") or ""),
                    )
                counts["weapons"] = len([w for w in weaps_dict.values() if isinstance(w, dict)])

        if "armors" in cats:
            armors_dict = template.get("armors")
            if isinstance(armors_dict, dict):
                for aid, adata in armors_dict.items():
                    if not isinstance(adata, dict):
                        continue
                    p_min = max(0, _safe_int(adata.get("protection_min"), 1))
                    p_max = max(0, _safe_int(adata.get("protection_max"), 5))
                    if p_min > p_max:
                        p_min, p_max = p_max, p_min
                    p_avg = _safe_int(adata.get("protection_avg"), (p_min + p_max) // 2)
                    rel = max(0.0, min(1.0, _safe_float(adata.get("reliability"), 0.9)))
                    world.armors[str(aid)] = Armor(
                        id=str(aid),
                        name=str(adata.get("name") or aid),
                        protection_min=p_min,
                        protection_max=p_max,
                        protection_avg=p_avg,
                        reliability=rel,
                        description=str(adata.get("description") or ""),
                    )
                counts["armors"] = len([a for a in armors_dict.values() if isinstance(a, dict)])

        if "spells" in cats:
            spells_dict = template.get("spells")
            if isinstance(spells_dict, dict):
                for sid, sdata in spells_dict.items():
                    if not isinstance(sdata, dict):
                        continue
                    eff = _parse_spell_effect(sdata.get("effect_type"))
                    tgt = _parse_spell_target(sdata.get("target_type"))
                    eff_val = max(0, _safe_int(sdata.get("effect_value"), 10))
                    mana = max(0, _safe_int(sdata.get("mana_cost"), 10))
                    req_lvl = max(1, _safe_int(sdata.get("required_level"), 1))
                    req_int = max(0, _safe_int(sdata.get("required_intelligence"), 0))
                    world.spells[str(sid)] = Spell(
                        id=str(sid),
                        name=str(sdata.get("name") or sid),
                        effect_type=eff,
                        effect_value=eff_val,
                        target_type=tgt,
                        mana_cost=mana,
                        required_level=req_lvl,
                        required_intelligence=req_int,
                        description=str(sdata.get("description") or ""),
                    )
                counts["spells"] = len([s for s in spells_dict.values() if isinstance(s, dict)])

        if "dice_rules" in cats:
            dr_dict = template.get("dice_rules")
            if isinstance(dr_dict, dict):
                for drid, drdata in dr_dict.items():
                    if not isinstance(drdata, dict):
                        continue
                    ranges = {}
                    raw_ranges = drdata.get("ranges")
                    if isinstance(raw_ranges, dict):
                        for label, vals in raw_ranges.items():
                            ranges[str(label)] = _normalize_range(vals)
                    d_count = max(1, _safe_int(drdata.get("dice_count"), 1))
                    d_sides = max(1, _safe_int(drdata.get("dice_sides"), 20))
                    world.dice_rules[str(drid)] = DiceRule(
                        id=str(drid),
                        name=str(drdata.get("name") or drid),
                        dice_count=d_count,
                        dice_sides=d_sides,
                        ranges=ranges,
                        description=str(drdata.get("description") or ""),
                    )
                counts["dice_rules"] = len([d for d in dr_dict.values() if isinstance(d, dict)])

        # Skills & Attribute importieren
        skills = template.get("skills") or template.get("skill_definitions")
        if isinstance(skills, dict):
            for sk_id, sk_def in skills.items():
                if isinstance(sk_def, dict):
                    world.skill_definitions[str(sk_id)] = sk_def

        attrs = template.get("attributes")
        if isinstance(attrs, dict):
            world.skill_definitions["_ruleset_attributes"] = attrs

        if template.get("ruleset_name"):
            world.settings.genre = str(template["ruleset_name"])

        logger.info(f"Regelwerk importiert: {template.get('ruleset_name', '?')} -> {counts}")
        return counts


class RulesetImportDialog(QDialog):
    """Dialog zum Importieren von Regelwerk-Templates"""

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.template: Optional[Dict] = None
        self.template_path: Optional[str] = None
        self.setWindowTitle("Regelwerk importieren")
        self.setMinimumWidth(500)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        source_group = QGroupBox("Regelwerk auswählen")
        source_layout = QVBoxLayout(source_group)

        self.ruleset_combo = QComboBox()
        builtin = RulesetImporter.list_builtin_rulesets()
        for rs in builtin:
            self.ruleset_combo.addItem(f"{rs['name']}", rs["path"])
        self.ruleset_combo.addItem("Eigene Datei laden...", "__custom__")
        self.ruleset_combo.currentIndexChanged.connect(self._on_ruleset_changed)
        source_layout.addWidget(self.ruleset_combo)

        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        source_layout.addWidget(self.desc_label)
        layout.addWidget(source_group)

        self.preview_group = QGroupBox("Vorschau")
        self.preview_layout = QVBoxLayout(self.preview_group)
        self.preview_label = QLabel("Bitte Regelwerk auswählen")
        self.preview_layout.addWidget(self.preview_label)
        layout.addWidget(self.preview_group)

        cat_group = QGroupBox("Kategorien importieren")
        cat_layout = QVBoxLayout(cat_group)
        self.cat_checks = {}
        labels = {"races": "Völker/Rassen", "professions": "Professionen/Klassen",
                  "weapons": "Waffen", "armors": "Rüstungen",
                  "spells": "Zauber", "dice_rules": "Würfelregeln"}
        for key, label in labels.items():
            cb = QCheckBox(label)
            cb.setChecked(True)
            self.cat_checks[key] = cb
            cat_layout.addWidget(cb)
        layout.addWidget(cat_group)

        target_group = QGroupBox("Ziel")
        target_layout = QVBoxLayout(target_group)
        self.target_combo = QComboBox()
        self.target_combo.addItem("Neue Welt erstellen", "__new__")
        for wid, w in self.data_manager.worlds.items():
            self.target_combo.addItem(f"{w.settings.name} ({w.settings.genre})", wid)
        target_layout.addWidget(self.target_combo)
        layout.addWidget(target_group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if self.ruleset_combo.count() > 0:
            self._on_ruleset_changed(0)

    def _on_ruleset_changed(self, index):
        path = self.ruleset_combo.currentData()
        if path == "__custom__":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Regelwerk-Datei öffnen", "", "JSON (*.json)")
            if not file_path:
                self.ruleset_combo.blockSignals(True)
                self.ruleset_combo.setCurrentIndex(0)
                self.ruleset_combo.blockSignals(False)
                return
            path = file_path

        self.template = RulesetImporter.load_template(path)
        self.template_path = path
        if self.template:
            self.desc_label.setText(self.template.get("description", ""))
            preview = RulesetImporter.preview(self.template)
            lines = []
            labels = {"races": "Völker", "professions": "Professionen",
                      "weapons": "Waffen", "armors": "Rüstungen",
                      "spells": "Zauber", "dice_rules": "Würfelregeln"}
            for key, label in labels.items():
                count = preview.get(key, 0)
                lines.append(f"  {label}: {count}")
            self.preview_label.setText("\n".join(lines))
        else:
            self.preview_label.setText("Fehler beim Laden")

    def _on_accept(self):
        if not self.template:
            QMessageBox.warning(self, "Fehler", "Kein Regelwerk geladen!")
            return

        cats = set()
        for key, cb in self.cat_checks.items():
            if cb.isChecked():
                cats.add(key)

        if not cats:
            QMessageBox.warning(self, "Fehler", "Keine Kategorien ausgewählt!")
            return

        target = self.target_combo.currentData()
        if target == "__new__":
            name = self.template.get("ruleset_name", "Neue Welt")
            world = self.data_manager.create_world(name, name)
        else:
            world = self.data_manager.worlds.get(target)
            if not world:
                QMessageBox.warning(self, "Fehler", "Welt nicht gefunden!")
                return

        counts = RulesetImporter.import_ruleset(world, self.template, cats)
        self.data_manager.save_world(world)
        self.data_manager.current_world = world

        summary = "\n".join(f"  {k}: {v}" for k, v in counts.items() if v > 0)
        QMessageBox.information(self, "Import abgeschlossen",
                                f"Regelwerk '{self.template.get('ruleset_name', '?')}' importiert:\n\n{summary}")
        self.accept()
