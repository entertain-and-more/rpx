"""Session-Datenmodelle: ChatMessage, Mission, Session."""

import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from rpx_pro.constants import _filter_dataclass_fields
from rpx_pro.models.enums import (
    MessageRole, MissionStatus, WeatherType, TimeOfDay,
)
from rpx_pro.models.entities import Character, PlayerGroup


@dataclass
class ChatMessage:
    """Repraesentiert eine Chat-Nachricht"""
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
class Mission:
    """Quest/Mission"""
    id: str
    name: str
    description: str
    objective: str
    status: MissionStatus = MissionStatus.ACTIVE
    # Zuordnung
    is_group_quest: bool = False
    assigned_to: List[str] = field(default_factory=list)
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
        data = dict(data)
        if 'status' in data:
            data['status'] = MissionStatus(data['status'])
        return cls(**_filter_dataclass_fields(cls, data))


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
    turn_order: List[str] = field(default_factory=list)
    current_turn_index: int = 0
    actions_per_turn: int = 0
    current_round: int = 1
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
            'current_round': self.current_round,
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
            current_round=data.get('current_round', 1),
            gm_is_human=data.get('gm_is_human', True),
            gm_player_name=data.get('gm_player_name', ''),
            current_location_id=data.get('current_location_id'),
            current_weather=WeatherType(data.get('current_weather', 'clear')),
            current_time_of_day=TimeOfDay(data.get('current_time_of_day', 'noon'))
        )
