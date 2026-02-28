#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                             RPX LIGHT v1.0                                   ║
║                      RolePlay Xtreme - Light Edition                         ║
║══════════════════════════════════════════════════════════════════════════════║
║                                                                              ║
║  Das schlanke Rollenspiel-Kontrollzentrum für den schnellen Einstieg        ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │  🎵 AUDIO          Soundboard • Hintergrundmusik • Lautstärke          │ ║
║  │  💡 LICHT          Blitz • Stroboskop • Tag/Nacht • Farbfilter         │ ║
║  │  🌍 WELTEN         Karten • Orte • Nationen • Völker                   │ ║
║  │  🎲 WÜRFEL         Konfigurierbares Würfelsystem                       │ ║
║  │  📜 SESSION        Missionen • Rundensteuerung • Charaktere            │ ║
║  │  🤖 KI-PROMPTS     5 KI-Rollen • Spielstart • Update                   │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  💡 Upgrade auf RPX PRO für: Waffen, Magie, Trigger, Items, Fahrzeuge      ║
║                                                                              ║
║  © 2025 RPX Development                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import json
import logging
import time
import random
import uuid
import threading
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from functools import partial

# GUI Framework
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QSplitter, QDockWidget, QLineEdit, QComboBox, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QFileDialog, QMessageBox, 
    QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem, QSlider, 
    QScrollArea, QFrame, QGridLayout, QStatusBar, QMenuBar, QMenu, QToolBar,
    QProgressBar, QStackedWidget, QFormLayout, QTextBrowser, QColorDialog,
    QInputDialog, QHeaderView, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import (
    Qt, Signal, QThread, QTimer, QSize, Slot, QUrl, QPropertyAnimation,
    QEasingCurve, Property, QObject, QMutex, QWaitCondition
)
from PySide6.QtGui import (
    QAction, QIcon, QFont, QColor, QPalette, QPixmap, QTextCursor,
    QBrush, QPainter, QLinearGradient, QKeySequence, QShortcut
)

# ============================================================================
# AUDIO-UNTERSTÜTZUNG (Multi-Backend)
# ============================================================================

HAS_AUDIO = False
AUDIO_BACKEND = None

# Versuch 1: QSoundEffect (immer verfügbar in PySide6)
try:
    from PySide6.QtMultimedia import QSoundEffect
    HAS_SOUND_EFFECT = True
except ImportError:
    HAS_SOUND_EFFECT = False

# Versuch 2: QMediaPlayer (benötigt Backends)
try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    # Test ob Backend verfügbar
    _test_player = QMediaPlayer()
    if _test_player.isAvailable():
        HAS_AUDIO = True
        AUDIO_BACKEND = "QtMultimedia"
    del _test_player
except Exception:
    pass

# Versuch 3: pygame als Fallback
if not HAS_AUDIO:
    try:
        import pygame
        pygame.mixer.init()
        HAS_AUDIO = True
        AUDIO_BACKEND = "pygame"
        print("✓ Audio: pygame Backend aktiv")
    except Exception:
        pass

# Versuch 4: winsound für Windows (nur WAV)
if not HAS_AUDIO and sys.platform == 'win32':
    try:
        import winsound
        HAS_AUDIO = True
        AUDIO_BACKEND = "winsound"
        print("✓ Audio: winsound Backend aktiv (nur WAV)")
    except Exception:
        pass

# Fallback: QSoundEffect für einfache Sounds
if not HAS_AUDIO and HAS_SOUND_EFFECT:
    HAS_AUDIO = True
    AUDIO_BACKEND = "QSoundEffect"
    print("✓ Audio: QSoundEffect Backend aktiv (nur WAV)")

if not HAS_AUDIO:
    print("⚠ Kein Audio-Backend verfügbar - Audio deaktiviert")
    print("  Installiere pygame für Audio: pip install pygame")

# ============================================================================
# KONSTANTEN UND KONFIGURATION
# ============================================================================

APP_TITLE = "RPX Light"
VERSION = "1.0.0"
SCHEMA_VERSION = "1.0"

# Verzeichnisstruktur (Light-Version - reduziert)
PROJECT_ROOT = Path.cwd() / "rpx_light_data"
WORLDS_DIR = PROJECT_ROOT / "worlds"
SESSIONS_DIR = PROJECT_ROOT / "sessions"
CHARACTERS_DIR = PROJECT_ROOT / "characters"
MEDIA_DIR = PROJECT_ROOT / "media"
SOUNDS_DIR = MEDIA_DIR / "sounds"
IMAGES_DIR = MEDIA_DIR / "images"
MUSIC_DIR = MEDIA_DIR / "music"
MAPS_DIR = MEDIA_DIR / "maps"
BACKUPS_DIR = PROJECT_ROOT / "backups"
CONFIG_FILE = PROJECT_ROOT / "config.json"
LOG_FILE = PROJECT_ROOT / "rpx_light.log"

# Pro-only Verzeichnisse (für Kompatibilität als None)
ITEMS_DIR = None
WEAPONS_DIR = None
ARMOR_DIR = None
SPELLS_DIR = None
VEHICLES_DIR = None

# Alle Verzeichnisse erstellen
ALL_DIRS = [
    PROJECT_ROOT, WORLDS_DIR, SESSIONS_DIR, CHARACTERS_DIR, MEDIA_DIR,
    SOUNDS_DIR, IMAGES_DIR, MUSIC_DIR, MAPS_DIR, BACKUPS_DIR
]
for directory in ALL_DIRS:
    directory.mkdir(parents=True, exist_ok=True)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("UltimateRPG")

# ============================================================================
# ENUMS - Alle Rollen und Status-Typen
# ============================================================================

class MessageRole(Enum):
    """Rollen für Chat-Nachrichten"""
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
    """Trigger-Typen für Orte"""
    ON_EVERY_ENTER = "on_every_enter"
    ON_FIRST_ENTER = "on_first_enter"
    ON_EVERY_LEAVE = "on_every_leave"
    ON_FIRST_LEAVE = "on_first_leave"
    RANDOM = "random"

# ============================================================================
# AKTIONEN-SAMMLER (NEU für RPX Light)
# ============================================================================

class ActionCollector:
    """Sammelt Spieleraktionen und sendet sie gebündelt."""
    
    def __init__(self):
        self.pending_actions: List[Dict[str, Any]] = []
        self.max_actions: int = 5
        self.auto_send: bool = False
    
    def add_action(self, character_id: str, action_type: str, 
                   description: str, target: Optional[str] = None) -> bool:
        """Fügt eine Aktion zur Warteschlange hinzu.
        
        Returns:
            True wenn Aktion hinzugefügt, False wenn Limit erreicht
        """
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
        """Erstellt eine Zusammenfassung aller gesammelten Aktionen."""
        if not self.pending_actions:
            return "Keine Aktionen gesammelt."
        
        summary = f"=== {len(self.pending_actions)} Gesammelte Aktionen ===\n"
        for i, action in enumerate(self.pending_actions, 1):
            summary += f"\n{i}. [{action['action_type']}] {action['description']}"
            if action['target']:
                summary += f" → Ziel: {action['target']}"
        
        return summary
    
    def send_actions(self) -> List[Dict[str, Any]]:
        """Sendet alle gesammelten Aktionen und leert die Warteschlange.
        
        Returns:
            Liste der gesendeten Aktionen
        """
        actions = self.pending_actions.copy()
        self.pending_actions.clear()
        return actions
    
    def clear_actions(self):
        """Löscht alle gesammelten Aktionen."""
        self.pending_actions.clear()
    
    def get_action_count(self) -> int:
        """Gibt die Anzahl gesammelter Aktionen zurück."""
        return len(self.pending_actions)


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
    """Zieltypen für Zauber"""
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

# ============================================================================
# DATENMODELLE - Dataclasses für alle Entitäten
# ============================================================================

@dataclass
class ChatMessage:
    """Repräsentiert eine Chat-Nachricht"""
    role: MessageRole
    author: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'role': self.role.value,
            'author': self.author,
            'content': self.content,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChatMessage':
        return cls(
            role=MessageRole(data['role']),
            author=data['author'],
            content=data['content'],
            timestamp=data.get('timestamp', time.time()),
            metadata=data.get('metadata', {})
        )

@dataclass
class Trigger:
    """Trigger für Orte (Sound, Licht, Chat)"""
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
        data['trigger_type'] = TriggerType(data['trigger_type'])
        return cls(**data)

@dataclass
class Location:
    """Ort in der Spielwelt mit Außen-/Innenansicht"""
    id: str
    name: str
    description: str = ""
    parent_id: Optional[str] = None
    # Bilder
    exterior_image: Optional[str] = None
    interior_image: Optional[str] = None
    map_position: Tuple[int, int] = (0, 0)
    # Audio
    ambient_sound: Optional[str] = None
    ambient_volume: float = 0.5
    entry_sound: Optional[str] = None
    exit_sound: Optional[str] = None
    background_music: Optional[str] = None
    # Eigenschaften
    has_interior: bool = False
    visited: bool = False
    first_visit: bool = True
    # Trigger
    triggers: List[Trigger] = field(default_factory=list)
    # Farbfilter
    color_filter: Optional[str] = None
    color_filter_opacity: float = 0.3
    # Items an diesem Ort
    items: List[str] = field(default_factory=list)
    # Preisliste (für Shops/Tavernen)
    price_list_file: Optional[str] = None
    # Zusätzliche Infos
    actions_available: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['triggers'] = [t.to_dict() if isinstance(t, Trigger) else t for t in self.triggers]
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        if 'triggers' in data:
            data['triggers'] = [Trigger.from_dict(t) if isinstance(t, dict) else t for t in data['triggers']]
        if 'map_position' in data and isinstance(data['map_position'], list):
            data['map_position'] = tuple(data['map_position'])
        return cls(**data)

@dataclass
class Weapon:
    """Waffe mit allen Eigenschaften"""
    id: str
    name: str
    image_path: Optional[str] = None
    accuracy: float = 0.8  # Treffgenauigkeit 0-1
    damage_min: int = 1
    damage_max: int = 10
    damage_avg: int = 5
    damage_type: DamageType = DamageType.PHYSICAL
    # Völker-Boni
    race_bonuses: Dict[str, int] = field(default_factory=dict)
    # Voraussetzungen
    required_level: int = 1
    required_strength: int = 0
    required_skills: List[str] = field(default_factory=list)
    # Beschreibung
    description: str = ""
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['damage_type'] = self.damage_type.value
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Weapon':
        if 'damage_type' in data:
            data['damage_type'] = DamageType(data['damage_type'])
        return cls(**data)

@dataclass
class Armor:
    """Schutzgegenstand"""
    id: str
    name: str
    image_path: Optional[str] = None
    protection_min: int = 1
    protection_max: int = 10
    protection_avg: int = 5
    reliability: float = 0.9  # Zuverlässigkeit 0-1
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Armor':
        return cls(**data)

@dataclass
class CombatTechnique:
    """Kampftechnik/Attacke mit Stufen"""
    id: str
    name: str
    description: str = ""
    # Lernvoraussetzungen
    required_level: int = 1
    required_race: Optional[str] = None  # Volksspezifisch
    required_skills: List[str] = field(default_factory=list)
    # Stufen (Level 1-n mit jeweiligem Schaden)
    levels: Dict[int, Dict[str, Any]] = field(default_factory=dict)  # {1: {"damage": 10, "effect": "..."}}
    current_level: int = 1
    max_level: int = 5
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CombatTechnique':
        return cls(**data)

@dataclass
class Spell:
    """Zauber/Magie"""
    id: str
    name: str
    description: str = ""
    # Wirkung
    effect_type: SpellEffect = SpellEffect.DAMAGE
    effect_value: int = 10
    # Ziel
    target_type: SpellTarget = SpellTarget.SINGLE_ENEMY
    # Reichweite
    has_range_limit: bool = True
    range_meters: float = 10.0
    # Pluralität
    affects_multiple: bool = False
    max_targets: int = 1
    # Mana-Kosten
    mana_cost: int = 10
    # Voraussetzungen
    required_level: int = 1
    required_intelligence: int = 0
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['effect_type'] = self.effect_type.value
        d['target_type'] = self.target_type.value
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Spell':
        if 'effect_type' in data:
            data['effect_type'] = SpellEffect(data['effect_type'])
        if 'target_type' in data:
            data['target_type'] = SpellTarget(data['target_type'])
        return cls(**data)

@dataclass
class Character:
    """Charakter (Spieler oder NPC)"""
    id: str
    name: str
    race: str = ""
    profession: str = ""
    level: int = 1
    # Lebenskraft
    health: int = 100
    max_health: int = 100
    health_name: str = "Lebenskraft"  # Anpassbar
    mana: int = 50
    max_mana: int = 50
    # Attribute
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    constitution: int = 10
    wisdom: int = 10
    charisma: int = 10
    # Weitere Attribute (frei definierbar)
    custom_attributes: Dict[str, int] = field(default_factory=dict)
    # Skills
    skills: Dict[str, int] = field(default_factory=dict)
    # Ausrüstung
    equipped_weapon: Optional[str] = None
    equipped_armor: Optional[str] = None
    inventory: List[str] = field(default_factory=list)
    # Techniken und Zauber
    combat_techniques: List[str] = field(default_factory=list)
    known_spells: List[str] = field(default_factory=list)
    # Beschreibung
    biography: str = ""
    notes: str = ""
    image_path: Optional[str] = None
    # Spielzuordnung
    is_npc: bool = False
    player_name: Optional[str] = None
    group_id: Optional[str] = None
    # Bedürfnisse
    hunger: int = 0  # 0-100, 100 = verhungert
    thirst: int = 0  # 0-100, 100 = verdurstet
    hunger_rate: float = 1.0  # Pro Spielstunde
    thirst_rate: float = 1.5
    # Position
    current_location: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Character':
        return cls(**data)

@dataclass
class Mission:
    """Quest/Mission"""
    id: str
    name: str
    description: str
    objective: str
    status: MissionStatus = MissionStatus.ACTIVE
    # Zuordnung
    is_group_quest: bool = False
    assigned_to: List[str] = field(default_factory=list)  # Character IDs oder Group ID
    # Zeitbegrenzung
    has_time_limit: bool = False
    time_limit_hours: float = 0.0
    time_started: Optional[float] = None
    # Belohnungen
    rewards: List[str] = field(default_factory=list)
    reward_gold: int = 0
    reward_xp: int = 0
    # Notizen
    notes: str = ""
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['status'] = self.status.value
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Mission':
        if 'status' in data:
            data['status'] = MissionStatus(data['status'])
        return cls(**data)

@dataclass
class PlayerGroup:
    """Spielergruppe"""
    id: str
    name: str
    member_ids: List[str] = field(default_factory=list)  # Character IDs
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlayerGroup':
        return cls(**data)

@dataclass
class Vehicle:
    """Fahrzeug/Fortbewegungsmittel"""
    id: str
    name: str
    vehicle_class: str = ""  # z.B. "Kutsche", "Schiff"
    image_path: Optional[str] = None
    # Geschwindigkeit (km/h)
    speed_max: float = 50.0
    speed_min: float = 5.0  # z.B. bergauf
    speed_avg: float = 30.0
    # Antrieb
    propulsion_type: str = ""  # z.B. "Pferde", "Segel", "Dampf"
    fuel_type: str = ""  # z.B. "Nahrung+Wasser", "Kohle"
    fuel_consumption_per_km: float = 0.1
    # Verschleiß
    wear_level: float = 0.0  # 0-100
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Vehicle':
        return cls(**data)

@dataclass
class RoadType:
    """Wegeart"""
    id: str
    name: str
    material: str = ""
    width_meters: float = 5.0
    roll_resistance: float = 1.0  # 1.0 = normal, höher = langsamer
    annual_weathering: float = 0.01  # Verschlechterung pro Jahr
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RoadType':
        return cls(**data)

@dataclass
class Nation:
    """Nation/Land"""
    id: str
    name: str
    description: str = ""
    # Eigenschaften
    races: List[str] = field(default_factory=list)
    vegetation: str = ""
    climate: str = ""
    # Beziehungen
    friendly_nations: List[str] = field(default_factory=list)
    hostile_nations: List[str] = field(default_factory=list)
    # Untereinheiten
    counties: List[str] = field(default_factory=list)  # Grafschaften
    cities: List[str] = field(default_factory=list)
    villages: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Nation':
        return cls(**data)

@dataclass
class Race:
    """Volk/Rasse"""
    id: str
    name: str
    description: str = ""
    background_story: str = ""
    # Eigenschaften
    cultural_traits: str = ""
    abilities: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    # Bedürfnis-Modifikatoren
    hunger_modifier: float = 1.0
    thirst_modifier: float = 1.0
    special_needs: List[str] = field(default_factory=list)
    # Zeit bis Tod (in Spielstunden)
    starvation_hours: float = 72.0
    dehydration_hours: float = 48.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Race':
        return cls(**data)

@dataclass
class Item:
    """Gegenstand"""
    id: str
    name: str
    item_class: str = ""  # Oberklasse
    item_subclass: str = ""  # Unterklasse
    is_unique: bool = False  # Besonderes Item (nur einmal)
    description: str = ""
    # Auswirkungen
    health_bonus: int = 0
    strength_bonus: int = 0
    other_bonuses: Dict[str, int] = field(default_factory=dict)
    # Ort
    location_id: Optional[str] = None
    owner_id: Optional[str] = None  # Character ID wenn im Besitz
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        return cls(**data)

@dataclass
class DiceRule:
    """Würfelregel mit Zahlenbereichen"""
    id: str
    name: str
    dice_count: int = 1
    dice_sides: int = 20  # z.B. W20
    # Ergebnisbereiche
    ranges: Dict[str, Tuple[int, int]] = field(default_factory=dict)  # {"kritisch": (20, 20), "erfolg": (10, 19)}
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DiceRule':
        # Konvertiere ranges Listen zurück zu Tupeln
        if 'ranges' in data:
            data['ranges'] = {k: tuple(v) for k, v in data['ranges'].items()}
        return cls(**data)

@dataclass
class WorldSettings:
    """Welteinstellungen"""
    name: str = "Neue Welt"
    description: str = ""
    genre: str = "Fantasy"
    # Zeit
    day_hours: int = 24
    daylight_hours: int = 12
    time_ratio: float = 1.0  # 1 echte Stunde = X Spielstunden
    current_time: float = 12.0  # Aktuelle Uhrzeit (0-24)
    current_day: int = 1
    # Wahrscheinlichkeiten
    war_probability: float = 0.01
    disaster_probability: float = 0.005
    # Maßstab
    map_scale_km_per_cm: float = 10.0
    # Simulation
    simulate_time: bool = True
    simulate_wear: bool = True
    simulate_hunger: bool = True
    simulate_disasters: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorldSettings':
        return cls(**data)

@dataclass
class World:
    """Komplette Spielwelt"""
    id: str
    settings: WorldSettings = field(default_factory=WorldSettings)
    # Entitäten
    locations: Dict[str, Location] = field(default_factory=dict)
    nations: Dict[str, Nation] = field(default_factory=dict)
    races: Dict[str, Race] = field(default_factory=dict)
    professions: List[str] = field(default_factory=list)
    social_classes: List[str] = field(default_factory=list)
    road_types: Dict[str, RoadType] = field(default_factory=dict)
    # Kampf
    weapons: Dict[str, Weapon] = field(default_factory=dict)
    armors: Dict[str, Armor] = field(default_factory=dict)
    combat_techniques: Dict[str, CombatTechnique] = field(default_factory=dict)
    spells: Dict[str, Spell] = field(default_factory=dict)
    dice_rules: Dict[str, DiceRule] = field(default_factory=dict)
    # Items
    item_classes: List[str] = field(default_factory=list)
    typical_items: Dict[str, Item] = field(default_factory=dict)
    # Fahrzeuge
    vehicles: Dict[str, Vehicle] = field(default_factory=dict)
    # Karte
    map_image: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'settings': self.settings.to_dict(),
            'locations': {k: v.to_dict() for k, v in self.locations.items()},
            'nations': {k: v.to_dict() for k, v in self.nations.items()},
            'races': {k: v.to_dict() for k, v in self.races.items()},
            'professions': self.professions,
            'social_classes': self.social_classes,
            'road_types': {k: v.to_dict() for k, v in self.road_types.items()},
            'weapons': {k: v.to_dict() for k, v in self.weapons.items()},
            'armors': {k: v.to_dict() for k, v in self.armors.items()},
            'combat_techniques': {k: v.to_dict() for k, v in self.combat_techniques.items()},
            'spells': {k: v.to_dict() for k, v in self.spells.items()},
            'dice_rules': {k: v.to_dict() for k, v in self.dice_rules.items()},
            'item_classes': self.item_classes,
            'typical_items': {k: v.to_dict() for k, v in self.typical_items.items()},
            'vehicles': {k: v.to_dict() for k, v in self.vehicles.items()},
            'map_image': self.map_image
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'World':
        return cls(
            id=data['id'],
            settings=WorldSettings.from_dict(data.get('settings', {})),
            locations={k: Location.from_dict(v) for k, v in data.get('locations', {}).items()},
            nations={k: Nation.from_dict(v) for k, v in data.get('nations', {}).items()},
            races={k: Race.from_dict(v) for k, v in data.get('races', {}).items()},
            professions=data.get('professions', []),
            social_classes=data.get('social_classes', []),
            road_types={k: RoadType.from_dict(v) for k, v in data.get('road_types', {}).items()},
            weapons={k: Weapon.from_dict(v) for k, v in data.get('weapons', {}).items()},
            armors={k: Armor.from_dict(v) for k, v in data.get('armors', {}).items()},
            combat_techniques={k: CombatTechnique.from_dict(v) for k, v in data.get('combat_techniques', {}).items()},
            spells={k: Spell.from_dict(v) for k, v in data.get('spells', {}).items()},
            dice_rules={k: DiceRule.from_dict(v) for k, v in data.get('dice_rules', {}).items()},
            item_classes=data.get('item_classes', []),
            typical_items={k: Item.from_dict(v) for k, v in data.get('typical_items', {}).items()},
            vehicles={k: Vehicle.from_dict(v) for k, v in data.get('vehicles', {}).items()},
            map_image=data.get('map_image')
        )

@dataclass
class Session:
    """Spielsitzung"""
    id: str
    world_id: str
    name: str
    created: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    # Charaktere
    characters: Dict[str, Character] = field(default_factory=dict)
    groups: Dict[str, PlayerGroup] = field(default_factory=dict)
    # Missionen
    active_missions: Dict[str, Mission] = field(default_factory=dict)
    completed_missions: List[str] = field(default_factory=list)
    # Spielverlauf
    chat_history: List[ChatMessage] = field(default_factory=list)
    last_clipboard_index: int = 0
    # Spielmodus
    is_round_based: bool = False
    turn_order: List[str] = field(default_factory=list)  # Character IDs
    current_turn_index: int = 0
    actions_per_turn: int = 0  # 0 = unbegrenzt
    # Spielleiter
    gm_is_human: bool = True
    gm_player_name: str = ""
    # Aktueller Ort
    current_location_id: Optional[str] = None
    # Zeit
    current_weather: WeatherType = WeatherType.CLEAR
    current_time_of_day: TimeOfDay = TimeOfDay.NOON
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'world_id': self.world_id,
            'name': self.name,
            'created': self.created,
            'last_modified': self.last_modified,
            'characters': {k: v.to_dict() for k, v in self.characters.items()},
            'groups': {k: v.to_dict() for k, v in self.groups.items()},
            'active_missions': {k: v.to_dict() for k, v in self.active_missions.items()},
            'completed_missions': self.completed_missions,
            'chat_history': [m.to_dict() for m in self.chat_history],
            'last_clipboard_index': self.last_clipboard_index,
            'is_round_based': self.is_round_based,
            'turn_order': self.turn_order,
            'current_turn_index': self.current_turn_index,
            'actions_per_turn': self.actions_per_turn,
            'gm_is_human': self.gm_is_human,
            'gm_player_name': self.gm_player_name,
            'current_location_id': self.current_location_id,
            'current_weather': self.current_weather.value,
            'current_time_of_day': self.current_time_of_day.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        return cls(
            id=data['id'],
            world_id=data['world_id'],
            name=data['name'],
            created=data.get('created', time.time()),
            last_modified=data.get('last_modified', time.time()),
            characters={k: Character.from_dict(v) for k, v in data.get('characters', {}).items()},
            groups={k: PlayerGroup.from_dict(v) for k, v in data.get('groups', {}).items()},
            active_missions={k: Mission.from_dict(v) for k, v in data.get('active_missions', {}).items()},
            completed_missions=data.get('completed_missions', []),
            chat_history=[ChatMessage.from_dict(m) for m in data.get('chat_history', [])],
            last_clipboard_index=data.get('last_clipboard_index', 0),
            is_round_based=data.get('is_round_based', False),
            turn_order=data.get('turn_order', []),
            current_turn_index=data.get('current_turn_index', 0),
            actions_per_turn=data.get('actions_per_turn', 0),
            gm_is_human=data.get('gm_is_human', True),
            gm_player_name=data.get('gm_player_name', ''),
            current_location_id=data.get('current_location_id'),
            current_weather=WeatherType(data.get('current_weather', 'clear')),
            current_time_of_day=TimeOfDay(data.get('current_time_of_day', 'noon'))
        )

# ============================================================================
# MANAGER-KLASSEN
# ============================================================================

class DataManager:
    """Zentralisierte Datenverwaltung für alle Entitäten"""
    
    def __init__(self):
        self.worlds: Dict[str, World] = {}
        self.sessions: Dict[str, Session] = {}
        self.current_world: Optional[World] = None
        self.current_session: Optional[Session] = None
        self._load_all()
    
    def _load_all(self):
        """Lädt alle gespeicherten Daten"""
        self._load_worlds()
        self._load_sessions()
    
    def _load_worlds(self):
        """Lädt alle Welten"""
        for path in WORLDS_DIR.glob("*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    world = World.from_dict(data)
                    self.worlds[world.id] = world
                    logger.info(f"Welt geladen: {world.settings.name}")
            except Exception as e:
                logger.error(f"Fehler beim Laden von {path}: {e}")
    
    def _load_sessions(self):
        """Lädt alle Sessions"""
        for path in SESSIONS_DIR.glob("*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                    self.sessions[session.id] = session
                    logger.info(f"Session geladen: {session.name}")
            except Exception as e:
                logger.error(f"Fehler beim Laden von {path}: {e}")
    
    def save_world(self, world: World) -> bool:
        """Speichert eine Welt"""
        try:
            path = WORLDS_DIR / f"{world.id}.json"
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(world.to_dict(), f, ensure_ascii=False, indent=2)
            self.worlds[world.id] = world
            logger.info(f"Welt gespeichert: {world.settings.name}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Welt: {e}")
            return False
    
    def save_session(self, session: Session) -> bool:
        """Speichert eine Session"""
        try:
            session.last_modified = time.time()
            path = SESSIONS_DIR / f"{session.id}.json"
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            self.sessions[session.id] = session
            logger.info(f"Session gespeichert: {session.name}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Session: {e}")
            return False
    
    def create_world(self, name: str, genre: str = "Fantasy") -> World:
        """Erstellt eine neue Welt"""
        world_id = str(uuid.uuid4())[:8]
        settings = WorldSettings(name=name, genre=genre)
        world = World(id=world_id, settings=settings)
        self.save_world(world)
        return world
    
    def create_session(self, world_id: str, name: str) -> Optional[Session]:
        """Erstellt eine neue Session"""
        if world_id not in self.worlds:
            logger.error(f"Welt {world_id} nicht gefunden")
            return None
        session_id = str(uuid.uuid4())[:8]
        session = Session(id=session_id, world_id=world_id, name=name)
        self.save_session(session)
        return session
    
    def delete_world(self, world_id: str) -> bool:
        """Löscht eine Welt (mit Backup)"""
        if world_id not in self.worlds:
            return False
        try:
            path = WORLDS_DIR / f"{world_id}.json"
            backup_path = BACKUPS_DIR / f"world_{world_id}_{int(time.time())}.json"
            if path.exists():
                path.rename(backup_path)
            del self.worlds[world_id]
            return True
        except Exception as e:
            logger.error(f"Fehler beim Löschen: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Löscht eine Session (mit Backup)"""
        if session_id not in self.sessions:
            return False
        try:
            path = SESSIONS_DIR / f"{session_id}.json"
            backup_path = BACKUPS_DIR / f"session_{session_id}_{int(time.time())}.json"
            if path.exists():
                path.rename(backup_path)
            del self.sessions[session_id]
            return True
        except Exception as e:
            logger.error(f"Fehler beim Löschen: {e}")
            return False


class PromptGenerator:
    """Generiert KI-Prompts für verschiedene Rollen"""
    
    # Vordefinierte KI-Auftrags-Templates
    ROLE_TEMPLATES = {
        "storyteller": "Entwickle die Geschichte weiter. Was passiert als nächstes? Beschreibe die Szene atmosphärisch.",
        "plottwist": "Baue eine überraschende Wendung in die Geschichte ein. Etwas Unerwartetes soll geschehen!",
        "gamemaster": "Steuere unser Spiel. Was sind unsere Optionen? Welche Entscheidungen müssen wir treffen?",
        "enemy": "Erschaffe einen passenden Gegner für unsere Gruppe. Beschreibe Aussehen, Fähigkeiten und Motivation.",
        "npc": "Denke dir interessante NPCs aus und baue sie in die Szene ein. Gib ihnen Persönlichkeit und Ziele.",
        "landscape": "Beschreibe die Landschaft und Umgebung detailliert. Was können wir sehen, hören, riechen?",
        "fauna_flora": "Beschreibe Pflanzen und Tiere in unserer aktuellen Umgebung. Erfinde passende Namen für diese Welt.",
    }
    
    @staticmethod
    def generate_game_start_prompt(session: Session, world: World) -> str:
        """Generiert den Spielstart-Prompt mit allen relevanten Infos"""
        lines = [
            "=== SPIELSTART ===",
            f"Wir sind eine Gruppe aus {len(session.characters)} Spielern.",
            f"Wir spielen ein Pen & Paper Rollenspiel im Genre: {world.settings.genre}",
            f"Die Welt heißt: {world.settings.name}",
            ""
        ]
        
        # Weltbeschreibung
        if world.settings.description:
            lines.append(f"Weltbeschreibung: {world.settings.description}")
            lines.append("")
        
        # Charaktere
        lines.append("=== UNSERE CHARAKTERE ===")
        for char in session.characters.values():
            if not char.is_npc:
                char_info = f"- {char.name}"
                if char.race:
                    char_info += f" ({char.race})"
                if char.profession:
                    char_info += f", {char.profession}"
                char_info += f", Level {char.level}"
                if char.player_name:
                    char_info += f" [Spieler: {char.player_name}]"
                lines.append(char_info)
        lines.append("")
        
        # Aktive Missionen
        active = [m for m in session.active_missions.values() if m.status == MissionStatus.ACTIVE]
        if active:
            lines.append("=== AKTIVE MISSIONEN ===")
            for mission in active:
                lines.append(f"- {mission.name}: {mission.objective}")
            lines.append("")
        
        # Aktueller Ort
        if session.current_location_id and session.current_location_id in world.locations:
            loc = world.locations[session.current_location_id]
            lines.append(f"=== AKTUELLER ORT ===")
            lines.append(f"Ort: {loc.name}")
            if loc.description:
                lines.append(f"Beschreibung: {loc.description}")
            lines.append("")
        
        # Spielmodus
        lines.append("=== SPIELMODUS ===")
        if session.is_round_based:
            lines.append(f"Rundenbasiert: Ja")
            if session.actions_per_turn > 0:
                lines.append(f"Aktionen pro Runde: {session.actions_per_turn}")
        else:
            lines.append("Spielmodus: Frei")
        
        if session.gm_is_human:
            lines.append(f"Spielleiter: {session.gm_player_name} (Mensch)")
        else:
            lines.append("Spielleiter: KI")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_context_update_prompt(session: Session, max_messages: int = 20) -> str:
        """Generiert ein Kontext-Update aus dem Spielverlauf"""
        lines = ["=== SPIELVERLAUF UPDATE ==="]
        
        # Letzte Nachrichten seit letztem Clipboard-Cut
        recent = session.chat_history[session.last_clipboard_index:]
        if len(recent) > max_messages:
            recent = recent[-max_messages:]
        
        for msg in recent:
            timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M")
            role_name = msg.role.value.upper()
            lines.append(f"[{timestamp}] [{role_name}] {msg.author}: {msg.content}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_action_prompt(character: Character, action: str, location: Optional[Location] = None) -> str:
        """Generiert einen Aktions-Prompt"""
        lines = [f"=== AKTION VON {character.name.upper()} ==="]
        lines.append(f"Charakter: {character.name} ({character.race}, {character.profession})")
        lines.append(f"Level: {character.level}, Leben: {character.health}/{character.max_health}")
        
        if location:
            lines.append(f"Ort: {location.name}")
        
        lines.append(f"Aktion: {action}")
        
        return "\n".join(lines)
    
    @classmethod
    def generate_role_prompt(cls, role: str, session: Session, world: World) -> str:
        """Generiert einen Rollen-spezifischen Prompt"""
        template = cls.ROLE_TEMPLATES.get(role, "")
        if not template:
            return ""
        
        lines = [
            f"=== KI-AUFTRAG: {role.upper()} ===",
            "",
            f"Welt: {world.settings.name} ({world.settings.genre})",
        ]
        
        # Aktueller Ort
        if session.current_location_id and session.current_location_id in world.locations:
            loc = world.locations[session.current_location_id]
            lines.append(f"Ort: {loc.name}")
        
        lines.append("")
        lines.append(f"Auftrag: {template}")
        
        return "\n".join(lines)


class AudioManager:
    """Verwaltet Audio-Wiedergabe (Musik, Sounds, Effekte)"""
    
    def __init__(self):
        self.music_player: Optional[QMediaPlayer] = None
        self.sound_players: Dict[str, QMediaPlayer] = {}
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.ambient_volume = 0.4
        self._init_audio()
    
    def _init_audio(self):
        """Initialisiert Audio-System"""
        if not HAS_AUDIO:
            logger.warning("Audio nicht verfügbar")
            return
        
        try:
            self.music_player = QMediaPlayer()
            self.music_output = QAudioOutput()
            self.music_player.setAudioOutput(self.music_output)
            self.music_output.setVolume(self.music_volume)
            logger.info("Audio-System initialisiert")
        except Exception as e:
            logger.error(f"Audio-Initialisierung fehlgeschlagen: {e}")
    
    def play_music(self, file_path: str, loop: bool = True):
        """Spielt Hintergrundmusik"""
        if not HAS_AUDIO or not self.music_player:
            return
        
        try:
            path = Path(file_path)
            if not path.exists():
                path = MUSIC_DIR / file_path
            
            if path.exists():
                self.music_player.setSource(QUrl.fromLocalFile(str(path)))
                if loop:
                    self.music_player.setLoops(QMediaPlayer.Infinite)
                self.music_player.play()
                logger.info(f"Musik gestartet: {path.name}")
        except Exception as e:
            logger.error(f"Musik-Fehler: {e}")
    
    def stop_music(self):
        """Stoppt Hintergrundmusik"""
        if self.music_player:
            self.music_player.stop()
    
    def play_sound(self, file_path: str, volume: float = None):
        """Spielt einen Sound-Effekt"""
        if not HAS_AUDIO:
            return
        
        try:
            path = Path(file_path)
            if not path.exists():
                path = SOUNDS_DIR / file_path
            
            if path.exists():
                player = QMediaPlayer()
                output = QAudioOutput()
                player.setAudioOutput(output)
                output.setVolume(volume or self.sound_volume)
                player.setSource(QUrl.fromLocalFile(str(path)))
                player.play()
                
                # Aufräumen nach Abspielen
                sound_id = str(uuid.uuid4())[:8]
                self.sound_players[sound_id] = player
                logger.info(f"Sound gespielt: {path.name}")
        except Exception as e:
            logger.error(f"Sound-Fehler: {e}")
    
    def set_music_volume(self, volume: float):
        """Setzt Musik-Lautstärke (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_output:
            self.music_output.setVolume(self.music_volume)
    
    def set_sound_volume(self, volume: float):
        """Setzt Sound-Lautstärke"""
        self.sound_volume = max(0.0, min(1.0, volume))


class LightEffectManager(QObject):
    """Verwaltet Lichteffekte (Blitze, Tag/Nacht, Farbfilter)"""
    
    effect_started = Signal(str)
    effect_finished = Signal(str)
    
    def __init__(self, target_widget: QWidget = None):
        super().__init__()
        self.target = target_widget
        self.overlay: Optional[QWidget] = None
        self.effect_timer: Optional[QTimer] = None
        self.current_effect = ""
    
    def set_target(self, widget: QWidget):
        """Setzt das Ziel-Widget für Effekte"""
        self.target = widget
        self._create_overlay()
    
    def _create_overlay(self):
        """Erstellt das Overlay-Widget"""
        if not self.target:
            return
        
        self.overlay = QWidget(self.target)
        self.overlay.setStyleSheet("background-color: transparent;")
        self.overlay.setGeometry(self.target.rect())
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.overlay.hide()
    
    def flash_lightning(self, duration_ms: int = 200):
        """Blitz-Effekt"""
        if not self.overlay:
            return
        
        self.current_effect = "lightning"
        self.effect_started.emit("lightning")
        
        # Sequenz: Schwarz -> Weiß -> Schwarz -> Fade
        sequence = [
            ("rgba(0, 0, 0, 0.8)", 50),
            ("rgba(255, 255, 255, 0.9)", 50),
            ("rgba(0, 0, 0, 0.6)", 50),
            ("transparent", duration_ms - 150)
        ]
        
        self._run_sequence(sequence)
    
    def flash_strobe(self, flashes: int = 5, interval_ms: int = 100):
        """Stroboskop-Effekt"""
        if not self.overlay:
            return
        
        self.current_effect = "strobe"
        self.effect_started.emit("strobe")
        
        sequence = []
        for _ in range(flashes):
            sequence.append(("rgba(255, 255, 255, 0.9)", interval_ms // 2))
            sequence.append(("transparent", interval_ms // 2))
        
        self._run_sequence(sequence)
    
    def set_day_night(self, is_night: bool, opacity: float = 0.5):
        """Tag/Nacht-Effekt"""
        if not self.overlay:
            return
        
        if is_night:
            self.overlay.setStyleSheet(f"background-color: rgba(0, 0, 30, {opacity});")
        else:
            self.overlay.setStyleSheet(f"background-color: rgba(255, 255, 200, {opacity * 0.3});")
        self.overlay.show()
    
    def set_color_filter(self, color: str, opacity: float = 0.3):
        """Setzt Farbfilter"""
        if not self.overlay:
            return
        
        # Konvertiere Farbname zu RGBA
        qcolor = QColor(color)
        self.overlay.setStyleSheet(
            f"background-color: rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {opacity});"
        )
        self.overlay.show()
    
    def clear_filter(self):
        """Entfernt alle Filter"""
        if self.overlay:
            self.overlay.setStyleSheet("background-color: transparent;")
            self.overlay.hide()
    
    def _run_sequence(self, sequence: List[Tuple[str, int]]):
        """Führt eine Effekt-Sequenz aus"""
        if not self.overlay or not sequence:
            return
        
        self.overlay.show()
        
        def apply_step(index):
            if index >= len(sequence):
                self.overlay.hide()
                self.effect_finished.emit(self.current_effect)
                return
            
            color, duration = sequence[index]
            self.overlay.setStyleSheet(f"background-color: {color};")
            QTimer.singleShot(duration, lambda: apply_step(index + 1))
        
        apply_step(0)


class DiceRoller:
    """Würfelsystem mit konfigurierbaren Regeln"""
    
    def __init__(self):
        self.rules: Dict[str, DiceRule] = {}
        self.history: List[Dict[str, Any]] = []
    
    def add_rule(self, rule: DiceRule):
        """Fügt eine Würfelregel hinzu"""
        self.rules[rule.id] = rule
    
    def roll(self, rule_id: str = None, dice_count: int = 1, dice_sides: int = 20) -> Dict[str, Any]:
        """Würfelt nach Regel oder frei"""
        
        # Würfeln
        rolls = [random.randint(1, dice_sides) for _ in range(dice_count)]
        total = sum(rolls)
        
        result = {
            "rolls": rolls,
            "total": total,
            "dice": f"{dice_count}W{dice_sides}",
            "timestamp": time.time(),
            "outcome": None
        }
        
        # Regel anwenden
        if rule_id and rule_id in self.rules:
            rule = self.rules[rule_id]
            for outcome_name, (min_val, max_val) in rule.ranges.items():
                if min_val <= total <= max_val:
                    result["outcome"] = outcome_name
                    break
        
        self.history.append(result)
        return result
    
    def get_last_rolls(self, count: int = 10) -> List[Dict[str, Any]]:
        """Gibt die letzten Würfe zurück"""
        return self.history[-count:]

# ============================================================================
# GUI-KOMPONENTEN
# ============================================================================

class ChatWidget(QWidget):
    """Chat-Widget mit Farbcodierung nach Rolle"""
    
    message_sent = Signal(ChatMessage)
    
    ROLE_COLORS = {
        MessageRole.PLAYER: "#3498db",        # Blau
        MessageRole.GM: "#e74c3c",            # Rot
        MessageRole.AI_STORYTELLER: "#9b59b6", # Lila
        MessageRole.AI_WORLD_DESIGNER: "#27ae60", # Grün
        MessageRole.AI_NPC: "#e67e22",        # Orange
        MessageRole.AI_PLOTTWIST: "#f39c12",  # Gold
        MessageRole.AI_ENEMY: "#c0392b",      # Dunkelrot
        MessageRole.AI_LANDSCAPE: "#16a085",  # Türkis
        MessageRole.AI_FAUNA_FLORA: "#2ecc71", # Hellgrün
        MessageRole.SYSTEM: "#7f8c8d",        # Grau
        MessageRole.NARRATOR: "#1abc9c",      # Cyan
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Chat-Anzeige
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                background-color: #1a1a2e;
                color: #eee;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.chat_display, stretch=1)
        
        # Eingabebereich
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #16213e; border-radius: 5px; padding: 5px;")
        input_layout = QVBoxLayout(input_frame)
        
        # Rolle und Autor
        role_layout = QHBoxLayout()
        
        role_layout.addWidget(QLabel("Rolle:"))
        self.role_combo = QComboBox()
        for role in MessageRole:
            self.role_combo.addItem(role.value.replace("_", " ").title(), role)
        self.role_combo.setCurrentIndex(0)
        role_layout.addWidget(self.role_combo)
        
        role_layout.addWidget(QLabel("Name:"))
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Dein Name...")
        role_layout.addWidget(self.author_input)
        
        input_layout.addLayout(role_layout)
        
        # Nachrichteneingabe
        msg_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(80)
        self.message_input.setPlaceholderText("Nachricht eingeben...")
        msg_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("📤 Senden")
        self.send_button.setMinimumHeight(60)
        self.send_button.clicked.connect(self.send_message)
        msg_layout.addWidget(self.send_button)
        
        input_layout.addLayout(msg_layout)
        layout.addWidget(input_frame)
    
    def add_message(self, message: ChatMessage):
        """Fügt eine Nachricht zum Chat hinzu"""
        color = self.ROLE_COLORS.get(message.role, "#aaa")
        timestamp = datetime.fromtimestamp(message.timestamp).strftime("%H:%M")
        role_name = message.role.value.replace("_", " ").title()
        
        html = f'''
        <div style="margin-bottom: 10px; padding: 8px; background-color: rgba(255,255,255,0.05); border-radius: 5px; border-left: 3px solid {color};">
            <span style="color: {color}; font-weight: bold;">[{role_name}]</span>
            <span style="color: #888; font-size: 11px;">{timestamp}</span>
            <span style="color: {color}; font-weight: bold;"> {message.author}:</span>
            <div style="color: #eee; margin-top: 5px; padding-left: 10px;">{message.content}</div>
        </div>
        '''
        
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(html)
        self.chat_display.ensureCursorVisible()
    
    def send_message(self):
        """Sendet die aktuelle Nachricht"""
        content = self.message_input.toPlainText().strip()
        if not content:
            return
        
        role = self.role_combo.currentData()
        author = self.author_input.text().strip() or "Anonym"
        
        message = ChatMessage(role=role, author=author, content=content)
        self.add_message(message)
        self.message_sent.emit(message)
        
        self.message_input.clear()
    
    def load_history(self, messages: List[ChatMessage]):
        """Lädt Chat-Verlauf"""
        self.chat_display.clear()
        for msg in messages:
            self.add_message(msg)


class SoundboardWidget(QWidget):
    """Soundboard für Effekte"""
    
    def __init__(self, audio_manager: AudioManager, parent=None):
        super().__init__(parent)
        self.audio = audio_manager
        self.sound_buttons: Dict[str, QPushButton] = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titel
        title = QLabel("🔊 Soundboard")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        layout.addWidget(title)
        
        # Lautstärke
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Lautstärke:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self._on_volume_change)
        vol_layout.addWidget(self.volume_slider)
        layout.addLayout(vol_layout)
        
        # Sound-Buttons Grid
        self.button_grid = QGridLayout()
        layout.addLayout(self.button_grid)
        
        # Buttons zum Hinzufügen/Entfernen
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Sound hinzufügen")
        add_btn.clicked.connect(self.add_sound)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("➖ Sound entfernen")
        remove_btn.clicked.connect(self.remove_sound)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        # Standard-Sounds laden
        self._load_default_sounds()
    
    def _load_default_sounds(self):
        """Lädt Standard-Sounds aus dem Verzeichnis"""
        for path in SOUNDS_DIR.glob("*.*"):
            if path.suffix.lower() in ['.mp3', '.wav', '.ogg']:
                self.add_sound_button(path.stem, str(path))
    
    def add_sound_button(self, name: str, file_path: str):
        """Fügt einen Sound-Button hinzu"""
        btn = QPushButton(f"🔔 {name}")
        btn.setMinimumHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)
        btn.clicked.connect(lambda: self.audio.play_sound(file_path))
        
        # Position berechnen
        count = len(self.sound_buttons)
        row = count // 3
        col = count % 3
        
        self.button_grid.addWidget(btn, row, col)
        self.sound_buttons[name] = btn
    
    def add_sound(self):
        """Dialog zum Hinzufügen eines Sounds"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sound auswählen", str(SOUNDS_DIR),
            "Audio-Dateien (*.mp3 *.wav *.ogg)"
        )
        if file_path:
            name, ok = QInputDialog.getText(self, "Sound benennen", "Name:")
            if ok and name:
                self.add_sound_button(name, file_path)
    
    def remove_sound(self):
        """Dialog zum Entfernen eines Sounds"""
        if not self.sound_buttons:
            return
        name, ok = QInputDialog.getItem(
            self, "Sound entfernen", "Auswählen:",
            list(self.sound_buttons.keys()), 0, False
        )
        if ok and name in self.sound_buttons:
            btn = self.sound_buttons.pop(name)
            btn.deleteLater()
    
    def _on_volume_change(self, value):
        self.audio.set_sound_volume(value / 100)


class CharacterWidget(QWidget):
    """Charakteranzeige mit Avatar und Status"""
    
    def __init__(self, character: Character = None, parent=None):
        super().__init__(parent)
        self.character = character
        self.setup_ui()
        if character:
            self.update_display(character)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.setMinimumWidth(200)
        self.setMaximumWidth(250)
        
        # Avatar
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(150, 150)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                border-radius: 75px;
                border: 3px solid #3498db;
            }
        """)
        layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)
        
        # Name (fett)
        self.name_label = QLabel("Charaktername")
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff;")
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)
        
        # Spielername
        self.player_label = QLabel("Spieler: -")
        self.player_label.setStyleSheet("font-size: 12px; color: #888;")
        self.player_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.player_label)
        
        # Rasse & Beruf
        self.info_label = QLabel("Rasse | Beruf")
        self.info_label.setStyleSheet("font-size: 12px; color: #aaa;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Statusbalken
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        
        # Leben
        hp_layout = QHBoxLayout()
        hp_layout.addWidget(QLabel("❤️"))
        self.health_bar = QProgressBar()
        self.health_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333;
                border-radius: 5px;
                text-align: center;
                background-color: #1a1a2e;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
                border-radius: 4px;
            }
        """)
        hp_layout.addWidget(self.health_bar)
        status_layout.addLayout(hp_layout)
        
        # Mana
        mp_layout = QHBoxLayout()
        mp_layout.addWidget(QLabel("💧"))
        self.mana_bar = QProgressBar()
        self.mana_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333;
                border-radius: 5px;
                text-align: center;
                background-color: #1a1a2e;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        mp_layout.addWidget(self.mana_bar)
        status_layout.addLayout(mp_layout)
        
        layout.addWidget(status_frame)
        
        # Inventar-Button
        self.inventory_btn = QPushButton("🎒 Inventar")
        self.inventory_btn.clicked.connect(self.open_inventory)
        layout.addWidget(self.inventory_btn)
        
        layout.addStretch()
    
    def update_display(self, character: Character):
        """Aktualisiert die Anzeige"""
        self.character = character
        
        self.name_label.setText(character.name)
        self.player_label.setText(f"Spieler: {character.player_name or '-'}")
        self.info_label.setText(f"{character.race} | {character.profession}")
        
        self.health_bar.setMaximum(character.max_health)
        self.health_bar.setValue(character.health)
        self.health_bar.setFormat(f"{character.health}/{character.max_health}")
        
        self.mana_bar.setMaximum(character.max_mana)
        self.mana_bar.setValue(character.mana)
        self.mana_bar.setFormat(f"{character.mana}/{character.max_mana}")
        
        # Avatar laden
        if character.image_path and Path(character.image_path).exists():
            pixmap = QPixmap(character.image_path)
            pixmap = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.avatar_label.setPixmap(pixmap)
        else:
            self.avatar_label.setText("👤")
            self.avatar_label.setStyleSheet(self.avatar_label.styleSheet() + "font-size: 60px;")
    
    def open_inventory(self):
        """Öffnet Inventar-Dialog"""
        if not self.character:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Inventar - {self.character.name}")
        dialog.setMinimumSize(300, 400)
        
        layout = QVBoxLayout(dialog)
        
        inv_list = QListWidget()
        for item in self.character.inventory:
            inv_list.addItem(item)
        layout.addWidget(inv_list)
        
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()


class LocationViewWidget(QWidget):
    """Ortsansicht mit Außen-/Innenansicht"""
    
    location_entered = Signal(str)
    location_exited = Signal(str)
    
    def __init__(self, light_manager: LightEffectManager = None, parent=None):
        super().__init__(parent)
        self.light_manager = light_manager
        self.current_location: Optional[Location] = None
        self.is_inside = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Bildanzeige
        self.image_label = QLabel()
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a2e;
                border: 2px solid #333;
                border-radius: 10px;
            }
        """)
        self.image_label.setText("🏞️\nKein Ort ausgewählt")
        layout.addWidget(self.image_label, stretch=1)
        
        # Lichteffekt-Overlay
        if self.light_manager:
            self.light_manager.set_target(self.image_label)
        
        # Ortsname
        self.location_name = QLabel("Ort: -")
        self.location_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        layout.addWidget(self.location_name)
        
        # Beschreibung
        self.description_text = QTextBrowser()
        self.description_text.setMaximumHeight(100)
        self.description_text.setStyleSheet("""
            QTextBrowser {
                background-color: #16213e;
                color: #ccc;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.description_text)
        
        # Aktionen
        action_layout = QHBoxLayout()
        
        self.enter_btn = QPushButton("🚪 Betreten")
        self.enter_btn.clicked.connect(self.enter_location)
        action_layout.addWidget(self.enter_btn)
        
        self.exit_btn = QPushButton("🚶 Verlassen")
        self.exit_btn.clicked.connect(self.exit_location)
        self.exit_btn.setEnabled(False)
        action_layout.addWidget(self.exit_btn)
        
        self.info_btn = QPushButton("ℹ️ Info/Preisliste")
        self.info_btn.clicked.connect(self.show_info)
        action_layout.addWidget(self.info_btn)
        
        layout.addLayout(action_layout)
    
    def show_location(self, location: Location, world: World = None):
        """Zeigt einen Ort an"""
        self.current_location = location
        self.is_inside = False
        
        self.location_name.setText(f"📍 {location.name}")
        self.description_text.setHtml(location.description)
        
        # Außenansicht laden
        if location.exterior_image and Path(location.exterior_image).exists():
            pixmap = QPixmap(location.exterior_image)
            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("🏞️\nKein Bild verfügbar")
        
        # Farbfilter anwenden
        if location.color_filter and self.light_manager:
            self.light_manager.set_color_filter(location.color_filter, location.color_filter_opacity)
        
        self.enter_btn.setEnabled(location.has_interior)
        self.exit_btn.setEnabled(False)
    
    def enter_location(self):
        """Betritt den Ort (Innenansicht)"""
        if not self.current_location or not self.current_location.has_interior:
            return
        
        # Blackout-Effekt
        if self.light_manager:
            self.light_manager.set_color_filter("black", 0.9)
            QTimer.singleShot(500, self._show_interior)
        else:
            self._show_interior()
    
    def _show_interior(self):
        """Zeigt Innenansicht"""
        if self.light_manager:
            self.light_manager.clear_filter()
        
        loc = self.current_location
        if loc.interior_image and Path(loc.interior_image).exists():
            pixmap = QPixmap(loc.interior_image)
            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        
        self.is_inside = True
        self.enter_btn.setEnabled(False)
        self.exit_btn.setEnabled(True)
        
        self.location_entered.emit(loc.id)
    
    def exit_location(self):
        """Verlässt den Ort"""
        if not self.current_location:
            return
        
        self.location_exited.emit(self.current_location.id)
        
        # Zurück zur Außenansicht
        if self.current_location.exterior_image:
            pixmap = QPixmap(self.current_location.exterior_image)
            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        
        self.is_inside = False
        self.enter_btn.setEnabled(self.current_location.has_interior)
        self.exit_btn.setEnabled(False)
    
    def show_info(self):
        """Zeigt Zusatzinfos/Preisliste"""
        if not self.current_location:
            return
        
        loc = self.current_location
        if loc.price_list_file and Path(loc.price_list_file).exists():
            # Datei mit Standardprogramm öffnen
            import subprocess
            subprocess.Popen(['start', '', loc.price_list_file], shell=True)
        else:
            QMessageBox.information(self, "Info", f"Verfügbare Aktionen: {', '.join(loc.actions_available) or 'Keine'}")


class PromptGeneratorWidget(QWidget):
    """Widget für KI-Prompt-Generierung"""
    
    prompt_generated = Signal(str)
    
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titel
        title = QLabel("🤖 KI-Promptgenerator")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #9b59b6;")
        layout.addWidget(title)
        
        # Auswahl
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
        
        # KI-Auftrags-Buttons
        ki_group = QGroupBox("KI-Aufträge")
        ki_layout = QGridLayout(ki_group)
        
        ki_buttons = [
            ("📖 Storyteller", "storyteller"),
            ("🔀 Plottwist", "plottwist"),
            ("🎮 Spielleiter", "gamemaster"),
            ("⚔️ Gegner", "enemy"),
            ("👥 NPCs", "npc"),
            ("🏔️ Landschaft", "landscape"),
            ("🌿 Fauna/Flora", "fauna_flora"),
        ]
        
        for i, (text, role) in enumerate(ki_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, r=role: self.generate_role_prompt(r))
            ki_layout.addWidget(btn, i // 4, i % 4)
        
        layout.addWidget(ki_group)
        
        # Prompt-Vorschau
        layout.addWidget(QLabel("Generierter Prompt:"))
        self.prompt_preview = QTextEdit()
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setMinimumHeight(150)
        layout.addWidget(self.prompt_preview)
        
        # Aktions-Buttons
        btn_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("⚡ Generieren")
        self.generate_btn.clicked.connect(self.generate_prompt)
        btn_layout.addWidget(self.generate_btn)
        
        self.copy_btn = QPushButton("📋 In Zwischenablage")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.copy_btn)
        
        self.start_btn = QPushButton("🚀 Spielstart-Prompt")
        self.start_btn.clicked.connect(self.generate_start_prompt)
        btn_layout.addWidget(self.start_btn)
        
        self.update_btn = QPushButton("🔄 Update-Prompt")
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
        
        # Clipboard-Index aktualisieren
        session.last_clipboard_index = len(session.chat_history)
        self.data_manager.save_session(session)
        
        self.prompt_generated.emit(prompt)
    
    def copy_to_clipboard(self):
        """Kopiert Prompt in Zwischenablage"""
        text = self.prompt_preview.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Kopiert", "Prompt wurde in die Zwischenablage kopiert!")

# ============================================================================
# HAUPTFENSTER
# ============================================================================

class RPXLightMainWindow(QMainWindow):
    """Hauptfenster des RPX Light Control Centers"""
    
    def __init__(self):
        super().__init__()
        
        # Manager initialisieren
        self.data_manager = DataManager()
        self.audio_manager = AudioManager()
        self.dice_roller = DiceRoller()
        self.light_manager = LightEffectManager()
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.apply_dark_theme()
        
        logger.info(f"{APP_TITLE} v{VERSION} gestartet")
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        self.setWindowTitle(f"🎭 {APP_TITLE} v{VERSION} - Light Edition")
        self.setMinimumSize(1400, 900)
        
        # Zentrales Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # Linke Seite: Charaktere
        self.character_panel = QWidget()
        char_layout = QVBoxLayout(self.character_panel)
        char_layout.addWidget(QLabel("👥 Aktive Charaktere"))
        self.character_list = QVBoxLayout()
        char_layout.addLayout(self.character_list)
        char_layout.addStretch()
        self.character_panel.setMaximumWidth(270)
        main_layout.addWidget(self.character_panel)
        
        # Mitte: Tab-System
        self.tabs = QTabWidget()
        
        # Tab 1: Chat
        self.chat_widget = ChatWidget()
        self.chat_widget.message_sent.connect(self.on_message_sent)
        self.tabs.addTab(self.chat_widget, "💬 Chat")
        
        # Tab 2: Ortsansicht
        self.location_view = LocationViewWidget(self.light_manager)
        self.location_view.location_entered.connect(self.on_location_entered)
        self.location_view.location_exited.connect(self.on_location_exited)
        self.tabs.addTab(self.location_view, "🗺️ Ortsansicht")
        
        # Tab 3: Weltverwaltung
        self.world_tab = self.create_world_tab()
        self.tabs.addTab(self.world_tab, "🌍 Welt")
        
        # Tab 4: Charaktere
        self.characters_tab = self.create_characters_tab()
        self.tabs.addTab(self.characters_tab, "👤 Charaktere")
        
        # Tab 5: Kampfsystem
        self.combat_tab = self.create_combat_tab()
        self.tabs.addTab(self.combat_tab, "⚔️ Kampf")
        
        # Tab 6: Missionen
        self.missions_tab = self.create_missions_tab()
        self.tabs.addTab(self.missions_tab, "📜 Missionen")
        
        # Tab 7: Immersion
        self.immersion_tab = self.create_immersion_tab()
        self.tabs.addTab(self.immersion_tab, "✨ Immersion")
        
        # Tab 8: Promptgenerator
        self.prompt_widget = PromptGeneratorWidget(self.data_manager)
        self.tabs.addTab(self.prompt_widget, "🤖 KI-Prompts")
        
        # Tab 9: Einstellungen
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "⚙️ Einstellungen")
        
        main_layout.addWidget(self.tabs, stretch=1)
        
        # Rechte Seite: Rundensteuerung
        self.turn_panel = self.create_turn_panel()
        main_layout.addWidget(self.turn_panel)
        
        # Statusbar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("RPX Light bereit | Upgrade auf Pro für alle Features")
    
    def create_world_tab(self) -> QWidget:
        """Erstellt den Welt-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Welt-Auswahl
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Aktive Welt:"))
        self.world_combo = QComboBox()
        self.world_combo.currentIndexChanged.connect(self.on_world_changed)
        select_layout.addWidget(self.world_combo, stretch=1)
        
        new_world_btn = QPushButton("➕ Neue Welt")
        new_world_btn.clicked.connect(self.create_new_world)
        select_layout.addWidget(new_world_btn)
        layout.addLayout(select_layout)
        
        # Welt-Info
        info_group = QGroupBox("Weltinformationen")
        info_layout = QFormLayout(info_group)
        
        self.world_name_edit = QLineEdit()
        info_layout.addRow("Name:", self.world_name_edit)
        
        self.world_genre_edit = QLineEdit()
        info_layout.addRow("Genre:", self.world_genre_edit)
        
        self.world_desc_edit = QTextEdit()
        self.world_desc_edit.setMaximumHeight(100)
        info_layout.addRow("Beschreibung:", self.world_desc_edit)
        
        layout.addWidget(info_group)
        
        # Orte
        locations_group = QGroupBox("Orte")
        loc_layout = QVBoxLayout(locations_group)
        
        self.locations_tree = QTreeWidget()
        self.locations_tree.setHeaderLabels(["Name", "Innenansicht", "Trigger"])
        loc_layout.addWidget(self.locations_tree)
        
        loc_btn_layout = QHBoxLayout()
        add_loc_btn = QPushButton("➕ Ort hinzufügen")
        add_loc_btn.clicked.connect(self.add_location)
        loc_btn_layout.addWidget(add_loc_btn)
        
        edit_loc_btn = QPushButton("✏️ Bearbeiten")
        loc_btn_layout.addWidget(edit_loc_btn)
        loc_layout.addLayout(loc_btn_layout)
        
        layout.addWidget(locations_group)
        
        # Speichern
        save_btn = QPushButton("💾 Welt speichern")
        save_btn.clicked.connect(self.save_world)
        layout.addWidget(save_btn)
        
        # Welten laden
        self.refresh_world_list()
        
        return widget
    
    def create_characters_tab(self) -> QWidget:
        """Erstellt den Charaktere-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Charakterliste
        self.char_table = QTableWidget()
        self.char_table.setColumnCount(7)
        self.char_table.setHorizontalHeaderLabels([
            "Name", "Spieler", "Rasse", "Beruf", "Level", "Leben", "NPC"
        ])
        self.char_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.char_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_char_btn = QPushButton("➕ Charakter erstellen")
        add_char_btn.clicked.connect(self.create_character)
        btn_layout.addWidget(add_char_btn)
        
        edit_char_btn = QPushButton("✏️ Bearbeiten")
        btn_layout.addWidget(edit_char_btn)
        
        delete_char_btn = QPushButton("🗑️ Löschen")
        btn_layout.addWidget(delete_char_btn)
        
        add_to_session_btn = QPushButton("📥 Zu Session hinzufügen")
        btn_layout.addWidget(add_to_session_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def create_combat_tab(self) -> QWidget:
        """Erstellt den Kampf-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Würfelsystem
        dice_group = QGroupBox("🎲 Würfelsystem")
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
        
        roll_btn = QPushButton("🎲 Würfeln!")
        roll_btn.setMinimumHeight(50)
        roll_btn.clicked.connect(self.roll_dice)
        dice_ctrl.addWidget(roll_btn)
        
        dice_layout.addLayout(dice_ctrl)
        
        self.dice_result_label = QLabel("Ergebnis: -")
        self.dice_result_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f1c40f;")
        self.dice_result_label.setAlignment(Qt.AlignCenter)
        dice_layout.addWidget(self.dice_result_label)
        
        layout.addWidget(dice_group)
        
        # Waffen
        weapons_group = QGroupBox("⚔️ Waffen")
        weapons_layout = QVBoxLayout(weapons_group)
        self.weapons_list = QListWidget()
        weapons_layout.addWidget(self.weapons_list)
        
        weap_btn_layout = QHBoxLayout()
        add_weap_btn = QPushButton("➕ Waffe hinzufügen")
        add_weap_btn.clicked.connect(self.add_weapon)
        weap_btn_layout.addWidget(add_weap_btn)
        weapons_layout.addLayout(weap_btn_layout)
        
        layout.addWidget(weapons_group)
        
        # Zauber
        spells_group = QGroupBox("✨ Zauber/Magie")
        spells_layout = QVBoxLayout(spells_group)
        self.spells_list = QListWidget()
        spells_layout.addWidget(self.spells_list)
        
        spell_btn_layout = QHBoxLayout()
        add_spell_btn = QPushButton("➕ Zauber hinzufügen")
        add_spell_btn.clicked.connect(self.add_spell)
        spell_btn_layout.addWidget(add_spell_btn)
        spells_layout.addLayout(spell_btn_layout)
        
        layout.addWidget(spells_group)
        
        return widget
    
    def create_missions_tab(self) -> QWidget:
        """Erstellt den Missions-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Aktive Missionen (oben)
        active_group = QGroupBox("🟢 Aktive Missionen")
        active_layout = QVBoxLayout(active_group)
        self.active_missions_list = QListWidget()
        active_layout.addWidget(self.active_missions_list)
        layout.addWidget(active_group)
        
        # Abgeschlossene Missionen
        completed_group = QGroupBox("✅ Abgeschlossen")
        completed_layout = QVBoxLayout(completed_group)
        self.completed_missions_list = QListWidget()
        completed_layout.addWidget(self.completed_missions_list)
        layout.addWidget(completed_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_mission_btn = QPushButton("➕ Mission hinzufügen")
        add_mission_btn.clicked.connect(self.add_mission)
        btn_layout.addWidget(add_mission_btn)
        
        complete_btn = QPushButton("✅ Abschließen")
        btn_layout.addWidget(complete_btn)
        
        fail_btn = QPushButton("❌ Gescheitert")
        btn_layout.addWidget(fail_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def create_immersion_tab(self) -> QWidget:
        """Erstellt den Immersion-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Soundboard
        self.soundboard = SoundboardWidget(self.audio_manager)
        splitter.addWidget(self.soundboard)
        
        # Lichteffekte
        light_widget = QWidget()
        light_layout = QVBoxLayout(light_widget)
        
        light_layout.addWidget(QLabel("💡 Lichteffekte"))
        
        light_btn_layout = QGridLayout()
        
        lightning_btn = QPushButton("⚡ Blitz")
        lightning_btn.clicked.connect(lambda: self.light_manager.flash_lightning())
        light_btn_layout.addWidget(lightning_btn, 0, 0)
        
        strobe_btn = QPushButton("🔦 Stroboskop")
        strobe_btn.clicked.connect(lambda: self.light_manager.flash_strobe())
        light_btn_layout.addWidget(strobe_btn, 0, 1)
        
        day_btn = QPushButton("☀️ Tag")
        day_btn.clicked.connect(lambda: self.light_manager.set_day_night(False))
        light_btn_layout.addWidget(day_btn, 1, 0)
        
        night_btn = QPushButton("🌙 Nacht")
        night_btn.clicked.connect(lambda: self.light_manager.set_day_night(True))
        light_btn_layout.addWidget(night_btn, 1, 1)
        
        clear_btn = QPushButton("🔲 Effekte löschen")
        clear_btn.clicked.connect(self.light_manager.clear_filter)
        light_btn_layout.addWidget(clear_btn, 2, 0, 1, 2)
        
        light_layout.addLayout(light_btn_layout)
        
        # Farbfilter
        color_btn = QPushButton("🎨 Farbfilter wählen")
        color_btn.clicked.connect(self.choose_color_filter)
        light_layout.addWidget(color_btn)
        
        light_layout.addStretch()
        splitter.addWidget(light_widget)
        
        # Musik
        music_widget = QWidget()
        music_layout = QVBoxLayout(music_widget)
        
        music_layout.addWidget(QLabel("🎵 Hintergrundmusik"))
        
        self.music_list = QListWidget()
        self.music_list.itemDoubleClicked.connect(self.play_music)
        music_layout.addWidget(self.music_list)
        
        # Musik aus Verzeichnis laden
        for path in MUSIC_DIR.glob("*.*"):
            if path.suffix.lower() in ['.mp3', '.wav', '.ogg']:
                self.music_list.addItem(path.name)
        
        music_ctrl = QHBoxLayout()
        play_btn = QPushButton("▶️")
        play_btn.clicked.connect(self.play_music)
        music_ctrl.addWidget(play_btn)
        
        stop_btn = QPushButton("⏹️")
        stop_btn.clicked.connect(self.audio_manager.stop_music)
        music_ctrl.addWidget(stop_btn)
        
        music_layout.addLayout(music_ctrl)
        
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Lautstärke:"))
        music_vol_slider = QSlider(Qt.Horizontal)
        music_vol_slider.setRange(0, 100)
        music_vol_slider.setValue(50)
        music_vol_slider.valueChanged.connect(lambda v: self.audio_manager.set_music_volume(v/100))
        vol_layout.addWidget(music_vol_slider)
        music_layout.addLayout(vol_layout)
        
        music_layout.addStretch()
        splitter.addWidget(music_widget)
        
        layout.addWidget(splitter)
        
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Erstellt den Einstellungen-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Session-Einstellungen
        session_group = QGroupBox("📋 Session-Einstellungen")
        session_layout = QFormLayout(session_group)
        
        self.round_based_check = QCheckBox("Rundenbasiert")
        self.round_based_check.stateChanged.connect(self.on_round_mode_changed)
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
        world_group = QGroupBox("🌍 Welt-Einstellungen")
        world_layout = QFormLayout(world_group)
        
        self.time_ratio_spin = QDoubleSpinBox()
        self.time_ratio_spin.setRange(0.1, 100)
        self.time_ratio_spin.setValue(1.0)
        world_layout.addRow("Zeitverhältnis (1h real = X Spielstunden):", self.time_ratio_spin)
        
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
        
        return widget
    
    def create_turn_panel(self) -> QWidget:
        """Erstellt das Rundensteuerungs-Panel"""
        panel = QWidget()
        panel.setMaximumWidth(250)
        layout = QVBoxLayout(panel)
        
        layout.addWidget(QLabel("⏱️ Rundensteuerung"))
        
        # Aktueller Spieler
        self.current_turn_label = QLabel("Aktuell: -")
        self.current_turn_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f1c40f;")
        layout.addWidget(self.current_turn_label)
        
        # Zugreihenfolge
        self.turn_order_list = QListWidget()
        layout.addWidget(self.turn_order_list)
        
        # Zug-Buttons
        self.end_turn_btn = QPushButton("✅ Zug beenden")
        self.end_turn_btn.clicked.connect(self.end_turn)
        self.end_turn_btn.setMinimumHeight(40)
        layout.addWidget(self.end_turn_btn)
        
        # Aktionen-Zähler
        self.actions_label = QLabel("Aktionen: 0/∞")
        layout.addWidget(self.actions_label)
        
        layout.addStretch()
        
        return panel
    
    def setup_menu(self):
        """Erstellt die Menüleiste"""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("📁 Datei")
        
        new_session_action = QAction("Neue Session", self)
        new_session_action.setShortcut(QKeySequence.New)
        new_session_action.triggered.connect(self.new_session)
        file_menu.addAction(new_session_action)
        
        load_session_action = QAction("Session laden", self)
        load_session_action.setShortcut(QKeySequence.Open)
        load_session_action.triggered.connect(self.load_session)
        file_menu.addAction(load_session_action)
        
        save_session_action = QAction("Session speichern", self)
        save_session_action.setShortcut(QKeySequence.Save)
        save_session_action.triggered.connect(self.save_session)
        file_menu.addAction(save_session_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Beenden", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("❓ Hilfe")
        
        about_action = QAction("Über", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Erstellt die Toolbar"""
        toolbar = QToolBar("Haupt-Toolbar")
        self.addToolBar(toolbar)
        
        start_action = QAction("🚀 Spiel starten", self)
        start_action.triggered.connect(self.start_game)
        toolbar.addAction(start_action)
        
        toolbar.addSeparator()
        
        dice_action = QAction("🎲 Würfeln", self)
        dice_action.triggered.connect(self.roll_dice)
        toolbar.addAction(dice_action)
        
        toolbar.addSeparator()
        
        save_action = QAction("💾 Speichern", self)
        save_action.triggered.connect(self.save_session)
        toolbar.addAction(save_action)
    
    def apply_dark_theme(self):
        """Wendet Dark Theme an"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0f0f23;
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1a1a2e;
            }
            QTabBar::tab {
                background-color: #16213e;
                color: #aaa;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a2e;
                color: #fff;
            }
            QPushButton {
                background-color: #16213e;
                color: #fff;
                border: 1px solid #333;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1f3460;
            }
            QPushButton:pressed {
                background-color: #3498db;
            }
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: #16213e;
                color: #fff;
                border: 1px solid #333;
                padding: 5px;
                border-radius: 3px;
            }
            QGroupBox {
                border: 1px solid #333;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #3498db;
            }
            QListWidget, QTreeWidget, QTableWidget {
                background-color: #16213e;
                color: #fff;
                border: 1px solid #333;
            }
            QHeaderView::section {
                background-color: #1a1a2e;
                color: #fff;
                border: 1px solid #333;
                padding: 5px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #16213e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QProgressBar {
                border: 1px solid #333;
                border-radius: 5px;
                text-align: center;
            }
            QStatusBar {
                background-color: #16213e;
                color: #aaa;
            }
            QMenuBar {
                background-color: #16213e;
                color: #fff;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: #1a1a2e;
                color: #fff;
                border: 1px solid #333;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
            QToolBar {
                background-color: #16213e;
                border: none;
                spacing: 5px;
            }
        """)
    
    # ==================== EVENT HANDLERS ====================
    
    def on_message_sent(self, message: ChatMessage):
        """Wird aufgerufen wenn eine Nachricht gesendet wird"""
        session = self.data_manager.current_session
        if session:
            session.chat_history.append(message)
            self.data_manager.save_session(session)
            logger.info(f"Nachricht: [{message.role.value}] {message.author}: {message.content[:50]}...")
    
    def on_world_changed(self, index):
        """Wird aufgerufen wenn eine andere Welt ausgewählt wird"""
        world_id = self.world_combo.currentData()
        if world_id and world_id in self.data_manager.worlds:
            world = self.data_manager.worlds[world_id]
            self.data_manager.current_world = world
            self.world_name_edit.setText(world.settings.name)
            self.world_genre_edit.setText(world.settings.genre)
            self.world_desc_edit.setPlainText(world.settings.description)
            self.refresh_locations_tree()
    
    def on_round_mode_changed(self, state):
        """Wird aufgerufen wenn Rundenmodus geändert wird"""
        is_round_based = state == Qt.Checked
        self.actions_spin.setEnabled(is_round_based)
        self.turn_panel.setVisible(is_round_based)
    
    def on_location_entered(self, location_id: str):
        """Wird aufgerufen wenn ein Ort betreten wird"""
        session = self.data_manager.current_session
        world = self.data_manager.current_world
        
        if session and world and location_id in world.locations:
            loc = world.locations[location_id]
            session.current_location_id = location_id
            
            # Trigger auslösen
            for trigger in loc.triggers:
                if trigger.trigger_type == TriggerType.ON_EVERY_ENTER:
                    self._fire_trigger(trigger)
                elif trigger.trigger_type == TriggerType.ON_FIRST_ENTER and loc.first_visit:
                    self._fire_trigger(trigger)
            
            loc.first_visit = False
            loc.visited = True
            
            # Hintergrund-Audio
            if loc.background_music:
                self.audio_manager.play_music(loc.background_music)
            
            # Log
            msg = ChatMessage(
                role=MessageRole.SYSTEM,
                author="System",
                content=f"🚪 Ort betreten: {loc.name}"
            )
            self.chat_widget.add_message(msg)
            session.chat_history.append(msg)
            
            self.data_manager.save_world(world)
            self.data_manager.save_session(session)
    
    def on_location_exited(self, location_id: str):
        """Wird aufgerufen wenn ein Ort verlassen wird"""
        world = self.data_manager.current_world
        if world and location_id in world.locations:
            loc = world.locations[location_id]
            
            # Exit-Trigger
            for trigger in loc.triggers:
                if trigger.trigger_type == TriggerType.ON_EVERY_LEAVE:
                    self._fire_trigger(trigger)
            
            self.audio_manager.stop_music()
    
    def _fire_trigger(self, trigger: Trigger):
        """Führt einen Trigger aus"""
        if not trigger.enabled:
            return
        
        if trigger.sound_file:
            self.audio_manager.play_sound(trigger.sound_file)
        
        if trigger.light_effect:
            if trigger.light_effect == "lightning":
                self.light_manager.flash_lightning(int(trigger.light_duration * 1000))
            elif trigger.light_effect == "strobe":
                self.light_manager.flash_strobe()
        
        if trigger.chat_message:
            msg = ChatMessage(
                role=MessageRole.NARRATOR,
                author="Erzähler",
                content=trigger.chat_message
            )
            self.chat_widget.add_message(msg)
            if self.data_manager.current_session:
                self.data_manager.current_session.chat_history.append(msg)
        
        trigger.triggered_count += 1
    
    # ==================== ACTIONS ====================
    
    def refresh_world_list(self):
        """Aktualisiert die Welt-Auswahlliste"""
        self.world_combo.clear()
        for world in self.data_manager.worlds.values():
            self.world_combo.addItem(world.settings.name, world.id)
    
    def refresh_locations_tree(self):
        """Aktualisiert den Orte-Baum"""
        self.locations_tree.clear()
        world = self.data_manager.current_world
        if not world:
            return
        
        for loc in world.locations.values():
            item = QTreeWidgetItem([
                loc.name,
                "✓" if loc.has_interior else "✗",
                str(len(loc.triggers))
            ])
            item.setData(0, Qt.UserRole, loc.id)
            self.locations_tree.addTopLevelItem(item)
    
    def create_new_world(self):
        """Erstellt eine neue Welt"""
        name, ok = QInputDialog.getText(self, "Neue Welt", "Name der Welt:")
        if ok and name:
            world = self.data_manager.create_world(name)
            self.refresh_world_list()
            self.world_combo.setCurrentText(name)
            self.status_bar.showMessage(f"Welt '{name}' erstellt")
    
    def save_world(self):
        """Speichert die aktuelle Welt"""
        world = self.data_manager.current_world
        if not world:
            return
        
        world.settings.name = self.world_name_edit.text()
        world.settings.genre = self.world_genre_edit.text()
        world.settings.description = self.world_desc_edit.toPlainText()
        
        if self.data_manager.save_world(world):
            self.status_bar.showMessage("Welt gespeichert")
    
    def add_location(self):
        """Fügt einen neuen Ort hinzu"""
        world = self.data_manager.current_world
        if not world:
            QMessageBox.warning(self, "Fehler", "Keine Welt ausgewählt!")
            return
        
        name, ok = QInputDialog.getText(self, "Neuer Ort", "Name des Ortes:")
        if ok and name:
            loc_id = str(uuid.uuid4())[:8]
            location = Location(id=loc_id, name=name)
            world.locations[loc_id] = location
            self.data_manager.save_world(world)
            self.refresh_locations_tree()
    
    def create_character(self):
        """Erstellt einen neuen Charakter"""
        name, ok = QInputDialog.getText(self, "Neuer Charakter", "Name:")
        if ok and name:
            char_id = str(uuid.uuid4())[:8]
            character = Character(id=char_id, name=name)
            
            session = self.data_manager.current_session
            if session:
                session.characters[char_id] = character
                self.data_manager.save_session(session)
                self.refresh_character_table()
    
    def refresh_character_table(self):
        """Aktualisiert die Charaktertabelle"""
        session = self.data_manager.current_session
        if not session:
            return
        
        self.char_table.setRowCount(len(session.characters))
        for row, char in enumerate(session.characters.values()):
            self.char_table.setItem(row, 0, QTableWidgetItem(char.name))
            self.char_table.setItem(row, 1, QTableWidgetItem(char.player_name or "-"))
            self.char_table.setItem(row, 2, QTableWidgetItem(char.race))
            self.char_table.setItem(row, 3, QTableWidgetItem(char.profession))
            self.char_table.setItem(row, 4, QTableWidgetItem(str(char.level)))
            self.char_table.setItem(row, 5, QTableWidgetItem(f"{char.health}/{char.max_health}"))
            self.char_table.setItem(row, 6, QTableWidgetItem("✓" if char.is_npc else "✗"))
    
    def add_mission(self):
        """Fügt eine neue Mission hinzu"""
        session = self.data_manager.current_session
        if not session:
            QMessageBox.warning(self, "Fehler", "Keine aktive Session!")
            return
        
        name, ok = QInputDialog.getText(self, "Neue Mission", "Missionsname:")
        if ok and name:
            mission_id = str(uuid.uuid4())[:8]
            mission = Mission(
                id=mission_id,
                name=name,
                description="",
                objective="Ziel definieren..."
            )
            session.active_missions[mission_id] = mission
            self.data_manager.save_session(session)
            self.refresh_missions_list()
    
    def refresh_missions_list(self):
        """Aktualisiert die Missionslisten"""
        session = self.data_manager.current_session
        if not session:
            return
        
        self.active_missions_list.clear()
        self.completed_missions_list.clear()
        
        for mission in session.active_missions.values():
            if mission.status == MissionStatus.ACTIVE:
                self.active_missions_list.addItem(f"🟢 {mission.name}: {mission.objective}")
            elif mission.status == MissionStatus.COMPLETED:
                self.completed_missions_list.addItem(f"✅ {mission.name}")
            else:
                self.completed_missions_list.addItem(f"❌ {mission.name}")
    
    def add_weapon(self):
        """Fügt eine neue Waffe hinzu"""
        world = self.data_manager.current_world
        if not world:
            return
        
        name, ok = QInputDialog.getText(self, "Neue Waffe", "Name der Waffe:")
        if ok and name:
            weapon_id = str(uuid.uuid4())[:8]
            weapon = Weapon(id=weapon_id, name=name)
            world.weapons[weapon_id] = weapon
            self.data_manager.save_world(world)
            self.weapons_list.addItem(f"⚔️ {name}")
    
    def add_spell(self):
        """Fügt einen neuen Zauber hinzu"""
        world = self.data_manager.current_world
        if not world:
            return
        
        name, ok = QInputDialog.getText(self, "Neuer Zauber", "Name des Zaubers:")
        if ok and name:
            spell_id = str(uuid.uuid4())[:8]
            spell = Spell(id=spell_id, name=name)
            world.spells[spell_id] = spell
            self.data_manager.save_world(world)
            self.spells_list.addItem(f"✨ {name}")
    
    def roll_dice(self):
        """Würfelt"""
        count = self.dice_count_spin.value()
        sides_text = self.dice_sides_combo.currentText()
        sides = int(sides_text[1:])  # "W20" -> 20
        
        result = self.dice_roller.roll(dice_count=count, dice_sides=sides)
        
        rolls_str = ", ".join(map(str, result["rolls"]))
        self.dice_result_label.setText(f"🎲 {result['dice']}: [{rolls_str}] = {result['total']}")
        
        # In Chat loggen
        msg = ChatMessage(
            role=MessageRole.SYSTEM,
            author="Würfel",
            content=f"🎲 {result['dice']}: {rolls_str} = **{result['total']}**"
        )
        self.chat_widget.add_message(msg)
        
        session = self.data_manager.current_session
        if session:
            session.chat_history.append(msg)
    
    def end_turn(self):
        """Beendet den aktuellen Zug"""
        session = self.data_manager.current_session
        if not session or not session.is_round_based:
            return
        
        if session.turn_order:
            session.current_turn_index = (session.current_turn_index + 1) % len(session.turn_order)
            current_char_id = session.turn_order[session.current_turn_index]
            
            if current_char_id in session.characters:
                char = session.characters[current_char_id]
                self.current_turn_label.setText(f"Aktuell: {char.name}")
                
                msg = ChatMessage(
                    role=MessageRole.SYSTEM,
                    author="System",
                    content=f"🎯 Du bist dran, {char.name}! ({char.player_name or 'NPC'})"
                )
                self.chat_widget.add_message(msg)
                session.chat_history.append(msg)
            
            self.data_manager.save_session(session)
    
    def choose_color_filter(self):
        """Öffnet Farbauswahl-Dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.light_manager.set_color_filter(color.name())
    
    def play_music(self):
        """Spielt ausgewählte Musik"""
        item = self.music_list.currentItem()
        if item:
            file_path = MUSIC_DIR / item.text()
            self.audio_manager.play_music(str(file_path))
    
    def new_session(self):
        """Erstellt eine neue Session"""
        if not self.data_manager.worlds:
            QMessageBox.warning(self, "Fehler", "Erstelle zuerst eine Welt!")
            return
        
        world_names = [w.settings.name for w in self.data_manager.worlds.values()]
        world_name, ok = QInputDialog.getItem(self, "Welt auswählen", "Welt:", world_names, 0, False)
        if not ok:
            return
        
        world = next((w for w in self.data_manager.worlds.values() if w.settings.name == world_name), None)
        if not world:
            return
        
        session_name, ok = QInputDialog.getText(self, "Neue Session", "Name der Session:")
        if ok and session_name:
            session = self.data_manager.create_session(world.id, session_name)
            if session:
                self.data_manager.current_session = session
                self.data_manager.current_world = world
                self.status_bar.showMessage(f"Session '{session_name}' erstellt")
                self.prompt_widget.update_characters(session.characters)
    
    def load_session(self):
        """Lädt eine Session"""
        if not self.data_manager.sessions:
            QMessageBox.information(self, "Info", "Keine gespeicherten Sessions gefunden")
            return
        
        session_names = [s.name for s in self.data_manager.sessions.values()]
        name, ok = QInputDialog.getItem(self, "Session laden", "Session:", session_names, 0, False)
        if ok:
            session = next((s for s in self.data_manager.sessions.values() if s.name == name), None)
            if session:
                self.data_manager.current_session = session
                if session.world_id in self.data_manager.worlds:
                    self.data_manager.current_world = self.data_manager.worlds[session.world_id]
                
                self.chat_widget.load_history(session.chat_history)
                self.refresh_character_table()
                self.refresh_missions_list()
                self.prompt_widget.update_characters(session.characters)
                self.status_bar.showMessage(f"Session '{name}' geladen")
    
    def save_session(self):
        """Speichert die aktuelle Session"""
        session = self.data_manager.current_session
        if session:
            if self.data_manager.save_session(session):
                self.status_bar.showMessage("Session gespeichert")
        else:
            QMessageBox.warning(self, "Fehler", "Keine aktive Session!")
    
    def start_game(self):
        """Startet das Spiel und generiert Spielstart-Prompt"""
        session = self.data_manager.current_session
        world = self.data_manager.current_world
        
        if not session or not world:
            QMessageBox.warning(self, "Fehler", "Erstelle/lade zuerst eine Session!")
            return
        
        # Spielstart-Prompt generieren und kopieren
        prompt = PromptGenerator.generate_game_start_prompt(session, world)
        QApplication.clipboard().setText(prompt)
        
        # In Chat loggen
        msg = ChatMessage(
            role=MessageRole.SYSTEM,
            author="System",
            content="🚀 Spiel gestartet! Der Spielstart-Prompt wurde in die Zwischenablage kopiert."
        )
        self.chat_widget.add_message(msg)
        session.chat_history.append(msg)
        
        self.data_manager.save_session(session)
        self.status_bar.showMessage("Spiel gestartet - Prompt in Zwischenablage!")
        
        QMessageBox.information(self, "Spiel gestartet", 
            "Der Spielstart-Prompt wurde in die Zwischenablage kopiert.\n"
            "Du kannst ihn jetzt an deine KI senden!")
    
    def show_about(self):
        """Zeigt About-Dialog"""
        QMessageBox.about(self, "Über",
            f"<h2>{APP_TITLE}</h2>"
            f"<p>Version {VERSION}</p>"
            f"<p>Ein umfassendes Pen & Paper Toolkit</p>"
            f"<p>Features:</p>"
            f"<ul>"
            f"<li>Immersion: Soundboard, Lichteffekte, Tag/Nacht</li>"
            f"<li>Weltverwaltung: Karten, Orte, Trigger</li>"
            f"<li>Kampfsystem: Waffen, Magie, Würfel</li>"
            f"<li>KI-Integration: Promptgenerator</li>"
            f"</ul>"
        )
    
    def closeEvent(self, event):
        """Wird beim Schließen aufgerufen"""
        # Auto-Save
        if self.data_manager.current_session:
            self.data_manager.save_session(self.data_manager.current_session)
        
        if self.data_manager.current_world:
            self.data_manager.save_world(self.data_manager.current_world)
        
        logger.info("Anwendung beendet")
        event.accept()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Dark Palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15, 15, 35))
    palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
    palette.setColor(QPalette.Base, QColor(22, 33, 62))
    palette.setColor(QPalette.AlternateBase, QColor(26, 26, 46))
    palette.setColor(QPalette.ToolTipBase, QColor(224, 224, 224))
    palette.setColor(QPalette.ToolTipText, QColor(224, 224, 224))
    palette.setColor(QPalette.Text, QColor(224, 224, 224))
    palette.setColor(QPalette.Button, QColor(22, 33, 62))
    palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(52, 152, 219))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = RPXLightMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
