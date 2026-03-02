"""PromptGenerator: Generiert KI-Prompts fuer verschiedene Rollen."""

from datetime import datetime
from typing import Optional

from rpx_pro.models.enums import MissionStatus
from rpx_pro.models.entities import Character
from rpx_pro.models.world import Location
from rpx_pro.models.session import Session, ChatMessage
from rpx_pro.models.world import World


class PromptGenerator:
    """Generiert KI-Prompts fuer verschiedene Rollen"""

    ROLE_TEMPLATES = {
        "storyteller": "Entwickle die Geschichte weiter. Was passiert als naechstes? Beschreibe die Szene atmosphaerisch.",
        "plottwist": "Baue eine ueberraschende Wendung in die Geschichte ein. Etwas Unerwartetes soll geschehen!",
        "gamemaster": "Steuere unser Spiel. Was sind unsere Optionen? Welche Entscheidungen muessen wir treffen?",
        "enemy": "Erschaffe einen passenden Gegner fuer unsere Gruppe. Beschreibe Aussehen, Faehigkeiten und Motivation.",
        "npc": "Denke dir interessante NPCs aus und baue sie in die Szene ein. Gib ihnen Persoenlichkeit und Ziele.",
        "landscape": "Beschreibe die Landschaft und Umgebung detailliert. Was koennen wir sehen, hoeren, riechen?",
        "fauna_flora": "Beschreibe Pflanzen und Tiere in unserer aktuellen Umgebung. Erfinde passende Namen fuer diese Welt.",
    }

    @staticmethod
    def generate_game_start_prompt(session: Session, world: World) -> str:
        """Generiert den Spielstart-Prompt mit allen relevanten Infos"""
        lines = [
            "=== SPIELSTART ===",
            f"Wir sind eine Gruppe aus {len(session.characters)} Spielern.",
            f"Wir spielen ein Pen & Paper Rollenspiel im Genre: {world.settings.genre}",
            f"Die Welt heisst: {world.settings.name}",
            ""
        ]

        if world.settings.description:
            lines.append(f"Weltbeschreibung: {world.settings.description}")
            lines.append("")

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

        active = [m for m in session.active_missions.values() if m.status == MissionStatus.ACTIVE]
        if active:
            lines.append("=== AKTIVE MISSIONEN ===")
            for mission in active:
                lines.append(f"- {mission.name}: {mission.objective}")
            lines.append("")

        if session.current_location_id and session.current_location_id in world.locations:
            loc = world.locations[session.current_location_id]
            lines.append("=== AKTUELLER ORT ===")
            lines.append(f"Ort: {loc.name}")
            if loc.description:
                lines.append(f"Beschreibung: {loc.description}")
            lines.append("")

        lines.append("=== SPIELMODUS ===")
        if session.is_round_based:
            lines.append("Rundenbasiert: Ja")
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

        if session.current_location_id and session.current_location_id in world.locations:
            loc = world.locations[session.current_location_id]
            lines.append(f"Ort: {loc.name}")

        lines.append("")
        lines.append(f"Auftrag: {template}")

        return "\n".join(lines)
