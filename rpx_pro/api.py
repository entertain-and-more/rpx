"""RPXProAPI: Programmatische Python-API fuer RPX Pro."""

import random
from pathlib import Path
from typing import Any, List, Optional

from rpx_pro.constants import (
    DEFAULT_UNARMED_CRIT_THRESHOLD,
    MUSIC_DIR,
    SOUNDS_DIR,
    generate_short_id,
)
from rpx_pro.models.enums import (
    MessageRole,
    MissionStatus,
    TimeOfDay,
    WeatherType,
)
from rpx_pro.models.entities import Character
from rpx_pro.models.session import ChatMessage, Mission
from rpx_pro.models.world import Location
from rpx_pro.managers.data_manager import DataManager
from rpx_pro.managers.prompt_generator import PromptGenerator


class RPXProAPI:
    """Programmatische API fuer RPX Pro - gibt JSON-serialisierbare Dicts zurueck."""

    def __init__(
        self,
        data_manager: DataManager,
        audio_manager: Optional[Any] = None,
        dice_roller: Optional[Any] = None,
        light_manager: Optional[Any] = None,
    ):
        self.dm = data_manager
        self.audio_manager = audio_manager
        self.dice_roller = dice_roller
        self.light_manager = light_manager

    # --- Welt ---

    def create_world(self, name: str, genre: str = "Fantasy") -> dict:
        world = self.dm.create_world(name, genre)
        return {"id": world.id, "name": world.settings.name, "genre": world.settings.genre}

    def list_worlds(self) -> list:
        return [
            {"id": w.id, "name": w.settings.name, "genre": w.settings.genre}
            for w in self.dm.worlds.values()
        ]

    def load_world(self, world_id: str) -> dict:
        if world_id not in self.dm.worlds:
            return {"error": f"Welt {world_id} nicht gefunden"}
        world = self.dm.worlds[world_id]
        self.dm.current_world = world
        return {"id": world.id, "name": world.settings.name, "genre": world.settings.genre}

    def get_world(self, world_id: Optional[str] = None) -> dict:
        """Gibt ausfuehrliche Details der aktuellen oder angegebenen Welt zurueck."""
        world = self.dm.worlds.get(world_id) if world_id else self.dm.current_world
        if not world:
            return {"error": f"Welt {world_id or 'aktuell'} nicht gefunden"}
        return {
            "id": world.id,
            "name": world.settings.name,
            "description": world.settings.description,
            "genre": world.settings.genre,
            "settings": world.settings.to_dict(),
            "locations_count": len(world.locations),
            "nations": [n.name for n in world.nations.values()],
            "races": [r.name for r in world.races.values()],
            "weapons_count": len(world.weapons),
            "spells_count": len(world.spells),
            "typical_items_count": len(world.typical_items),
        }

    # --- Orte & Umgebung ---

    def create_location(
        self,
        name: str,
        description: str = "",
        location_type: str = "city",
        parent_id: Optional[str] = None,
    ) -> dict:
        """Erstellt einen neuen Ort in der aktuellen Welt."""
        world = self.dm.current_world
        if not world:
            return {"error": "Keine aktive Welt geladen"}
        loc_id = generate_short_id()
        loc = Location(
            id=loc_id,
            name=name,
            description=description,
            location_type=location_type,
            parent_id=parent_id,
        )
        world.locations[loc_id] = loc
        self.dm.save_world(world)
        return {
            "id": loc_id,
            "name": name,
            "description": description,
            "location_type": location_type,
            "parent_id": parent_id,
        }

    def list_locations(self) -> list:
        """Listet alle Orte der aktuellen Welt auf."""
        world = self.dm.current_world
        if not world:
            return []
        return [
            {
                "id": loc.id,
                "name": loc.name,
                "location_type": loc.location_type,
                "description": loc.description,
                "visited": loc.visited,
                "parent_id": loc.parent_id,
            }
            for loc in world.locations.values()
        ]

    def set_location(self, location_id: str) -> dict:
        """Setzt den aktuellen Aufenthaltsort in der aktiven Session."""
        session = self.dm.current_session
        world = self.dm.current_world
        if not session:
            return {"error": "Keine aktive Session"}
        if world and location_id not in world.locations:
            return {"error": f"Ort {location_id} nicht in Welt gefunden"}

        session.current_location_id = location_id
        loc_name = ""
        if world and location_id in world.locations:
            loc = world.locations[location_id]
            loc.visited = True
            loc_name = loc.name
            self.dm.save_world(world)

        self.dm.save_session(session)
        return {
            "current_location_id": location_id,
            "name": loc_name,
            "status": "location_updated",
        }

    def set_environment(
        self,
        weather: Optional[str] = None,
        time_of_day: Optional[str] = None,
    ) -> dict:
        """Setzt Wetter und Tageszeit in der aktiven Session."""
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}

        if weather is not None:
            try:
                session.current_weather = WeatherType(weather.lower())
            except ValueError:
                return {
                    "error": f"Ungueltiges Wetter '{weather}'. Erlaubt: {[w.value for w in WeatherType]}"
                }

        if time_of_day is not None:
            try:
                session.current_time_of_day = TimeOfDay(time_of_day.lower())
            except ValueError:
                return {
                    "error": f"Ungueltige Tageszeit '{time_of_day}'. Erlaubt: {[t.value for t in TimeOfDay]}"
                }

        self.dm.save_session(session)
        return {
            "current_weather": session.current_weather.value,
            "current_time_of_day": session.current_time_of_day.value,
        }

    # --- Session & Spielstatus ---

    def create_session(self, world_id: str, name: str) -> dict:
        session = self.dm.create_session(world_id, name)
        if not session:
            return {"error": "Welt nicht gefunden"}
        return {"id": session.id, "world_id": session.world_id, "name": session.name}

    def list_sessions(self) -> list:
        return [
            {"id": s.id, "world_id": s.world_id, "name": s.name}
            for s in self.dm.sessions.values()
        ]

    def load_session(self, session_id: str) -> dict:
        if session_id not in self.dm.sessions:
            return {"error": f"Session {session_id} nicht gefunden"}
        session = self.dm.sessions[session_id]
        self.dm.current_session = session
        self.dm.current_world = self.dm.worlds.get(session.world_id)
        return {"id": session.id, "name": session.name, "characters": len(session.characters)}

    def get_session_state(self) -> dict:
        """Umfassender Snapshot fuer LLM-Spielleiter: Welt, Ort, Umwelt, Charaktere, Missionen."""
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}
        world = self.dm.current_world

        loc_name = ""
        if world and session.current_location_id and session.current_location_id in world.locations:
            loc_name = world.locations[session.current_location_id].name

        return {
            "session_id": session.id,
            "session_name": session.name,
            "world_id": session.world_id,
            "world_name": world.settings.name if world else "",
            "current_location_id": session.current_location_id,
            "current_location_name": loc_name,
            "current_weather": session.current_weather.value,
            "current_time_of_day": session.current_time_of_day.value,
            "is_round_based": session.is_round_based,
            "current_round": session.current_round,
            "active_missions_count": len(session.active_missions),
            "characters": [
                {
                    "id": cid,
                    "name": c.name,
                    "health": c.health,
                    "max_health": c.max_health,
                    "gold": c.gold,
                    "defeated": c.health <= 0,
                }
                for cid, c in session.characters.items()
            ],
        }

    # --- Charaktere ---

    def create_character(self, name: str, **kwargs) -> dict:
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}
        char_id = generate_short_id()
        char = Character(id=char_id, name=name, **kwargs)
        session.characters[char_id] = char
        self.dm.save_session(session)
        return {"id": char_id, "name": name}

    def get_character(self, char_id: str) -> dict:
        session = self.dm.current_session
        if not session or char_id not in session.characters:
            return {"error": "Charakter nicht gefunden"}
        return session.characters[char_id].to_dict()

    def heal_character(self, char_id: str, amount: int) -> dict:
        session = self.dm.current_session
        if not session or char_id not in session.characters:
            return {"error": "Charakter nicht gefunden"}
        char = session.characters[char_id]
        old_hp = char.health
        char.health = min(char.max_health, char.health + amount)
        self.dm.save_session(session)
        return {"name": char.name, "old_hp": old_hp, "new_hp": char.health, "healed": char.health - old_hp}

    def damage_character(self, char_id: str, amount: int) -> dict:
        session = self.dm.current_session
        if not session or char_id not in session.characters:
            return {"error": "Charakter nicht gefunden"}
        char = session.characters[char_id]
        old_hp = char.health
        char.health = max(0, char.health - amount)
        self.dm.save_session(session)
        return {"name": char.name, "old_hp": old_hp, "new_hp": char.health, "damage": old_hp - char.health}

    def get_inventory(self, char_id: str) -> dict:
        session = self.dm.current_session
        if not session or char_id not in session.characters:
            return {"error": "Charakter nicht gefunden"}
        char = session.characters[char_id]
        items = []
        world = self.dm.current_world
        for item_id, count in char.inventory.items():
            name = item_id
            if world and item_id in world.typical_items:
                name = world.typical_items[item_id].name
            items.append({"item_id": item_id, "name": name, "count": count})
        return {"character": char.name, "gold": char.gold, "items": items}

    def give_item(self, char_id: str, item_id: str, count: int = 1) -> dict:
        session = self.dm.current_session
        if not session or char_id not in session.characters:
            return {"error": "Charakter nicht gefunden"}
        char = session.characters[char_id]
        char.inventory[item_id] = char.inventory.get(item_id, 0) + count
        self.dm.save_session(session)
        return {"character": char.name, "item_id": item_id, "count": char.inventory[item_id]}

    # --- Kampf & Runden / Turn Order ---

    def get_combat_state(self) -> dict:
        """Liefert den aktuellen Kampfstatus, Runden- und Zugreihenfolge."""
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}

        current_actor = None
        if session.turn_order and 0 <= session.current_turn_index < len(session.turn_order):
            actor_id = session.turn_order[session.current_turn_index]
            char = session.characters.get(actor_id)
            current_actor = {
                "id": actor_id,
                "name": char.name if char else actor_id,
                "health": char.health if char else 0,
            }

        return {
            "in_combat": session.is_round_based,
            "current_round": session.current_round,
            "current_turn_index": session.current_turn_index,
            "turn_order": session.turn_order,
            "current_actor": current_actor,
            "characters": {
                cid: {
                    "name": c.name,
                    "health": c.health,
                    "max_health": c.max_health,
                    "defeated": c.health <= 0,
                }
                for cid, c in session.characters.items()
            },
        }

    def start_combat(
        self,
        character_ids: Optional[List[str]] = None,
        shuffle: bool = False,
    ) -> dict:
        """Startet rundenbasierten Kampf und initialisiert die Initiativ-Reihenfolge."""
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}

        if character_ids is not None:
            order = [cid for cid in character_ids if cid in session.characters]
        else:
            order = list(session.characters.keys())

        if not order:
            return {"error": "Keine Charaktere fuer den Kampf verfuegbar"}

        if shuffle:
            # RPG-Initiative: nach Geschicklichkeit (dexterity) absteigend
            order.sort(
                key=lambda cid: (
                    session.characters[cid].dexterity if cid in session.characters else 10,
                    random.random(),
                ),
                reverse=True,
            )

        session.is_round_based = True
        session.turn_order = order
        session.current_turn_index = 0
        session.current_round = 1
        self.dm.save_session(session)
        return self.get_combat_state()

    def next_turn(self) -> dict:
        """Schaltet zum naechsten Akteur weiter (erhoeht Runde beim Durchlauf)."""
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}
        if not session.is_round_based or not session.turn_order:
            return {"error": "Kein aktiver Kampf"}

        session.current_turn_index += 1
        round_advanced = False
        if session.current_turn_index >= len(session.turn_order):
            session.current_turn_index = 0
            session.current_round += 1
            round_advanced = True

        self.dm.save_session(session)
        state = self.get_combat_state()
        state["round_advanced"] = round_advanced
        return state

    def end_combat(self) -> dict:
        """Beendet den rundenbasierten Kampf und raeumt die Zugreihenfolge auf."""
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}

        session.is_round_based = False
        session.turn_order = []
        session.current_turn_index = 0
        self.dm.save_session(session)
        return {"status": "combat_ended", "in_combat": False}

    def execute_attack(
        self,
        attacker_id: str,
        defender_id: str,
        weapon_id: Optional[str] = None,
    ) -> dict:
        """Fuehrt einen vollstaendigen Angriff nach RPX-Regeln programmatisch aus."""
        session = self.dm.current_session
        world = self.dm.current_world
        if not session or not world:
            return {"error": "Keine aktive Session oder Welt geladen"}

        attacker = session.characters.get(attacker_id)
        defender = session.characters.get(defender_id)
        if not attacker:
            return {"error": f"Angreifer {attacker_id} nicht gefunden"}
        if not defender:
            return {"error": f"Verteidiger {defender_id} nicht gefunden"}
        if attacker_id == defender_id:
            return {"error": "Angreifer und Verteidiger muessen verschieden sein"}

        # Waffe bestimmen
        chosen_weapon_id = weapon_id or attacker.equipped_weapon
        weapon = None
        if chosen_weapon_id and chosen_weapon_id in world.weapons:
            weapon = world.weapons[chosen_weapon_id]

        # Trefferwurf & Schwelle
        hit_roll = random.randint(1, 20)
        accuracy = weapon.accuracy if weapon else 0.5
        hit_threshold = max(1, int(20 - accuracy * 20))

        # Skill-Bonus
        skill_bonus = 0
        if world.skill_definitions:
            for skill_name, skill_def in world.skill_definitions.items():
                affects = skill_def.get("affects", {})
                if "strength" in affects or "dexterity" in affects:
                    skill_bonus += attacker.skills.get(skill_name, 0)

        effective_roll = hit_roll + skill_bonus
        is_hit = effective_roll >= hit_threshold
        final_dmg = 0
        is_crit = False

        lines = [f"Angriff: {attacker.name} -> {defender.name}"]
        weapon_name = weapon.name if weapon else "Unbewaffnet"
        lines.append(f"Waffe: {weapon_name} | Wurf: {hit_roll} (+ Skill {skill_bonus}) vs. Schwelle {hit_threshold}")

        if not is_hit:
            lines.append("Ergebnis: VERFEHLT!")
            summary = f"{attacker.name} greift {defender.name} mit {weapon_name} an, verfehlt aber knapp."
        else:
            if weapon:
                base_dmg = random.randint(weapon.damage_min, weapon.damage_max)
                is_crit = hit_roll >= weapon.critical_threshold
                if is_crit:
                    base_dmg = int(base_dmg * weapon.critical_multiplier)
            else:
                base_dmg = random.randint(1, 4)
                is_crit = hit_roll >= DEFAULT_UNARMED_CRIT_THRESHOLD
                if is_crit:
                    base_dmg *= 2

            str_bonus = (attacker.strength - 10) // 2
            total_dmg = max(0, base_dmg + str_bonus)

            armor_def = 0
            if defender.equipped_armor and defender.equipped_armor in world.armors:
                armor_def = world.armors[defender.equipped_armor].protection_avg

            final_dmg = max(0, total_dmg - armor_def)
            defender.health = max(0, defender.health - final_dmg)

            crit_prefix = "KRITISCHER TREFFER! " if is_crit else ""
            summary = (
                f"{crit_prefix}{attacker.name} trifft {defender.name} mit {weapon_name} "
                f"fuer {final_dmg} Schaden ({defender.health}/{defender.max_health} HP verbleibend)."
            )
            if defender.health <= 0:
                summary += f" {defender.name} ist BESIEGT!"

            lines.append(summary)

        # In Chat-Historie als Systemnachricht hinterlegen
        chat_msg = ChatMessage(
            role=MessageRole.SYSTEM,
            author="Kampf",
            content=summary,
        )
        session.chat_history.append(chat_msg)
        self.dm.save_session(session)

        return {
            "attacker_id": attacker_id,
            "attacker_name": attacker.name,
            "defender_id": defender_id,
            "defender_name": defender.name,
            "weapon": weapon_name,
            "hit_roll": hit_roll,
            "skill_bonus": skill_bonus,
            "effective_roll": effective_roll,
            "hit_threshold": hit_threshold,
            "is_hit": is_hit,
            "is_critical": is_crit,
            "damage": final_dmg,
            "defender_health": defender.health,
            "defender_max_health": defender.max_health,
            "defeated": defender.health <= 0,
            "summary": summary,
        }

    # --- Soundboard & Audio ---

    def list_sounds(self) -> list:
        """Listet alle verfuegbaren Sounds im SOUNDS_DIR auf."""
        if not SOUNDS_DIR.exists():
            return []
        sounds = []
        for path in sorted(SOUNDS_DIR.glob("*.*")):
            if path.suffix.lower() in [".mp3", ".wav", ".ogg"]:
                sounds.append({
                    "id": path.stem,
                    "name": path.name,
                    "path": str(path),
                })
        return sounds

    def play_sound(self, sound_name_or_path: str, volume: Optional[float] = None) -> dict:
        """Spielt einen Soundeffekt ab (ueber AudioManager)."""
        target_path = Path(sound_name_or_path)
        if not target_path.exists():
            candidate = SOUNDS_DIR / sound_name_or_path
            if candidate.exists():
                target_path = candidate
            else:
                for ext in [".wav", ".mp3", ".ogg"]:
                    cand_ext = SOUNDS_DIR / f"{sound_name_or_path}{ext}"
                    if cand_ext.exists():
                        target_path = cand_ext
                        break

        played = False
        if self.audio_manager:
            self.audio_manager.play_sound(str(target_path), volume=volume)
            played = True

        return {
            "sound": sound_name_or_path,
            "resolved_path": str(target_path) if target_path.exists() else None,
            "exists": target_path.exists(),
            "played": played,
            "volume": volume,
        }

    def list_music(self) -> list:
        """Listet Musikdateien im MUSIC_DIR auf."""
        if not MUSIC_DIR.exists():
            return []
        music_files = []
        for path in sorted(MUSIC_DIR.glob("*.*")):
            if path.suffix.lower() in [".mp3", ".wav", ".ogg"]:
                music_files.append({
                    "id": path.stem,
                    "name": path.name,
                    "path": str(path),
                })
        return music_files

    def play_music(self, music_name_or_path: str, loop: bool = True) -> dict:
        """Spielt Hintergrundmusik ab."""
        target_path = Path(music_name_or_path)
        if not target_path.exists():
            candidate = MUSIC_DIR / music_name_or_path
            if candidate.exists():
                target_path = candidate
            else:
                for ext in [".mp3", ".ogg", ".wav"]:
                    cand_ext = MUSIC_DIR / f"{music_name_or_path}{ext}"
                    if cand_ext.exists():
                        target_path = cand_ext
                        break

        played = False
        if self.audio_manager:
            self.audio_manager.play_music(str(target_path), loop=loop)
            played = True

        return {
            "track": music_name_or_path,
            "resolved_path": str(target_path) if target_path.exists() else None,
            "exists": target_path.exists(),
            "playing": played,
            "loop": loop,
        }

    def stop_music(self) -> dict:
        """Stoppt laufende Hintergrundmusik."""
        stopped = False
        if self.audio_manager:
            self.audio_manager.stop_music()
            stopped = True
        return {"stopped": stopped}

    def set_volume(
        self,
        music: Optional[float] = None,
        sound: Optional[float] = None,
    ) -> dict:
        """Setzt Audio-Lautstaerken (0.0 bis 1.0)."""
        if self.audio_manager:
            if music is not None:
                self.audio_manager.set_music_volume(music)
            if sound is not None:
                self.audio_manager.set_sound_volume(sound)
        return {
            "music_volume": music,
            "sound_volume": sound,
            "updated": self.audio_manager is not None,
        }

    # --- Chat ---

    def send_chat_message(self, role: str, author: str, content: str) -> dict:
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}
        try:
            msg_role = MessageRole(role)
        except ValueError:
            msg_role = MessageRole.SYSTEM
        message = ChatMessage(role=msg_role, author=author, content=content)
        session.chat_history.append(message)
        self.dm.save_session(session)
        return {"role": msg_role.value, "author": author, "content": content, "timestamp": message.timestamp}

    def get_chat_history(self, limit: int = 50) -> list:
        session = self.dm.current_session
        if not session:
            return []
        messages = session.chat_history[-limit:]
        return [m.to_dict() for m in messages]

    # --- Wuerfel ---

    def roll_dice(self, count: int = 1, sides: int = 20) -> dict:
        if self.dice_roller:
            return self.dice_roller.roll(dice_count=count, dice_sides=sides)
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        return {"dice": f"{count}W{sides}", "rolls": rolls, "total": total}

    # --- Missionen ---

    def create_mission(self, name: str, objective: str, description: str = "") -> dict:
        session = self.dm.current_session
        if not session:
            return {"error": "Keine aktive Session"}
        mission_id = generate_short_id()
        mission = Mission(id=mission_id, name=name, description=description, objective=objective)
        session.active_missions[mission_id] = mission
        self.dm.save_session(session)
        return {"id": mission_id, "name": name, "objective": objective}

    def complete_mission(self, mission_id: str) -> dict:
        session = self.dm.current_session
        if not session or mission_id not in session.active_missions:
            return {"error": "Mission nicht gefunden"}
        mission = session.active_missions[mission_id]
        mission.status = MissionStatus.COMPLETED
        session.completed_missions.append(mission_id)
        del session.active_missions[mission_id]
        self.dm.save_session(session)
        return {"id": mission_id, "name": mission.name, "status": "completed"}

    # --- Prompts ---

    def generate_start_prompt(self) -> str:
        session = self.dm.current_session
        world = self.dm.current_world
        if not session or not world:
            return ""
        return PromptGenerator.generate_game_start_prompt(session, world)

    def generate_context_update(self) -> str:
        session = self.dm.current_session
        if not session:
            return ""
        prompt = PromptGenerator.generate_context_update_prompt(session)
        session.last_clipboard_index = len(session.chat_history)
        self.dm.save_session(session)
        return prompt

    def export_campaign_bundle(
        self,
        destination: str,
        world_ids: Optional[List[str]] = None,
        session_ids: Optional[List[str]] = None,
        include_media: str = "manifest",
    ) -> dict:
        return self.dm.export_campaign_bundle(
            destination=destination,
            world_ids=world_ids,
            session_ids=session_ids,
            include_media=include_media,
        )

    def import_campaign_bundle(
        self,
        source: str,
        conflict_strategy: str = "rename",
    ) -> dict:
        return self.dm.import_campaign_bundle(
            source=source,
            conflict_strategy=conflict_strategy,
        )
