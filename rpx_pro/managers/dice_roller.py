"""DiceRoller: Wuerfelsystem mit konfigurierbaren Regeln."""

import random
import time
from typing import Dict, List, Any, Optional

from rpx_pro.models.entities import DiceRule


class DiceRoller:
    """Wuerfelsystem mit konfigurierbaren Regeln."""

    def __init__(self):
        self.rules: Dict[str, DiceRule] = {}
        self.history: List[Dict[str, Any]] = []

    def add_rule(self, rule: DiceRule):
        """Fuegt eine Wuerfelregel hinzu."""
        self.rules[rule.id] = rule

    def load_rules_from_world(self, world: Any):
        """Laedt alle Wuerfelregeln aus einer Spielwelt."""
        if hasattr(world, "dice_rules") and isinstance(world.dice_rules, dict):
            for rule in world.dice_rules.values():
                if isinstance(rule, DiceRule):
                    self.add_rule(rule)

    def clear_rules(self):
        """Entfernt alle registrierten Wuerfelregeln."""
        self.rules.clear()

    def roll(
        self,
        rule_id: Optional[str] = None,
        dice_count: Optional[int] = None,
        dice_sides: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Wuerfelt nach Regel oder frei."""
        rule = self.rules.get(rule_id) if rule_id else None

        if rule is not None:
            count = dice_count if dice_count is not None else rule.dice_count
            sides = dice_sides if dice_sides is not None else rule.dice_sides
        else:
            count = dice_count if dice_count is not None else 1
            sides = dice_sides if dice_sides is not None else 20

        count = max(1, int(count))
        sides = max(1, int(sides))
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)

        outcome = None
        if rule and rule.ranges:
            for outcome_name, bounds in rule.ranges.items():
                if isinstance(bounds, (list, tuple)) and len(bounds) >= 2:
                    min_val = min(bounds[0], bounds[1])
                    max_val = max(bounds[0], bounds[1])
                    if min_val <= total <= max_val:
                        outcome = outcome_name
                        break

        result = {
            "rolls": rolls,
            "total": total,
            "dice": f"{count}W{sides}",
            "timestamp": time.time(),
            "outcome": outcome,
            "rule_id": rule.id if rule else (rule_id if rule_id else None),
            "rule_name": rule.name if rule else None,
        }

        self.history.append(result)
        return result

    def get_last_rolls(self, count: int = 10) -> List[Dict[str, Any]]:
        """Gibt die letzten Wuerfe zurueck."""
        return self.history[-count:]
