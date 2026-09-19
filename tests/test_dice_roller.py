"""Unit-Tests fuer DiceRoller: Freies Wuerfeln und regelbasiertes Wuerfeln."""

import unittest
from unittest.mock import MagicMock

from rpx_pro.models.entities import DiceRule
from rpx_pro.managers.dice_roller import DiceRoller


class TestDiceRoller(unittest.TestCase):
    """Testfaelle fuer das DiceRoller-System."""

    def setUp(self):
        self.roller = DiceRoller()

    def test_roll_free_default(self):
        """Freies Wuerfeln ohne Argumente wuerfelt standardmaessig 1W20."""
        res = self.roller.roll()
        self.assertEqual(len(res["rolls"]), 1)
        self.assertEqual(res["dice"], "1W20")
        self.assertTrue(1 <= res["rolls"][0] <= 20)
        self.assertEqual(res["total"], res["rolls"][0])
        self.assertIsNone(res["outcome"])
        self.assertIsNone(res["rule_id"])
        self.assertIsNone(res["rule_name"])

    def test_roll_free_custom(self):
        """Freies Wuerfeln mit benutzerdefinierten Wuerfeln (z.B. 2W6)."""
        res = self.roller.roll(dice_count=2, dice_sides=6)
        self.assertEqual(len(res["rolls"]), 2)
        self.assertEqual(res["dice"], "2W6")
        self.assertTrue(2 <= res["total"] <= 12)
        for r in res["rolls"]:
            self.assertTrue(1 <= r <= 6)
        self.assertIsNone(res["outcome"])

    def test_roll_with_rule_respects_dice_count_and_sides(self):
        """Wuerfeln nach Regel muss dice_count und dice_sides der Regel beachten."""
        rule_3d6 = DiceRule(
            id="rule-3d6",
            name="3W6 Attributsprobe",
            dice_count=3,
            dice_sides=6,
            ranges={
                "Kritischer Erfolg": (18, 18),
                "Erfolg": (10, 17),
                "Misserfolg": (4, 9),
                "Patzer": (3, 3),
            },
            description="3W6 Standardprobe",
        )
        self.roller.add_rule(rule_3d6)

        res = self.roller.roll(rule_id="rule-3d6")
        # Pruefe, dass die Wuerfelanzahl und -seiten der Regel entsprechen:
        self.assertEqual(len(res["rolls"]), 3, "Regel mit 3 Wuerfeln muss 3 Einzelergebnisse liefern")
        self.assertEqual(res["dice"], "3W6", "Wuerfelbezeichnung muss 3W6 sein")
        self.assertTrue(3 <= res["total"] <= 18, "Gesamtwert muss im Bereich 3-18 liegen")
        for r in res["rolls"]:
            self.assertTrue(1 <= r <= 6, f"Einzelergebnis {r} muss im Bereich 1-6 liegen")
        self.assertIn(
            res["outcome"],
            ["Kritischer Erfolg", "Erfolg", "Misserfolg", "Patzer"],
            "Ergebnis muss einem der definierten Bereiche zugeordnet sein",
        )
        self.assertEqual(res["rule_id"], "rule-3d6")
        self.assertEqual(res["rule_name"], "3W6 Attributsprobe")

    def test_roll_with_rule_override_count_or_sides(self):
        """Optionale Uebersteuerung von dice_count/dice_sides bei regelbasiertem Wuerfeln."""
        rule = DiceRule(
            id="dsa-talent",
            name="Talentprobe",
            dice_count=3,
            dice_sides=20,
            ranges={"Bestanden": (3, 45), "Nicht bestanden": (46, 60)},
        )
        self.roller.add_rule(rule)

        # Uebersteuerung der Wuerfelanzahl auf 4
        res = self.roller.roll(rule_id="dsa-talent", dice_count=4)
        self.assertEqual(len(res["rolls"]), 4)
        self.assertEqual(res["dice"], "4W20")
        for r in res["rolls"]:
            self.assertTrue(1 <= r <= 20)

    def test_roll_with_inverted_ranges(self):
        """Bereiche mit umgekehrter Min/Max-Reihenfolge (z.B. (20, 10)) werden sicher ausgewertet."""
        rule = DiceRule(
            id="inverted-rule",
            name="Invertierte Regel",
            dice_count=1,
            dice_sides=20,
            ranges={"High": (20, 11), "Low": (10, 1)},
        )
        self.roller.add_rule(rule)
        res = self.roller.roll(rule_id="inverted-rule")
        self.assertIn(res["outcome"], ["High", "Low"])

    def test_load_rules_from_world(self):
        """Wuerfelregeln koennen aus einem World-Objekt geladen werden."""
        world_mock = MagicMock()
        r1 = DiceRule(id="r1", name="Regel 1", dice_count=2, dice_sides=10)
        r2 = DiceRule(id="r2", name="Regel 2", dice_count=1, dice_sides=100)
        world_mock.dice_rules = {"r1": r1, "r2": r2}

        self.roller.load_rules_from_world(world_mock)
        self.assertIn("r1", self.roller.rules)
        self.assertIn("r2", self.roller.rules)

    def test_unknown_rule_fallback(self):
        """Unbekannte Regel-ID fuehrt nicht zum Absturz, sondern faellt auf Standard zurueck."""
        res = self.roller.roll(rule_id="nonexistent-rule")
        self.assertEqual(res["dice"], "1W20")
        self.assertEqual(len(res["rolls"]), 1)
        self.assertIsNone(res["outcome"])
        self.assertEqual(res["rule_id"], "nonexistent-rule")
        self.assertIsNone(res["rule_name"])


if __name__ == "__main__":
    unittest.main()
