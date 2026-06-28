"""DataManager: Zentralisierte Datenverwaltung fuer alle Entitaeten."""

import json
import os
import time
import tempfile
import logging
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile
from typing import Dict, Optional, Any, Iterable, List, Tuple

from rpx_pro.constants import (
    generate_short_id, APP_TITLE, VERSION, SCHEMA_VERSION,
    CONFIG_FILE, PROJECT_ROOT, MEDIA_DIR, WORLDS_DIR, SESSIONS_DIR,
    BACKUPS_DIR, RULESETS_DIR,
)
from rpx_pro.models.world import World, WorldSettings
from rpx_pro.models.session import Session

logger = logging.getLogger("RPX")


def _atomic_write_json(path, obj) -> None:
    """Schreibt JSON atomar (tmp + os.replace im selben Verzeichnis): ein Crash oder
    OneDrive-Sync-Konflikt waehrend des Schreibens kann die bestehende Datei dann
    nicht mehr truncaten/korrumpieren -> Schutz von config/Welt/Spielstand. save_session
    laeuft bei nahezu jeder Spielaktion, das Crash-Fenster ist also real."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        os.replace(tmp, p)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


MEDIA_PATH_KEYS = {
    "ambient_sound",
    "background_image",
    "background_music",
    "entry_sound",
    "exit_sound",
    "exterior_image",
    "image_path",
    "interior_image",
    "map_image",
    "price_list_file",
    "sound_file",
}
MEDIA_LIST_KEYS = {"images"}
MEDIA_KIND_HINTS = {
    "ambient_sound": "sound",
    "background_image": "map",
    "background_music": "music",
    "entry_sound": "sound",
    "exit_sound": "sound",
    "exterior_image": "image",
    "image_path": "image",
    "images": "image",
    "interior_image": "image",
    "map_image": "map",
    "price_list_file": "document",
    "sound_file": "sound",
}
MEDIA_SUBDIRS = {
    "document": "misc",
    "image": "images",
    "map": "maps",
    "music": "music",
    "sound": "sounds",
}


class DataManager:
    """Zentralisierte Datenverwaltung fuer alle Entitaeten"""

    DEFAULT_CONFIG = {
        "last_world_id": None,
        "last_session_id": None,
        "music_volume": 0.5,
        "sound_volume": 0.7,
        "window_geometry": None,
        "player_screen_monitor": 1,
    }

    def __init__(self):
        self.worlds: Dict[str, World] = {}
        self.sessions: Dict[str, Session] = {}
        self.current_world: Optional[World] = None
        self.current_session: Optional[Session] = None
        self.config: Dict[str, Any] = dict(self.DEFAULT_CONFIG)
        self.load_warnings: List[str] = []
        self.load_config()
        self._load_all()

    def load_config(self):
        """Laedt die Konfigurationsdatei"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                self.config.update(saved)
                logger.info("Konfiguration geladen")
            except Exception as e:
                logger.error(f"Fehler beim Laden der Konfiguration: {e}")

    def save_config(self):
        """Speichert die Konfigurationsdatei"""
        try:
            if self.current_world:
                self.config["last_world_id"] = self.current_world.id
            if self.current_session:
                self.config["last_session_id"] = self.current_session.id
            _atomic_write_json(CONFIG_FILE, self.config)
            logger.info("Konfiguration gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")

    def _load_all(self):
        """Laedt alle gespeicherten Daten"""
        self._load_worlds()
        self._load_sessions()

    def _load_worlds(self):
        """Laedt alle Welten"""
        for path in WORLDS_DIR.glob("*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data.setdefault("id", path.stem)
                    world = World.from_dict(data)
                    self.worlds[world.id] = world
                    logger.info(f"Welt geladen: {world.settings.name}")
            except Exception as e:
                self._quarantine_load_failure(path, "world", e)

    def _load_sessions(self):
        """Laedt alle Sessions"""
        for path in SESSIONS_DIR.glob("*.json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data.setdefault("id", path.stem)
                    data.setdefault("name", path.stem)
                    session = Session.from_dict(data)
                    self.sessions[session.id] = session
                    logger.info(f"Session geladen: {session.name}")
            except Exception as e:
                self._quarantine_load_failure(path, "session", e)

    def _quarantine_load_failure(self, path: Path, label: str, error: Exception) -> None:
        """Verschiebt unladbare Savegame-Dateien aus dem aktiven Startpfad."""
        display_label = "Welt" if label == "world" else "Session"
        message = f"{display_label} konnte nicht geladen werden: {path.name} ({error})"
        quarantine_dir = BACKUPS_DIR / "quarantine"
        try:
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            target = quarantine_dir / f"{label}_{path.stem}_{int(time.time())}{path.suffix}"
            counter = 2
            while target.exists():
                target = quarantine_dir / f"{label}_{path.stem}_{int(time.time())}_{counter}{path.suffix}"
                counter += 1
            path.rename(target)
            message += f" -> verschoben nach {target}"
        except Exception as quarantine_error:
            message += f" -> Quarantäne fehlgeschlagen: {quarantine_error}"
        self.load_warnings.append(message)
        logger.error(message)

    def save_world(self, world: World) -> bool:
        """Speichert eine Welt"""
        try:
            path = WORLDS_DIR / f"{world.id}.json"
            _atomic_write_json(path, world.to_dict())
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
            _atomic_write_json(path, session.to_dict())
            self.sessions[session.id] = session
            logger.info(f"Session gespeichert: {session.name}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Session: {e}")
            return False

    def create_world(self, name: str, genre: str = "Fantasy") -> World:
        """Erstellt eine neue Welt"""
        world_id = generate_short_id()
        settings = WorldSettings(name=name, genre=genre)
        world = World(id=world_id, settings=settings)
        self.save_world(world)
        return world

    def create_session(self, world_id: str, name: str) -> Optional[Session]:
        """Erstellt eine neue Session"""
        if world_id not in self.worlds:
            logger.error(f"Welt {world_id} nicht gefunden")
            return None
        session_id = generate_short_id()
        session = Session(id=session_id, world_id=world_id, name=name)
        self.save_session(session)
        return session

    def delete_world(self, world_id: str) -> bool:
        """Loescht eine Welt (mit Backup)"""
        if world_id not in self.worlds:
            return False
        try:
            path = WORLDS_DIR / f"{world_id}.json"
            backup_path = BACKUPS_DIR / f"world_{world_id}_{int(time.time())}.json"
            if path.exists():
                path.rename(backup_path)
            del self.worlds[world_id]
            if self.current_world and self.current_world.id == world_id:
                self.current_world = None
            return True
        except Exception as e:
            logger.error(f"Fehler beim Loeschen: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """Loescht eine Session (mit Backup)"""
        if session_id not in self.sessions:
            return False
        try:
            path = SESSIONS_DIR / f"{session_id}.json"
            backup_path = BACKUPS_DIR / f"session_{session_id}_{int(time.time())}.json"
            if path.exists():
                path.rename(backup_path)
            del self.sessions[session_id]
            if self.current_session and self.current_session.id == session_id:
                self.current_session = None
            return True
        except Exception as e:
            logger.error(f"Fehler beim Loeschen: {e}")
            return False

    def export_campaign_bundle(
        self,
        destination: str | Path,
        world_ids: Optional[Iterable[str]] = None,
        session_ids: Optional[Iterable[str]] = None,
        include_media: str = "manifest",
    ) -> Dict[str, Any]:
        """Exportiert Welten, Sessions, Regelwerke und optional Medien als ZIP-Bundle."""
        include_media = include_media.lower()
        if include_media not in {"none", "manifest", "files"}:
            raise ValueError("include_media muss 'none', 'manifest' oder 'files' sein")

        selected_sessions = self._select_sessions(session_ids, world_ids)
        selected_worlds = self._select_worlds(world_ids, selected_sessions)
        world_payloads = {world.id: world.to_dict() for world in selected_worlds}
        session_payloads = {session.id: session.to_dict() for session in selected_sessions}
        ruleset_entries = self._load_ruleset_entries()

        media_entries = self._rewrite_media_paths(world_payloads, session_payloads, include_media)
        manifest = {
            "format": "rpx-campaign-bundle-v1",
            "exported_at": time.time(),
            "app": {
                "title": APP_TITLE,
                "version": VERSION,
                "schema_version": SCHEMA_VERSION,
            },
            "media_mode": include_media,
            "worlds": [
                {
                    "id": world.id,
                    "name": world.settings.name,
                    "genre": world.settings.genre,
                    "file": f"worlds/{world.id}.json",
                }
                for world in selected_worlds
            ],
            "sessions": [
                {
                    "id": session.id,
                    "world_id": session.world_id,
                    "name": session.name,
                    "file": f"sessions/{session.id}.json",
                }
                for session in selected_sessions
            ],
            "rulesets": [
                {
                    "id": entry["id"],
                    "name": entry["name"],
                    "file": entry["bundle_path"],
                }
                for entry in ruleset_entries
            ],
            "media": media_entries,
        }

        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.writestr("media/manifest.json", json.dumps(media_entries, ensure_ascii=False, indent=2))
            for world in selected_worlds:
                archive.writestr(
                    f"worlds/{world.id}.json",
                    json.dumps(world_payloads[world.id], ensure_ascii=False, indent=2),
                )
            for session in selected_sessions:
                archive.writestr(
                    f"sessions/{session.id}.json",
                    json.dumps(session_payloads[session.id], ensure_ascii=False, indent=2),
                )
            for entry in ruleset_entries:
                archive.writestr(entry["bundle_path"], json.dumps(entry["data"], ensure_ascii=False, indent=2))
            if include_media == "files":
                for entry in media_entries:
                    source_path = entry.get("source_path")
                    if source_path and entry.get("exists"):
                        archive.write(source_path, arcname=entry["bundle_path"])

        logger.info(
            "Campaign-Bundle exportiert: %s (%s Welten, %s Sessions, %s Medienreferenzen)",
            destination,
            len(selected_worlds),
            len(selected_sessions),
            len(media_entries),
        )
        return {
            "path": str(destination),
            "format": manifest["format"],
            "world_count": len(selected_worlds),
            "session_count": len(selected_sessions),
            "ruleset_count": len(ruleset_entries),
            "media_count": len(media_entries),
            "media_mode": include_media,
        }

    def import_campaign_bundle(
        self,
        source: str | Path,
        conflict_strategy: str = "rename",
    ) -> Dict[str, Any]:
        """Importiert ein Campaign-Bundle und normalisiert Medienpfade fuer den Desktop."""
        conflict_strategy = conflict_strategy.lower()
        if conflict_strategy not in {"rename", "replace", "skip"}:
            raise ValueError("conflict_strategy muss 'rename', 'replace' oder 'skip' sein")

        source = Path(source)
        if not source.exists():
            raise FileNotFoundError(f"Campaign-Bundle nicht gefunden: {source}")

        imported_worlds: List[Dict[str, str]] = []
        imported_sessions: List[Dict[str, str]] = []
        imported_rulesets: List[Dict[str, str]] = []
        media_cache: Dict[str, Path] = {}
        media_events: List[Dict[str, str]] = []

        with ZipFile(source, "r") as archive:
            manifest = self._load_bundle_manifest(archive)
            names = set(archive.namelist())
            world_id_map: Dict[str, str] = {}

            for entry in manifest.get("worlds", []):
                payload = self._load_bundle_json(archive, entry.get("file"), "Welt")
                original_id = str(payload.get("id") or entry.get("id") or "")
                if not original_id:
                    raise ValueError("Welt im Bundle ohne ID gefunden")

                target_id, action = self._resolve_entity_conflict(
                    original_id,
                    self.worlds,
                    conflict_strategy,
                )
                if action == "skipped":
                    world_id_map[original_id] = original_id
                    imported_worlds.append({"id": original_id, "action": action})
                    continue

                self._localize_bundle_media_paths(
                    payload,
                    archive,
                    names,
                    conflict_strategy,
                    media_cache,
                    media_events,
                )
                if target_id != original_id:
                    payload["id"] = target_id
                world = World.from_dict(payload)
                self.save_world(world)
                world_id_map[original_id] = world.id
                imported_worlds.append({"id": world.id, "action": action})

            for entry in manifest.get("sessions", []):
                payload = self._load_bundle_json(archive, entry.get("file"), "Session")
                original_id = str(payload.get("id") or entry.get("id") or "")
                if not original_id:
                    raise ValueError("Session im Bundle ohne ID gefunden")

                original_world_id = str(payload.get("world_id") or entry.get("world_id") or "")
                mapped_world_id = world_id_map.get(original_world_id, original_world_id)
                if mapped_world_id not in self.worlds:
                    raise ValueError(
                        f"Session {original_id} verweist auf unbekannte Welt {original_world_id}"
                    )

                target_id, action = self._resolve_entity_conflict(
                    original_id,
                    self.sessions,
                    conflict_strategy,
                )
                if action == "skipped":
                    imported_sessions.append({"id": original_id, "action": action})
                    continue

                self._localize_bundle_media_paths(
                    payload,
                    archive,
                    names,
                    conflict_strategy,
                    media_cache,
                    media_events,
                )
                payload["world_id"] = mapped_world_id
                if target_id != original_id:
                    payload["id"] = target_id
                session = Session.from_dict(payload)
                self.save_session(session)
                imported_sessions.append({"id": session.id, "action": action})

            for entry in manifest.get("rulesets", []):
                bundle_path = str(entry.get("file") or "")
                if not bundle_path:
                    raise ValueError("Regelwerk-Eintrag ohne Dateipfad gefunden")
                target_path, action = self._resolve_ruleset_target(bundle_path, conflict_strategy)
                if action == "skipped":
                    imported_rulesets.append({"file": target_path.name, "action": action})
                    continue

                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(archive.read(bundle_path))
                imported_rulesets.append({"file": target_path.name, "action": action})

        logger.info(
            "Campaign-Bundle importiert: %s (%s Welten, %s Sessions, %s Regelwerke, %s Medienpfade)",
            source,
            len([item for item in imported_worlds if item["action"] != "skipped"]),
            len([item for item in imported_sessions if item["action"] != "skipped"]),
            len([item for item in imported_rulesets if item["action"] != "skipped"]),
            len(media_cache),
        )
        return {
            "path": str(source),
            "format": "rpx-campaign-bundle-v1",
            "conflict_strategy": conflict_strategy,
            "worlds": imported_worlds,
            "sessions": imported_sessions,
            "rulesets": imported_rulesets,
            "media": media_events,
            "world_count": len([item for item in imported_worlds if item["action"] != "skipped"]),
            "session_count": len([item for item in imported_sessions if item["action"] != "skipped"]),
            "ruleset_count": len([item for item in imported_rulesets if item["action"] != "skipped"]),
            "media_count": len(media_cache),
        }

    def _select_sessions(
        self,
        session_ids: Optional[Iterable[str]],
        world_ids: Optional[Iterable[str]],
    ) -> List[Session]:
        if session_ids is not None:
            sessions = []
            for session_id in session_ids:
                if session_id not in self.sessions:
                    raise ValueError(f"Session {session_id} nicht gefunden")
                sessions.append(self.sessions[session_id])
            return sorted(sessions, key=lambda session: session.id)

        if world_ids is not None:
            selected_world_ids = set(world_ids)
            for world_id in selected_world_ids:
                if world_id not in self.worlds:
                    raise ValueError(f"Welt {world_id} nicht gefunden")
            sessions = [
                session
                for session in self.sessions.values()
                if session.world_id in selected_world_ids
            ]
            return sorted(sessions, key=lambda session: session.id)

        return sorted(self.sessions.values(), key=lambda session: session.id)

    def _select_worlds(
        self,
        world_ids: Optional[Iterable[str]],
        sessions: Iterable[Session],
    ) -> List[World]:
        selected_world_ids = set(world_ids or [])
        selected_world_ids.update(session.world_id for session in sessions)
        if not selected_world_ids:
            selected_world_ids = set(self.worlds.keys())
        worlds = []
        for world_id in sorted(selected_world_ids):
            if world_id not in self.worlds:
                raise ValueError(f"Welt {world_id} nicht gefunden")
            worlds.append(self.worlds[world_id])
        return worlds

    def _load_ruleset_entries(self) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        for ruleset_path in sorted(RULESETS_DIR.glob("*.json")):
            with open(ruleset_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            entries.append(
                {
                    "id": ruleset_path.stem,
                    "name": data.get("ruleset_name", ruleset_path.stem),
                    "bundle_path": f"rulesets/{ruleset_path.name}",
                    "data": data,
                }
            )
        return entries

    def _load_bundle_manifest(self, archive: ZipFile) -> Dict[str, Any]:
        if "manifest.json" not in archive.namelist():
            raise ValueError("Campaign-Bundle ohne manifest.json")
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        if manifest.get("format") != "rpx-campaign-bundle-v1":
            raise ValueError("Unbekanntes Campaign-Bundle-Format")
        return manifest

    def _load_bundle_json(self, archive: ZipFile, bundle_path: Any, label: str) -> Dict[str, Any]:
        if not bundle_path:
            raise ValueError(f"{label}-Eintrag ohne Dateipfad gefunden")
        return json.loads(archive.read(str(bundle_path)).decode("utf-8"))

    def _rewrite_media_paths(
        self,
        world_payloads: Dict[str, Dict[str, Any]],
        session_payloads: Dict[str, Dict[str, Any]],
        include_media: str,
    ) -> List[Dict[str, Any]]:
        media_entries: List[Dict[str, Any]] = []
        bundle_targets: Dict[str, str] = {}
        used_bundle_paths: set[str] = set()

        for payload in list(world_payloads.values()) + list(session_payloads.values()):
            for container, key, raw_value, media_kind in self._iter_media_refs(payload):
                bundle_path, source_path = self._map_media_path(
                    raw_value,
                    media_kind,
                    bundle_targets,
                    used_bundle_paths,
                )
                container[key] = bundle_path
                entry = next((item for item in media_entries if item["original_path"] == raw_value), None)
                if entry is None:
                    exists = bool(source_path and source_path.exists())
                    media_entries.append(
                        {
                            "original_path": raw_value,
                            "bundle_path": bundle_path,
                            "kind": media_kind,
                            "exists": exists,
                            "included": include_media == "files" and exists,
                            "source_path": str(source_path) if source_path else None,
                            "size_bytes": source_path.stat().st_size if exists else None,
                        }
                    )

        return sorted(media_entries, key=lambda entry: entry["bundle_path"])

    def _localize_bundle_media_paths(
        self,
        payload: Dict[str, Any],
        archive: ZipFile,
        archive_names: set[str],
        conflict_strategy: str,
        media_cache: Dict[str, Path],
        media_events: List[Dict[str, str]],
    ) -> None:
        for container, key, raw_value, media_kind in self._iter_media_refs(payload):
            archive_member = self._find_bundle_media_member(raw_value, media_kind, archive_names)
            cache_key = archive_member or self._normalize_bundle_media_path(raw_value, media_kind)
            localized_path = media_cache.get(cache_key)
            if localized_path is None:
                localized_path, action = self._prepare_import_media_target(
                    raw_value,
                    archive_member,
                    media_kind,
                    conflict_strategy,
                )
                if archive_member and action != "reused":
                    localized_path.parent.mkdir(parents=True, exist_ok=True)
                    localized_path.write_bytes(archive.read(archive_member))
                media_cache[cache_key] = localized_path
                media_events.append(
                    {
                        "source": raw_value,
                        "bundle_path": archive_member or cache_key,
                        "local_path": str(localized_path),
                        "action": action,
                    }
                )
            container[key] = str(localized_path)

    def _iter_media_refs(
        self,
        payload: Dict[str, Any],
    ) -> Iterable[Tuple[Dict[str, Any] | List[Any], str | int, str, str]]:
        stack: List[Any] = [payload]
        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                for key, value in current.items():
                    if key in MEDIA_PATH_KEYS and isinstance(value, str) and value.strip():
                        yield current, key, value, MEDIA_KIND_HINTS.get(key, "document")
                    elif key in MEDIA_LIST_KEYS and isinstance(value, list):
                        for index, item in enumerate(value):
                            if isinstance(item, str) and item.strip():
                                yield value, index, item, MEDIA_KIND_HINTS.get(key, "image")
                    elif isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(current, list):
                for item in current:
                    if isinstance(item, (dict, list)):
                        stack.append(item)

    def _map_media_path(
        self,
        raw_value: str,
        media_kind: str,
        bundle_targets: Dict[str, str],
        used_bundle_paths: set[str],
    ) -> Tuple[str, Optional[Path]]:
        normalized = raw_value.replace("\\", "/").strip()
        cached = bundle_targets.get(normalized)
        if cached:
            source = self._resolve_media_source(normalized)
            return cached, source

        source = self._resolve_media_source(normalized)
        bundle_path = self._build_bundle_media_path(normalized, source, media_kind)
        unique_bundle_path = bundle_path
        counter = 2
        while unique_bundle_path in used_bundle_paths:
            candidate = PurePosixPath(bundle_path)
            stem = Path(candidate.name).stem
            suffix = Path(candidate.name).suffix
            unique_bundle_path = str(candidate.with_name(f"{stem}-{counter}{suffix}"))
            counter += 1

        bundle_targets[normalized] = unique_bundle_path
        used_bundle_paths.add(unique_bundle_path)
        return unique_bundle_path, source

    def _find_bundle_media_member(
        self,
        raw_value: str,
        media_kind: str,
        archive_names: set[str],
    ) -> Optional[str]:
        for candidate in self._bundle_media_candidates(raw_value, media_kind):
            if candidate in archive_names:
                return candidate
        return None

    def _bundle_media_candidates(self, raw_value: str, media_kind: str) -> List[str]:
        normalized = raw_value.replace("\\", "/").strip()
        primary = self._normalize_bundle_media_path(normalized, media_kind)
        candidates: List[str] = []
        for candidate in (normalized, primary):
            if candidate and candidate not in candidates:
                candidates.append(candidate)

        primary_parts = list(PurePosixPath(primary).parts)
        if primary_parts[:1] == ["media"] and len(primary_parts) > 1:
            legacy = PurePosixPath(*primary_parts[1:]).as_posix()
            if legacy not in candidates:
                candidates.append(legacy)

        raw_parts = [part for part in PurePosixPath(normalized).parts if part not in {".", ""}]
        if raw_parts[:1] in (["images"], ["maps"], ["music"], ["sounds"]):
            media_prefixed = PurePosixPath("media", *raw_parts).as_posix()
            if media_prefixed not in candidates:
                candidates.append(media_prefixed)
        return candidates

    def _normalize_bundle_media_path(self, raw_value: str, media_kind: str) -> str:
        normalized = raw_value.replace("\\", "/").strip()
        raw_path = PurePosixPath(normalized)
        parts = [part for part in raw_path.parts if part not in {".", ""}]
        if parts and parts[0] == "media":
            return PurePosixPath(*parts).as_posix()
        if parts and parts[0] in {"images", "sounds", "music", "maps"}:
            return PurePosixPath("media", *parts).as_posix()

        filename = raw_path.name or f"{media_kind}-asset"
        category = MEDIA_SUBDIRS.get(media_kind, "misc")
        return PurePosixPath("media", category, filename).as_posix()

    def _prepare_import_media_target(
        self,
        raw_value: str,
        archive_member: Optional[str],
        media_kind: str,
        conflict_strategy: str,
    ) -> Tuple[Path, str]:
        bundle_path = archive_member or self._normalize_bundle_media_path(raw_value, media_kind)
        bundle_parts = [part for part in PurePosixPath(bundle_path).parts if part not in {".", ""}]
        if bundle_parts[:1] == ["media"]:
            relative_parts = bundle_parts[1:]
        else:
            relative_parts = bundle_parts
        if not relative_parts:
            filename = Path(raw_value).name or f"{media_kind}-asset"
            relative_parts = [MEDIA_SUBDIRS.get(media_kind, "misc"), filename]

        target_path = MEDIA_DIR / Path(*relative_parts)
        if not target_path.exists():
            return target_path, "created"
        if conflict_strategy == "replace":
            return target_path, "replaced"
        if conflict_strategy == "skip":
            return target_path, "reused"
        return self._unique_path(target_path), "renamed"

    def _resolve_entity_conflict(
        self,
        original_id: str,
        existing: Dict[str, Any],
        conflict_strategy: str,
    ) -> Tuple[str, str]:
        if original_id not in existing:
            return original_id, "created"
        if conflict_strategy == "replace":
            return original_id, "replaced"
        if conflict_strategy == "skip":
            return original_id, "skipped"

        candidate = generate_short_id()
        while candidate in existing:
            candidate = generate_short_id()
        return candidate, "renamed"

    def _resolve_ruleset_target(
        self,
        bundle_path: str,
        conflict_strategy: str,
    ) -> Tuple[Path, str]:
        target = RULESETS_DIR / Path(bundle_path).name
        if not target.exists():
            return target, "created"
        if conflict_strategy == "replace":
            return target, "replaced"
        if conflict_strategy == "skip":
            return target, "skipped"
        return self._unique_path(target), "renamed"

    def _unique_path(self, target: Path) -> Path:
        counter = 2
        candidate = target
        while candidate.exists():
            candidate = target.with_name(f"{target.stem}-{counter}{target.suffix}")
            counter += 1
        return candidate

    def _resolve_media_source(self, raw_value: str) -> Optional[Path]:
        candidate = Path(raw_value)
        candidates = []
        if candidate.is_absolute():
            candidates.append(candidate)
        else:
            candidates.extend(
                [
                    PROJECT_ROOT / raw_value,
                    MEDIA_DIR / raw_value,
                    Path(raw_value),
                ]
            )

        for path in candidates:
            if path.exists() and path.is_file():
                return path.resolve()
        return None

    def _build_bundle_media_path(
        self,
        raw_value: str,
        source_path: Optional[Path],
        media_kind: str,
    ) -> str:
        if source_path:
            try:
                rel = source_path.relative_to(MEDIA_DIR.resolve())
                return PurePosixPath("media", rel.as_posix()).as_posix()
            except ValueError:
                pass

        raw_path = PurePosixPath(raw_value)
        parts = [part for part in raw_path.parts if part not in {".", ""}]
        if parts and parts[0] == "media":
            normalized = PurePosixPath(*parts)
            return normalized.as_posix()
        if parts and parts[0] in {"images", "sounds", "music", "maps"}:
            return PurePosixPath("media", *parts).as_posix()

        filename = raw_path.name or f"{media_kind}-asset"
        category = MEDIA_SUBDIRS.get(media_kind, "misc")
        return PurePosixPath("media", category, filename).as_posix()
