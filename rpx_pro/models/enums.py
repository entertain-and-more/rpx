"""Enums und einfache Hilfsklassen fuer RPX Pro."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


class MessageRole(Enum):
    """Rollen fuer Chat-Nachrichten"""
    PLAYER = "player"
    GM = "gm"
    AI_STORYTELLER = "ai_storyteller"
    AI_WORLD_DESIGNER = "ai_world_designer"
    AI_NPC = "ai_npc"
    AI_PLOTTWIST = "ai_plottwist"
    AI_ENEMY = "ai_enemy"
    AI_LANDSCAPE = "ai_landscape"
    AI_FAUNA_FLORA = "ai_fauna_flora"
    SYSTEM = "system"
    NARRATOR = "narrator"


class MissionStatus(Enum):
    """Status einer Mission/Quest"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TriggerType(Enum):
    """Trigger-Typen fuer Orte"""
    ON_EVERY_ENTER = "on_every_enter"
    ON_FIRST_ENTER = "on_first_enter"
    ON_EVERY_LEAVE = "on_every_leave"
    ON_FIRST_LEAVE = "on_first_leave"
    RANDOM = "random"


class PlayerScreenMode(Enum):
    """Anzeigemodus des Spieler-Bildschirms"""
    IMAGE = "image"
    MAP = "map"
    ROTATING = "rotating"
    TILES = "tiles"


class DamageType(Enum):
    """Schadenstypen"""
    PHYSICAL = "physical"
    MAGICAL = "magical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"


class SpellTarget(Enum):
    """Zieltypen fuer Zauber"""
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    SINGLE_ALLY = "single_ally"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"
    AREA = "area"
    OBJECT = "object"


class SpellEffect(Enum):
    """Zauber-Wirkungstypen"""
    DAMAGE = "damage"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"
    MANIPULATION = "manipulation"
    SUMMON = "summon"


class TimeOfDay(Enum):
    """Tageszeit"""
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    MIDNIGHT = "midnight"


class WeatherType(Enum):
    """Wettertypen"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"


@dataclass
class PlayerEvent:
    """Event das an den Spieler-Bildschirm geroutet wird"""
    event_type: str
    data: dict
    source_tab: str


class ActionCollector:
    """Sammelt Spieleraktionen und sendet sie gebuendelt."""

    def __init__(self):
        self.pending_actions: List[Dict[str, Any]] = []
        self.max_actions: int = 5
        self.auto_send: bool = False

    def add_action(self, character_id: str, action_type: str,
                   description: str, target: Optional[str] = None) -> bool:
        if len(self.pending_actions) >= self.max_actions:
            return False
        action = {
            "character_id": character_id,
            "action_type": action_type,
            "description": description,
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
        self.pending_actions.append(action)
        return True

    def get_actions_summary(self) -> str:
        if not self.pending_actions:
            return "Keine Aktionen gesammelt."
        summary = f"=== {len(self.pending_actions)} Gesammelte Aktionen ===\n"
        for i, action in enumerate(self.pending_actions, 1):
            summary += f"\n{i}. [{action['action_type']}] {action['description']}"
            if action['target']:
                summary += f" -> Ziel: {action['target']}"
        return summary

    def send_actions(self) -> List[Dict[str, Any]]:
        actions = self.pending_actions.copy()
        self.pending_actions.clear()
        return actions

    def clear_actions(self):
        self.pending_actions.clear()

    def get_action_count(self) -> int:
        return len(self.pending_actions)
