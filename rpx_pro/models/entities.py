"""Entitaeten-Dataclasses: Waffen, Ruestungen, Charaktere, Items, etc."""

import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple

from rpx_pro.constants import _filter_dataclass_fields
from rpx_pro.models.enums import (
    TriggerType, DamageType, SpellTarget, SpellEffect,
)


@dataclass
class Trigger:
    """Trigger fuer Orte (Sound, Licht, Chat)"""
    id: str
    trigger_type: TriggerType
    sound_file: Optional[str] = None
    sound_duration: float = 0.0
    light_effect: Optional[str] = None
    light_duration: float = 0.0
    chat_message: Optional[str] = None
    enabled: bool = True
    triggered_count: int = 0

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['trigger_type'] = self.trigger_type.value
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Trigger':
        data = dict(data)
        data['trigger_type'] = TriggerType(data['trigger_type'])
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class Weapon:
    """Waffe mit allen Eigenschaften"""
    id: str
    name: str
    image_path: Optional[str] = None
    accuracy: float = 0.8
    damage_min: int = 1
    damage_max: int = 10
    damage_avg: int = 5
    damage_type: DamageType = DamageType.PHYSICAL
    race_bonuses: Dict[str, int] = field(default_factory=dict)
    required_level: int = 1
    required_strength: int = 0
    required_skills: List[str] = field(default_factory=list)
    critical_multiplier: float = 2.0
    critical_threshold: int = 20
    range_type: str = "melee"
    description: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['damage_type'] = self.damage_type.value
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Weapon':
        data = dict(data)
        if 'damage_type' in data:
            data['damage_type'] = DamageType(data['damage_type'])
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class Armor:
    """Schutzgegenstand"""
    id: str
    name: str
    image_path: Optional[str] = None
    protection_min: int = 1
    protection_max: int = 10
    protection_avg: int = 5
    reliability: float = 0.9
    description: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Armor':
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class CombatTechnique:
    """Kampftechnik/Attacke mit Stufen"""
    id: str
    name: str
    description: str = ""
    required_level: int = 1
    required_race: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    levels: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    current_level: int = 1
    max_level: int = 5

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CombatTechnique':
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class Spell:
    """Zauber/Magie"""
    id: str
    name: str
    description: str = ""
    effect_type: SpellEffect = SpellEffect.DAMAGE
    effect_value: int = 10
    target_type: SpellTarget = SpellTarget.SINGLE_ENEMY
    has_range_limit: bool = True
    range_meters: float = 10.0
    affects_multiple: bool = False
    max_targets: int = 1
    mana_cost: int = 10
    required_level: int = 1
    required_intelligence: int = 0

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['effect_type'] = self.effect_type.value
        d['target_type'] = self.target_type.value
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Spell':
        data = dict(data)
        if 'effect_type' in data:
            data['effect_type'] = SpellEffect(data['effect_type'])
        if 'target_type' in data:
            data['target_type'] = SpellTarget(data['target_type'])
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class Character:
    """Charakter (Spieler oder NPC)"""
    id: str
    name: str
    race: str = ""
    profession: str = ""
    level: int = 1
    health: int = 100
    max_health: int = 100
    health_name: str = "Lebenskraft"
    mana: int = 50
    max_mana: int = 50
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    constitution: int = 10
    wisdom: int = 10
    charisma: int = 10
    custom_attributes: Dict[str, int] = field(default_factory=dict)
    skills: Dict[str, int] = field(default_factory=dict)
    equipped_weapon: Optional[str] = None
    equipped_armor: Optional[str] = None
    inventory: Dict[str, int] = field(default_factory=dict)
    combat_techniques: List[str] = field(default_factory=list)
    known_spells: List[str] = field(default_factory=list)
    biography: str = ""
    notes: str = ""
    image_path: Optional[str] = None
    is_npc: bool = False
    npc_type: str = "neutral"
    player_name: Optional[str] = None
    group_id: Optional[str] = None
    hunger: int = 0
    thirst: int = 0
    hunger_rate: float = 1.0
    thirst_rate: float = 1.5
    current_location: Optional[str] = None
    gold: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Character':
        data = dict(data)
        inv = data.get('inventory', {})
        if isinstance(inv, list):
            data['inventory'] = {item_id: 1 for item_id in inv}
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class Item:
    """Gegenstand (Klasse oder Einzelstueck)"""
    id: str
    name: str
    item_class: str = ""
    item_subclass: str = ""
    is_unique: bool = False
    description: str = ""
    weight: float = 0.0
    value: int = 0
    stackable: bool = True
    max_stack: int = 99
    health_bonus: int = 0
    strength_bonus: int = 0
    other_bonuses: Dict[str, int] = field(default_factory=dict)
    weapon_id: Optional[str] = None
    location_id: Optional[str] = None
    owner_id: Optional[str] = None
    find_probability: float = 1.0
    hidden: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class Vehicle:
    """Fahrzeug/Fortbewegungsmittel"""
    id: str
    name: str
    vehicle_class: str = ""
    image_path: Optional[str] = None
    speed_max: float = 50.0
    speed_min: float = 5.0
    speed_avg: float = 30.0
    propulsion_type: str = ""
    fuel_type: str = ""
    fuel_consumption_per_km: float = 0.1
    wear_level: float = 0.0
    description: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Vehicle':
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class RoadType:
    """Wegeart"""
    id: str
    name: str
    material: str = ""
    width_meters: float = 5.0
    roll_resistance: float = 1.0
    annual_weathering: float = 0.01
    description: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'RoadType':
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class Nation:
    """Nation/Land"""
    id: str
    name: str
    description: str = ""
    races: List[str] = field(default_factory=list)
    vegetation: str = ""
    climate: str = ""
    friendly_nations: List[str] = field(default_factory=list)
    hostile_nations: List[str] = field(default_factory=list)
    counties: List[str] = field(default_factory=list)
    cities: List[str] = field(default_factory=list)
    villages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Nation':
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class Race:
    """Volk/Rasse"""
    id: str
    name: str
    description: str = ""
    background_story: str = ""
    cultural_traits: str = ""
    abilities: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    hunger_modifier: float = 1.0
    thirst_modifier: float = 1.0
    special_needs: List[str] = field(default_factory=list)
    starvation_hours: float = 72.0
    dehydration_hours: float = 48.0

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Race':
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class DiceRule:
    """Wuerfelregel mit Zahlenbereichen"""
    id: str
    name: str
    dice_count: int = 1
    dice_sides: int = 20
    ranges: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    description: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'DiceRule':
        data = dict(data)
        if 'ranges' in data:
            data['ranges'] = {k: tuple(v) for k, v in data['ranges'].items()}
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class MapElement:
    """Ein Zeichenelement auf einer Karte"""
    id: str
    element_type: str
    x: float = 0.0
    y: float = 0.0
    width: float = 100.0
    height: float = 100.0
    x2: float = 0.0
    y2: float = 0.0
    color: str = "#e67e22"
    fill_color: str = ""
    line_width: float = 2.0
    opacity: float = 1.0
    text: str = ""
    font_size: int = 14
    image_path: str = ""
    rotation: float = 0.0

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**_filter_dataclass_fields(cls, data))


@dataclass
class GameMap:
    """Eine Karte mit Hintergrundbild und Zeichenelementen"""
    id: str
    name: str
    background_image: Optional[str] = None
    elements: Dict[str, 'MapElement'] = field(default_factory=dict)
    character_positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)

    def to_dict(self):
        d = asdict(self)
        d['elements'] = {k: v.to_dict() for k, v in self.elements.items()}
        return d

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        elements = {k: MapElement.from_dict(v) for k, v in data.pop('elements', {}).items()}
        filtered = _filter_dataclass_fields(cls, data)
        filtered['elements'] = elements
        return cls(**filtered)


@dataclass
class PlayerGroup:
    """Spielergruppe"""
    id: str
    name: str
    member_ids: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'PlayerGroup':
        return cls(**_filter_dataclass_fields(cls, data))
