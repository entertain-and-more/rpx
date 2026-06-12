from __future__ import annotations

import importlib
import json
import math
import os
import struct
import sys
import tempfile
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_SCALE_FACTOR", "1")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen
from PySide6.QtWidgets import QApplication


SCREENSHOT_FILES = {
    "main": "main-window.png",
    "world": "world-map.png",
    "player": "player-screen.png",
    "soundboard": "soundboard.png",
    "prompts": "ai-prompts.png",
}
SUMMARY_FILE = "summary.json"


@dataclass
class RuntimeModules:
    constants: Any
    DataManager: Any
    RPXProMainWindow: Any
    Character: Any
    GameMap: Any
    Item: Any
    ChatMessage: Any
    Mission: Any
    Location: Any
    MessageRole: Any
    MissionStatus: Any
    PlayerScreen: Any
    PlayerScreenMode: Any


@dataclass
class DemoContext:
    world_id: str
    session_id: str
    map_path: Path
    location_image: Path


def _process_events(app: QApplication, duration: float = 0.08) -> None:
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)


def _configure_runtime_paths(constants: Any, runtime_root: Path) -> None:
    data_root = runtime_root / "rpx_pro_data"
    rulesets_dir = runtime_root / "rulesets"
    path_updates = {
        "PROJECT_ROOT": data_root,
        "WORLDS_DIR": data_root / "worlds",
        "SESSIONS_DIR": data_root / "sessions",
        "CHARACTERS_DIR": data_root / "characters",
        "ITEMS_DIR": data_root / "items",
        "WEAPONS_DIR": data_root / "weapons",
        "ARMOR_DIR": data_root / "armor",
        "SPELLS_DIR": data_root / "spells",
        "VEHICLES_DIR": data_root / "vehicles",
        "MEDIA_DIR": data_root / "media",
        "SOUNDS_DIR": data_root / "media" / "sounds",
        "IMAGES_DIR": data_root / "media" / "images",
        "MUSIC_DIR": data_root / "media" / "music",
        "MAPS_DIR": data_root / "media" / "maps",
        "BACKUPS_DIR": data_root / "backups",
        "CONFIG_FILE": data_root / "config.json",
        "LOG_FILE": data_root / "rpx_pro.log",
        "RULESETS_DIR": rulesets_dir,
    }
    for name, value in path_updates.items():
        setattr(constants, name, value)
    constants.ALL_DIRS = [
        constants.PROJECT_ROOT,
        constants.WORLDS_DIR,
        constants.SESSIONS_DIR,
        constants.CHARACTERS_DIR,
        constants.ITEMS_DIR,
        constants.WEAPONS_DIR,
        constants.ARMOR_DIR,
        constants.SPELLS_DIR,
        constants.VEHICLES_DIR,
        constants.MEDIA_DIR,
        constants.SOUNDS_DIR,
        constants.IMAGES_DIR,
        constants.MUSIC_DIR,
        constants.MAPS_DIR,
        constants.BACKUPS_DIR,
    ]


def _load_runtime_modules(runtime_root: Path) -> RuntimeModules:
    import rpx_pro.constants as constants

    _configure_runtime_paths(constants, runtime_root)

    reload_order = [
        "rpx_pro.managers.data_manager",
        "rpx_pro.widgets.soundboard",
        "rpx_pro.widgets.prompt_widget",
        "rpx_pro.tabs.world_tab",
        "rpx_pro.tabs.views_tab",
        "rpx_pro.widgets.player_screen",
        "rpx_pro.main_window",
    ]
    for module_name in reload_order:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

    from rpx_pro.managers.data_manager import DataManager
    from rpx_pro.main_window import RPXProMainWindow
    from rpx_pro.models.entities import Character, GameMap, Item
    from rpx_pro.models.enums import MessageRole, MissionStatus, PlayerScreenMode
    from rpx_pro.models.session import ChatMessage, Mission
    from rpx_pro.models.world import Location
    from rpx_pro.widgets.player_screen import PlayerScreen

    return RuntimeModules(
        constants=constants,
        DataManager=DataManager,
        RPXProMainWindow=RPXProMainWindow,
        Character=Character,
        GameMap=GameMap,
        Item=Item,
        ChatMessage=ChatMessage,
        Mission=Mission,
        Location=Location,
        MessageRole=MessageRole,
        MissionStatus=MissionStatus,
        PlayerScreen=PlayerScreen,
        PlayerScreenMode=PlayerScreenMode,
    )


def _create_map_image(path: Path) -> None:
    width, height = 1600, 960
    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(QColor("#e5d7b6"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.fillRect(0, 0, width, height, QColor("#d9c89a"))
    painter.setPen(QPen(QColor("#8b6f47"), 5))
    painter.setBrush(QColor("#8fbf8f"))
    painter.drawEllipse(140, 120, 340, 220)
    painter.setBrush(QColor("#7ea3d8"))
    painter.drawEllipse(1050, 120, 320, 200)
    painter.setBrush(QColor("#c58d5d"))
    painter.drawRoundedRect(560, 180, 360, 190, 24, 24)
    painter.setBrush(QColor("#5a6e9b"))
    painter.drawRoundedRect(620, 520, 420, 220, 24, 24)

    road_pen = QPen(QColor("#5c3b20"), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(road_pen)
    painter.drawLine(320, 250, 735, 275)
    painter.drawLine(735, 275, 820, 620)
    painter.drawLine(820, 620, 1210, 220)

    painter.setPen(QColor("#1f2937"))
    painter.setFont(QFont("Georgia", 26, QFont.Weight.Bold))
    painter.drawText(180, 220, "Schattenforst")
    painter.drawText(1080, 210, "Silbersee")
    painter.drawText(610, 290, "Glasfurt")
    painter.drawText(720, 650, "Dornwacht")

    painter.setBrush(QColor("#c2410c"))
    painter.setPen(QPen(QColor("white"), 4))
    for x, y in ((735, 275), (820, 620), (1210, 220)):
        painter.drawEllipse(x - 14, y - 14, 28, 28)

    painter.end()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(path)):
        raise RuntimeError(f"Kartenbild konnte nicht gespeichert werden: {path}")


def _create_portrait_image(path: Path, label: str, accent: QColor) -> None:
    image = QImage(320, 320, QImage.Format_ARGB32)
    image.fill(QColor("#111827"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setBrush(accent)
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(48, 36, 224, 224)
    painter.setBrush(QColor("#f8fafc"))
    painter.drawEllipse(96, 88, 128, 128)
    painter.setBrush(QColor("#0f172a"))
    painter.drawEllipse(122, 122, 18, 18)
    painter.drawEllipse(180, 122, 18, 18)
    painter.drawRoundedRect(136, 170, 52, 12, 6, 6)

    painter.setPen(QColor("white"))
    painter.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
    painter.drawText(64, 290, label)
    painter.end()

    path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(path)):
        raise RuntimeError(f"Porträt konnte nicht gespeichert werden: {path}")


def _create_location_image(path: Path, title: str) -> None:
    image = QImage(1440, 900, QImage.Format_ARGB32)
    image.fill(QColor("#0f172a"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.fillRect(0, 0, 1440, 900, QColor("#111827"))
    painter.fillRect(0, 520, 1440, 380, QColor("#1f2937"))
    painter.setBrush(QColor("#b45309"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(240, 220, 960, 420, 28, 28)
    painter.setBrush(QColor("#78350f"))
    painter.drawRoundedRect(300, 280, 260, 240, 18, 18)
    painter.drawRoundedRect(880, 280, 260, 240, 18, 18)
    painter.setBrush(QColor("#fbbf24"))
    painter.drawEllipse(640, 330, 160, 160)

    painter.setPen(QColor("white"))
    painter.setFont(QFont("Georgia", 34, QFont.Weight.Bold))
    painter.drawText(70, 92, title)
    painter.setFont(QFont("Segoe UI", 16))
    painter.drawText(70, 132, "Spieleransicht mit Ortsbild für den zweiten Monitor")
    painter.end()

    path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(path)):
        raise RuntimeError(f"Ortsbild konnte nicht gespeichert werden: {path}")


def _create_sound_file(path: Path, frequency: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 22050
    frame_count = int(sample_rate * 0.25)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        frames = bytearray()
        for index in range(frame_count):
            sample = int(16000 * math.sin(2 * math.pi * frequency * (index / sample_rate)))
            frames.extend(struct.pack("<h", sample))
        handle.writeframes(frames)


def _seed_demo_state(app: QApplication, modules: RuntimeModules) -> DemoContext:
    const = modules.constants
    const.ensure_directories()
    const.RULESETS_DIR.mkdir(parents=True, exist_ok=True)

    map_path = const.MAPS_DIR / "auroria-map.png"
    tavern_path = const.IMAGES_DIR / "whispering-tavern.png"
    ayla_path = const.IMAGES_DIR / "ayla.png"
    bran_path = const.IMAGES_DIR / "bran.png"

    _create_map_image(map_path)
    _create_location_image(tavern_path, "Die Flüsternde Taverne")
    _create_portrait_image(ayla_path, "Ayla", QColor("#22c55e"))
    _create_portrait_image(bran_path, "Bran", QColor("#38bdf8"))
    _create_sound_file(const.SOUNDS_DIR / "thunder.wav", 180.0)
    _create_sound_file(const.SOUNDS_DIR / "portal.wav", 320.0)
    _create_sound_file(const.SOUNDS_DIR / "campfire.wav", 120.0)
    _create_sound_file(const.MUSIC_DIR / "tavern_theme.wav", 220.0)

    (const.RULESETS_DIR / "auroria.json").write_text(
        json.dumps(
            {
                "ruleset_name": "Auroria Demo",
                "weapons": [{"name": "Sternenklinge"}],
                "armor": [{"name": "Nebelmantel"}],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    dm = modules.DataManager()
    world = dm.create_world("Auroria", "Mystic Fantasy")
    world.settings.description = "Offline-Kampagne für Store-Screenshots mit Weltenkarte, Taverne und Frostturm."
    world.settings.simulate_disasters = True
    world.typical_items["starlantern"] = modules.Item(
        id="starlantern",
        name="Sternenlaterne",
        item_class="Artefakt",
        weight=1.2,
        value=45,
    )
    world.typical_items["healing_tea"] = modules.Item(
        id="healing_tea",
        name="Heiltee",
        item_class="Verbrauchsgut",
        weight=0.2,
        value=8,
    )
    world.maps["map-auroria"] = modules.GameMap(
        id="map-auroria",
        name="Weltkarte",
        background_image=str(map_path),
        character_positions={"char-ayla": (710, 290), "char-bran": (845, 610)},
    )
    world.active_map_id = "map-auroria"
    world.map_image = str(map_path)
    world.locations["loc-tavern"] = modules.Location(
        id="loc-tavern",
        name="Glasfurt Taverne",
        description="Zentrale Raststätte mit Gerüchten und Versorgungsständen.",
        exterior_image=str(tavern_path),
        background_music=str(const.MUSIC_DIR / "tavern_theme.wav"),
        map_position=(735, 275),
        location_type="building",
        has_interior=True,
    )
    world.locations["loc-keep"] = modules.Location(
        id="loc-keep",
        name="Dornwacht",
        description="Grenzfestung mit Blick auf den Silbersee.",
        exterior_image=str(tavern_path),
        map_position=(820, 620),
        location_type="city",
    )
    dm.save_world(world)

    session = dm.create_session(world.id, "Die Nebel von Glasfurt")
    session.characters["char-ayla"] = modules.Character(
        id="char-ayla",
        name="Ayla Nebelspur",
        race="Waldläuferin",
        profession="Späherin",
        health=34,
        max_health=40,
        mana=12,
        max_mana=18,
        inventory={"starlantern": 1, "healing_tea": 2},
        gold=37,
        image_path=str(ayla_path),
    )
    session.characters["char-bran"] = modules.Character(
        id="char-bran",
        name="Bran Silberfels",
        race="Wächter",
        profession="Schildträger",
        health=46,
        max_health=52,
        mana=4,
        max_mana=10,
        inventory={"healing_tea": 1},
        gold=21,
        image_path=str(bran_path),
    )
    session.active_missions["mission-bridge"] = modules.Mission(
        id="mission-bridge",
        name="Die Brücke aus Mondglas",
        description="Sichere den Übergang nach Dornwacht.",
        objective="Drei Runensiegel aktivieren, bevor der Nebel dichter wird.",
        status=modules.MissionStatus.ACTIVE,
        reward_gold=120,
    )
    session.active_missions["mission-scout"] = modules.Mission(
        id="mission-scout",
        name="Spuren im Schattenforst",
        description="Untersuche verschwundene Händler.",
        objective="Sammle Hinweise am Waldrand und befrage die Taverne.",
        status=modules.MissionStatus.ACTIVE,
        reward_gold=60,
    )
    session.chat_history.extend(
        [
            modules.ChatMessage(
                role=modules.MessageRole.GM,
                author="GM",
                content="Der Sturm zieht über Auroria auf. Glasfurt bereitet die Tore vor.",
            ),
            modules.ChatMessage(
                role=modules.MessageRole.PLAYER,
                author="Ayla",
                content="Ich prüfe die Mondglas-Brücke und halte nach Sabotagezeichen Ausschau.",
            ),
            modules.ChatMessage(
                role=modules.MessageRole.SYSTEM,
                author="System",
                content="Mission aktualisiert: Die Brücke aus Mondglas",
            ),
        ]
    )
    session.is_round_based = True
    session.turn_order = ["char-ayla", "char-bran"]
    session.current_turn_index = 0
    session.current_round = 3
    session.actions_per_turn = 2
    session.current_location_id = "loc-tavern"
    dm.save_session(session)

    dm.current_world = world
    dm.current_session = session
    dm.config["last_world_id"] = world.id
    dm.config["last_session_id"] = session.id
    dm.save_config()

    _process_events(app, 0.05)
    return DemoContext(
        world_id=world.id,
        session_id=session.id,
        map_path=map_path,
        location_image=tavern_path,
    )


def _save_widget(widget: Any, target: Path, app: QApplication) -> None:
    widget.show()
    widget.raise_()
    widget.activateWindow()
    _process_events(app, 0.16)
    pixmap = widget.grab()
    if pixmap.isNull():
        raise RuntimeError(f"Screenshot konnte nicht erzeugt werden: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not pixmap.save(str(target), "PNG"):
        raise RuntimeError(f"Screenshot konnte nicht gespeichert werden: {target}")


def _prime_turn_panel(window: Any) -> None:
    session = window.data_manager.current_session
    if not session:
        return
    window.turn_order_list.clear()
    for cid in session.turn_order:
        if cid in session.characters:
            window.turn_order_list.addItem(session.characters[cid].name)
    if session.turn_order and session.turn_order[session.current_turn_index] in session.characters:
        current = session.characters[session.turn_order[session.current_turn_index]].name
        window.current_turn_label.setText(f"Aktuell: {current}")
        window.turn_order_list.setCurrentRow(session.current_turn_index)
    window.round_label.setText(f"Runde: {session.current_round}")
    window.actions_label.setText(f"Aktionen: {session.actions_per_turn}/Runde")


def _capture_main_window(window: Any, output_dir: Path, app: QApplication) -> list[Path]:
    outputs: list[Path] = []

    window.tabs.setCurrentWidget(window.chat_widget)
    _prime_turn_panel(window)
    window.statusBar().showMessage("GM-Zentrale mit Chat, Rundensteuerung und Kampagnendaten", 0)
    main_target = output_dir / SCREENSHOT_FILES["main"]
    _save_widget(window, main_target, app)
    outputs.append(main_target)

    window.tabs.setCurrentWidget(window.world_tab)
    window.world_tab.refresh_world_map()
    if window.world_tab.locations_tree.topLevelItemCount() > 0:
        window.world_tab.locations_tree.setCurrentItem(window.world_tab.locations_tree.topLevelItem(0))
    window.statusBar().showMessage("Weltkarte mit Orten, Mehrkarten-Support und Session-Positionen", 0)
    world_target = output_dir / SCREENSHOT_FILES["world"]
    _save_widget(window, world_target, app)
    outputs.append(world_target)

    window.tabs.setCurrentWidget(window.immersion_tab)
    window.statusBar().showMessage("Soundboard mit lokalen Effekten für den Spieltisch", 0)
    soundboard_target = output_dir / SCREENSHOT_FILES["soundboard"]
    _save_widget(window, soundboard_target, app)
    outputs.append(soundboard_target)

    window.tabs.setCurrentWidget(window.prompt_widget)
    if window.prompt_widget.character_combo.count() > 0:
        window.prompt_widget.character_combo.setCurrentIndex(0)
    window.prompt_widget.generate_role_prompt("storyteller")
    window.statusBar().showMessage("KI-Promptgenerator für Story, Gegner und Szenenwechsel", 0)
    prompts_target = output_dir / SCREENSHOT_FILES["prompts"]
    _save_widget(window, prompts_target, app)
    outputs.append(prompts_target)

    return outputs


def _build_inventory_preview(session: Any, world: Any, character_id: str) -> dict[str, Any]:
    character = session.characters[character_id]
    items = []
    for item_id, quantity in character.inventory.items():
        item = world.typical_items.get(item_id)
        items.append({"name": item.name if item else item_id, "quantity": quantity})
    return {"items": items}


def _capture_player_screen(
    modules: RuntimeModules,
    window: Any,
    context: DemoContext,
    output_dir: Path,
    app: QApplication,
) -> Path:
    session = window.data_manager.current_session
    world = window.data_manager.current_world
    if not session or not world:
        raise RuntimeError("Demo-Session konnte nicht geladen werden")

    player_screen = modules.PlayerScreen()
    player_screen.resize(1600, 960)
    player_screen.set_background_image(str(context.location_image))
    player_screen.update_characters(window._collect_player_chars(session))
    player_screen.update_missions(
        [{"name": mission.name, "status": mission.status.value} for mission in session.active_missions.values()]
    )
    player_screen.update_chat(
        [
            f"<span style='color:#f1c40f;'><b>{message.author}:</b> {message.content}</span>"
            if message.role == modules.MessageRole.GM
            else f"<span style='color:#d1d5db;'><b>{message.author}:</b> {message.content}</span>"
            for message in session.chat_history
        ]
    )
    player_screen.update_turn_info(
        "Ayla Nebelspur",
        session.current_round,
        [session.characters[cid].name for cid in session.turn_order if cid in session.characters],
    )
    player_screen.update_inventory(_build_inventory_preview(session, world, "char-ayla"))
    player_screen.location_label.setText("Ort: Glasfurt Taverne")
    player_screen.update_weather("storm")
    player_screen.update_time("evening")
    player_screen.set_mode(modules.PlayerScreenMode.TILES)
    player_screen.set_enabled_views(
        {
            "characters": True,
            "missions": True,
            "chat": True,
            "turns": True,
            "inventory": True,
            "map": False,
            "location": False,
        }
    )

    player_target = output_dir / SCREENSHOT_FILES["player"]
    _save_widget(player_screen, player_target, app)
    player_screen.close()
    _process_events(app, 0.05)
    return player_target


def _write_summary(output_dir: Path, files: list[Path]) -> dict[str, Any]:
    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": [{"name": path.name, "path": str(path.resolve())} for path in files],
    }
    (output_dir / SUMMARY_FILE).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def generate_store_screenshots(output_dir: str | Path) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("RPX Pro Store Screenshots")

    with tempfile.TemporaryDirectory(prefix="rpx-store-shots-") as runtime:
        modules = _load_runtime_modules(Path(runtime))
        context = _seed_demo_state(app, modules)

        window = modules.RPXProMainWindow()
        window.resize(1600, 960)
        window.light_manager.effect_started.connect(window._mirror_effect_to_player)
        _process_events(app, 0.12)

        generated = _capture_main_window(window, output_dir, app)
        generated.append(_capture_player_screen(modules, window, context, output_dir, app))

        window.close()
        _process_events(app, 0.05)

    return _write_summary(output_dir, generated)


def main() -> int:
    output_dir = PROJECT_ROOT / "README" / "screenshots" / "store"
    summary = generate_store_screenshots(output_dir)
    print("Store-Screenshots erfolgreich erzeugt.")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
