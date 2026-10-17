"""Regressionstests fuer Ruleset-Import, Template-Validierung und Kampfsystem-Resilienz.
Software-Bugsearch 2026-10-18 (dev/bugsweep).
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from rpx_pro.models.enums import DamageType, SpellEffect, SpellTarget
from rpx_pro.models.entities import Character
from rpx_pro.models.world import World
from rpx_pro.widgets.ruleset_importer import RulesetImporter
from rpx_pro.tabs.combat_tab import CombatTab
from rpx_pro.managers.dice_roller import DiceRoller


class RulesetAndCombatResilienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        cls.app = QApplication.instance() or QApplication(sys.argv or ["test"])

    def setUp(self):
        self.world = World(id="test_world")
        self.world.settings.name = "Testwelt"

    def test_preview_handles_none_template_and_none_category_values(self):
        """preview stuerzt bei None-Template oder None-Kategoriewerten nicht mit TypeError/AttributeError ab."""
        # Facette 1: template = None
        res_none = RulesetImporter.preview(None)
        self.assertIsInstance(res_none, dict)
        self.assertEqual(res_none.get("races"), 0)

        # Facette 1: Kategoriewerte sind explizit None
        broken_template = {
            "races": None,
            "professions": None,
            "weapons": None,
            "armors": None,
            "spells": None,
            "dice_rules": None,
        }
        res_broken = RulesetImporter.preview(broken_template)
        self.assertEqual(res_broken["races"], 0)
        self.assertEqual(res_broken["professions"], 0)
        self.assertEqual(res_broken["weapons"], 0)
        self.assertEqual(res_broken["armors"], 0)
        self.assertEqual(res_broken["spells"], 0)
        self.assertEqual(res_broken["dice_rules"], 0)

    def test_import_ruleset_handles_none_categories_and_non_dict_template(self):
        """import_ruleset stuerzt bei None-Template oder None-Kategorien nicht mit AttributeError ab."""
        # Facette 2: template = None
        counts_none = RulesetImporter.import_ruleset(self.world, None)
        self.assertIsInstance(counts_none, dict)

        # Facette 2: None-Felder im Template
        broken_template = {
            "ruleset_name": "Broken World",
            "races": None,
            "professions": None,
            "weapons": None,
            "armors": None,
            "spells": None,
            "dice_rules": None,
        }
        counts = RulesetImporter.import_ruleset(self.world, broken_template)
        self.assertIsInstance(counts, dict)
        self.assertEqual(counts.get("races", 0), 0)

    def test_import_ruleset_empty_categories_set_respected(self):
        """import_ruleset respektiert categories=set() und importiert keine Kategorien."""
        # Facette 3: categories = set() darf nicht zu all_cats evaluieren
        template = {
            "races": {"elf": {"name": "Elf"}},
            "professions": ["Magier"],
        }
        counts = RulesetImporter.import_ruleset(self.world, template, categories=set())
        self.assertEqual(counts, {})
        self.assertNotIn("elf", self.world.races)
        self.assertNotIn("Magier", self.world.professions)

    def test_damage_type_and_spell_enums_case_insensitive_and_normalized(self):
        """Waffenschadens- und Zauber-Typen werden case-insensitiv aufgeloest statt still auf PHYSICAL/DAMAGE zurueckzufallen."""
        # Facette 4: Uppercase DamageType und SpellEffect
        template = {
            "weapons": {
                "flammenschwert": {
                    "name": "Flammenschwert",
                    "damage_type": "FIRE",
                    "damage_min": 2,
                    "damage_max": 8,
                },
                "frostklinge": {
                    "name": "Frostklinge",
                    "damage_type": "Ice",
                    "damage_min": 3,
                    "damage_max": 6,
                },
            },
            "spells": {
                "heilsegen": {
                    "name": "Heilsegen",
                    "effect_type": "HEAL",
                    "target_type": "ALL_ALLIES",
                    "effect_value": 20,
                    "mana_cost": 15,
                },
                "sturmwind": {
                    "name": "Sturmwind",
                    "effect_type": "DeBuff",
                    "target_type": "area",
                    "effect_value": 5,
                    "mana_cost": 10,
                },
            },
        }
        RulesetImporter.import_ruleset(self.world, template)
        self.assertEqual(self.world.weapons["flammenschwert"].damage_type, DamageType.FIRE)
        self.assertEqual(self.world.weapons["frostklinge"].damage_type, DamageType.ICE)
        self.assertEqual(self.world.spells["heilsegen"].effect_type, SpellEffect.HEAL)
        self.assertEqual(self.world.spells["heilsegen"].target_type, SpellTarget.ALL_ALLIES)
        self.assertEqual(self.world.spells["sturmwind"].effect_type, SpellEffect.DEBUFF)
        self.assertEqual(self.world.spells["sturmwind"].target_type, SpellTarget.AREA)

    def test_weapon_and_armor_bounds_inversion_and_none_guarded(self):
        """Invertierte Schadens- und Schutzgrenzen sowie None-Werte werden korrigiert."""
        # Facette 5: Invertierte Grenzen und None
        template = {
            "weapons": {
                "chaosdolch": {
                    "name": "Chaosdolch",
                    "damage_min": 10,
                    "damage_max": 2,
                    "accuracy": None,
                    "required_strength": None,
                }
            },
            "armors": {
                "spiegelruestung": {
                    "name": "Spiegelruestung",
                    "protection_min": 8,
                    "protection_max": 3,
                    "reliability": None,
                }
            },
        }
        RulesetImporter.import_ruleset(self.world, template)
        weap = self.world.weapons["chaosdolch"]
        self.assertEqual(weap.damage_min, 2)
        self.assertEqual(weap.damage_max, 10)
        self.assertEqual(weap.accuracy, 0.8)

        arm = self.world.armors["spiegelruestung"]
        self.assertEqual(arm.protection_min, 3)
        self.assertEqual(arm.protection_max, 8)
        self.assertEqual(arm.reliability, 0.9)

    def test_dice_rule_ranges_scalar_and_inverted_normalized(self):
        """Wuerfelregel-Bereiche mit Skalarwerten (20 statt [20, 20]) oder invertierten Werten ([20, 1]) werden normalisiert."""
        # Facette 6: ranges mit Skalar und invertierten Grenzen
        template = {
            "dice_rules": {
                "probenregel": {
                    "name": "Probenregel",
                    "dice_count": "2",
                    "dice_sides": "10",
                    "ranges": {
                        "Patzer": 20,
                        "Meisterlich": [1],
                        "Gelungen": [18, 2],
                    },
                }
            }
        }
        RulesetImporter.import_ruleset(self.world, template)
        drule = self.world.dice_rules["probenregel"]
        self.assertEqual(drule.dice_count, 2)
        self.assertEqual(drule.dice_sides, 10)
        self.assertEqual(drule.ranges["Patzer"], (20, 20))
        self.assertEqual(drule.ranges["Meisterlich"], (1, 1))
        self.assertEqual(drule.ranges["Gelungen"], (2, 18))

        # Verifikation mit DiceRoller
        roller = DiceRoller()
        roller.add_rule(drule)
        with patch("random.randint", side_effect=[10, 10]):  # Total 20 -> Patzer
            res = roller.roll("probenregel")
            self.assertEqual(res["total"], 20)
            self.assertEqual(res["outcome"], "Patzer")

    def test_skill_definitions_and_attributes_imported(self):
        """skills/skill_definitions und attributes aus Template werden in world.skill_definitions uebernommen."""
        # Facette 7: Skill- und Attribut-Import
        template = {
            "ruleset_name": "Cthulhu",
            "attributes": {
                "primary": ["STR", "CON", "DEX", "POW"],
            },
            "skills": {
                "verborgenes_erkennen": {
                    "name": "Verborgenes erkennen",
                    "base_value": 25,
                    "affects": {"dexterity": True},
                }
            },
        }
        RulesetImporter.import_ruleset(self.world, template)
        self.assertIn("verborgenes_erkennen", self.world.skill_definitions)
        self.assertIn("_ruleset_attributes", self.world.skill_definitions)
        self.assertEqual(
            self.world.skill_definitions["_ruleset_attributes"]["primary"],
            ["STR", "CON", "DEX", "POW"],
        )

    def test_combat_tab_execute_attack_guards_non_dict_skills_and_defeated_actors(self):
        """CombatTab._execute_attack stuerzt bei nicht-dict skills nicht mit AttributeError ab und verhindert Angriffe besiegter Akteure."""
        # Facette 8: CombatTab
        mock_dm = MagicMock()
        mock_session = MagicMock()
        mock_dm.current_session = mock_session
        mock_dm.current_world = self.world

        char_atk = Character(id="c_atk", name="Held", health=0, max_health=20)  # Besiegt!
        char_def = Character(id="c_def", name="Goblin", health=10, max_health=10)
        mock_session.characters = {"c_atk": char_atk, "c_def": char_def}

        # Nicht-dict skill definition in world
        self.world.skill_definitions["melee"] = "String statt Dict"

        tab = CombatTab(mock_dm, DiceRoller())
        tab.attacker_combo.addItem("Held", "c_atk")
        tab.defender_combo.addItem("Goblin", "c_def")
        tab.attacker_combo.setCurrentIndex(0)
        tab.defender_combo.setCurrentIndex(0)

        # Besiegter Angreifer
        with patch.object(mock_dm, "save_session") as mock_save:
            tab._execute_attack()
            self.assertIn("BESIEGT", tab.attack_result_label.text())
            mock_save.assert_not_called()

        # Angreifer lebt, Verteidiger lebt, skill_def ist String
        char_atk.health = 20
        with patch.object(mock_dm, "save_session"):
            tab._execute_attack()
            # Kein AttributeError, Angriff wurde ausgefuehrt
            self.assertIn("ANGRIFF", tab.attack_result_label.text())


if __name__ == "__main__":
    unittest.main()
