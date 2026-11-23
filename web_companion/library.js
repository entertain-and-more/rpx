const EOCD_SIGNATURE = 0x06054b50;
const CENTRAL_DIRECTORY_SIGNATURE = 0x02014b50;
const LOCAL_FILE_SIGNATURE = 0x04034b50;

export const COMPANION_DELTA_FORMAT = "rpx-companion-delta-v1";
export const MAX_NOTE_LENGTH = 500;
export const MAX_PLAYER_NOTES = 50;

let noteIdCounter = 0;

function sliceView(buffer) {
  return buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
}

function decodeText(bytes) {
  return new TextDecoder("utf-8").decode(bytes);
}

function readJson(entries, path, fallback = null) {
  const entry = entries.get(path);
  if (!entry) {
    if (fallback !== null) {
      return fallback;
    }
    throw new Error(`Bundle-Datei fehlt: ${path}`);
  }
  return JSON.parse(decodeText(entry.data));
}

async function inflateRaw(bytes) {
  if (typeof DecompressionStream === "function") {
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("deflate-raw"));
    return new Uint8Array(await new Response(stream).arrayBuffer());
  }
  if (typeof process !== "undefined" && process.versions?.node) {
    const { inflateRawSync } = await import("node:zlib");
    const inflated = inflateRawSync(Buffer.from(bytes));
    return inflated.subarray(0, inflated.length);
  }
  throw new Error("Deflate-Entpacken wird in dieser Laufzeit nicht unterstützt.");
}

async function decompressEntry(method, data, uncompressedSize) {
  if (method === 0) {
    return data;
  }
  if (method === 8) {
    const inflated = await inflateRaw(data);
    if (uncompressedSize && inflated.length !== uncompressedSize) {
      throw new Error("ZIP-Eintrag hat eine unerwartete Größe nach dem Entpacken.");
    }
    return inflated;
  }
  throw new Error(`ZIP-Kompression ${method} wird nicht unterstützt.`);
}

export async function unzipEntries(arrayBuffer) {
  const bytes = sliceView(arrayBuffer);
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const minOffset = Math.max(0, bytes.length - 0xffff - 22);
  let eocdOffset = -1;

  for (let offset = bytes.length - 22; offset >= minOffset; offset -= 1) {
    if (view.getUint32(offset, true) === EOCD_SIGNATURE) {
      eocdOffset = offset;
      break;
    }
  }

  if (eocdOffset < 0) {
    throw new Error("Kein gültiges ZIP-Ende gefunden.");
  }

  const totalEntries = view.getUint16(eocdOffset + 10, true);
  const centralDirectoryOffset = view.getUint32(eocdOffset + 16, true);
  let cursor = centralDirectoryOffset;
  const entries = new Map();

  for (let index = 0; index < totalEntries; index += 1) {
    if (view.getUint32(cursor, true) !== CENTRAL_DIRECTORY_SIGNATURE) {
      throw new Error("Ungültiger ZIP-Central-Directory-Eintrag.");
    }

    const compressionMethod = view.getUint16(cursor + 10, true);
    const compressedSize = view.getUint32(cursor + 20, true);
    const uncompressedSize = view.getUint32(cursor + 24, true);
    const fileNameLength = view.getUint16(cursor + 28, true);
    const extraLength = view.getUint16(cursor + 30, true);
    const commentLength = view.getUint16(cursor + 32, true);
    const localHeaderOffset = view.getUint32(cursor + 42, true);
    const fileNameBytes = bytes.subarray(cursor + 46, cursor + 46 + fileNameLength);
    const fileName = decodeText(fileNameBytes);

    const localView = new DataView(bytes.buffer, bytes.byteOffset + localHeaderOffset);
    if (localView.getUint32(0, true) !== LOCAL_FILE_SIGNATURE) {
      throw new Error(`Lokaler Header für ${fileName} ist beschädigt.`);
    }

    const localNameLength = localView.getUint16(26, true);
    const localExtraLength = localView.getUint16(28, true);
    const dataStart = localHeaderOffset + 30 + localNameLength + localExtraLength;
    const compressedData = bytes.subarray(dataStart, dataStart + compressedSize);
    const data = await decompressEntry(compressionMethod, compressedData, uncompressedSize);

    entries.set(fileName, {
      path: fileName,
      compressionMethod,
      compressedSize,
      uncompressedSize,
      data,
    });

    cursor += 46 + fileNameLength + extraLength + commentLength;
  }

  return entries;
}

function collectWorlds(manifest, worldPayloads) {
  return manifest.worlds.map((entry) => {
    const payload = worldPayloads.get(entry.id) ?? {};
    const settings = payload.settings ?? {};
    const locations = Object.values(payload.locations ?? {});
    const maps = Object.values(payload.maps ?? {});
    return {
      id: entry.id,
      name: settings.name ?? entry.name ?? entry.id,
      genre: settings.genre ?? entry.genre ?? "Unbekannt",
      locationCount: locations.length,
      mapCount: maps.length,
      mapImage: payload.map_image ?? null,
      featuredLocations: locations.slice(0, 4).map((location) => location.name).filter(Boolean),
    };
  });
}

function collectSessions(manifest, sessionPayloads, worldsById) {
  return manifest.sessions.map((entry) => {
    const payload = sessionPayloads.get(entry.id) ?? {};
    const characters = Object.values(payload.characters ?? {}).map((character) => ({
      id: character.id,
      name: character.name ?? character.id ?? "Unbenannter Charakter",
      health: character.health ?? null,
      maxHealth: character.max_health ?? null,
      mana: character.mana ?? null,
      maxMana: character.max_mana ?? null,
      gold: character.gold ?? null,
      imagePath: character.image_path ?? null,
    }));
    const activeMissions = Object.values(payload.active_missions ?? {}).map((mission) => ({
      id: mission.id,
      name: mission.name ?? "Mission",
      objective: mission.objective ?? "",
      status: mission.status ?? "active",
    }));
    const chat = Array.isArray(payload.chat_history) ? payload.chat_history.slice(-5) : [];
    return {
      id: entry.id,
      name: payload.name ?? entry.name ?? entry.id,
      worldId: payload.world_id ?? entry.world_id ?? null,
      worldName: worldsById.get(payload.world_id ?? entry.world_id)?.name ?? "Unbekannte Welt",
      characters,
      activeMissions,
      completedMissionCount: Array.isArray(payload.completed_missions)
        ? payload.completed_missions.length
        : 0,
      chat,
    };
  });
}

function collectRulesets(manifest, rulesetPayloads) {
  return manifest.rulesets.map((entry) => {
    const payload = rulesetPayloads.get(entry.id) ?? rulesetPayloads.get(entry.file?.replace(/^rulesets\//, "").replace(/\.json$/u, "")) ?? {};
    return {
      id: entry.id,
      name: payload.ruleset_name ?? entry.name ?? entry.id,
      weaponCount: Array.isArray(payload.weapons) ? payload.weapons.length : 0,
      spellCount: Array.isArray(payload.spells) ? payload.spells.length : 0,
      file: entry.file ?? `${entry.id}.json`,
    };
  });
}

function summarizeBundle(worlds, sessions, mediaEntries, rulesets) {
  const characterCount = sessions.reduce((sum, session) => sum + session.characters.length, 0);
  const activeMissionCount = sessions.reduce((sum, session) => sum + session.activeMissions.length, 0);
  const completedMissionCount = sessions.reduce((sum, session) => sum + session.completedMissionCount, 0);

  return {
    worldCount: worlds.length,
    sessionCount: sessions.length,
    rulesetCount: rulesets.length,
    mediaCount: mediaEntries.length,
    characterCount,
    activeMissionCount,
    completedMissionCount,
  };
}

export async function loadBundleFromArrayBuffer(arrayBuffer, sourceName = "campaign.zip") {
  const entries = await unzipEntries(arrayBuffer);
  const manifest = readJson(entries, "manifest.json");
  if (manifest.format !== "rpx-campaign-bundle-v1") {
    throw new Error(`Unbekanntes Bundle-Format: ${manifest.format ?? "ohne Kennung"}`);
  }

  const worldPayloads = new Map(
    manifest.worlds.map((entry) => [entry.id, readJson(entries, entry.file)])
  );
  const sessionPayloads = new Map(
    manifest.sessions.map((entry) => [entry.id, readJson(entries, entry.file)])
  );
  const rulesetPayloads = new Map(
    manifest.rulesets.map((entry) => {
      const payload = readJson(entries, entry.file);
      return [entry.id, payload];
    })
  );

  const mediaEntries = entries.has("media/manifest.json")
    ? readJson(entries, "media/manifest.json", [])
    : Array.isArray(manifest.media)
      ? manifest.media
      : [];

  const worlds = collectWorlds(manifest, worldPayloads);
  const worldsById = new Map(worlds.map((world) => [world.id, world]));
  const sessions = collectSessions(manifest, sessionPayloads, worldsById);
  const rulesets = collectRulesets(manifest, rulesetPayloads);
  const summary = summarizeBundle(worlds, sessions, mediaEntries, rulesets);

  return {
    sourceName,
    manifest,
    worlds,
    sessions,
    rulesets,
    mediaEntries,
    summary,
  };
}

export function getCharacterList(bundle) {
  const list = [];
  for (const session of bundle.sessions) {
    for (const character of session.characters) {
      list.push({
        sessionId: session.id,
        sessionName: session.name,
        characterId: character.id,
        characterName: character.name,
        health: character.health,
        maxHealth: character.maxHealth,
        mana: character.mana,
        maxMana: character.maxMana,
        gold: character.gold,
      });
    }
  }
  return list;
}

export function getPlayerView(bundle, sessionId, characterId) {
  const session = bundle.sessions.find((s) => s.id === sessionId);
  if (!session) {
    throw new Error(`Session nicht gefunden: ${sessionId}`);
  }
  const character = session.characters.find((c) => c.id === characterId);
  if (!character) {
    throw new Error(`Charakter nicht gefunden: ${characterId}`);
  }
  return {
    character,
    activeMissions: session.activeMissions,
    chatExcerpt: session.chat,
  };
}

export async function loadBundleFromFile(file) {
  return loadBundleFromArrayBuffer(await file.arrayBuffer(), file.name);
}

// --- Companion Delta Return-Export Engine (rpx-companion-delta-v1) ---

export function clampCharacterStat(value, maxValue = null) {
  if (value === null || value === undefined || typeof value === "boolean") {
    throw new RangeError("Ungültiger numerischer Statuswert.");
  }
  if (typeof value === "string" && value.trim() === "") {
    throw new RangeError("Leerer numerischer Statuswert.");
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new RangeError("Nicht-endlicher numerischer Statuswert.");
  }
  let normalized = Math.max(0, Math.trunc(parsed));
  if (maxValue !== null && maxValue !== undefined && Number.isFinite(Number(maxValue)) && Number(maxValue) > 0) {
    normalized = Math.min(normalized, Math.trunc(Number(maxValue)));
  }
  return normalized;
}

export function createEmptyCompanionDelta(bundle = null) {
  return {
    version: 1,
    sourceName: bundle?.sourceName ?? null,
    bundleExportedAt: bundle?.manifest?.exported_at ?? null,
    characterPatches: {},
    playerNotes: [],
  };
}

function makePatchKey(sessionId, characterId) {
  return `${sessionId}::${characterId}`;
}

export function getEffectiveCharacter(bundle, deltaState, sessionId, characterId) {
  const { character } = getPlayerView(bundle, sessionId, characterId);
  const key = makePatchKey(sessionId, characterId);
  const patch = deltaState?.characterPatches?.[key] ?? null;
  if (!patch) {
    return { ...character, hasDelta: false };
  }
  return {
    ...character,
    health: patch.health ?? character.health,
    mana: patch.mana ?? character.mana,
    gold: patch.gold ?? character.gold,
    hasDelta: true,
  };
}

export function recordCharacterPatch(
  deltaState,
  bundle,
  sessionId,
  characterId,
  patch,
  updatedAt = Math.floor(Date.now() / 1000)
) {
  const { character } = getPlayerView(bundle, sessionId, characterId);
  const baseState = deltaState ?? createEmptyCompanionDelta(bundle);
  const key = makePatchKey(sessionId, characterId);
  const previous = baseState.characterPatches?.[key] ?? {};

  const nextHealth = patch.health !== undefined
    ? clampCharacterStat(patch.health, character.maxHealth)
    : (previous.health ?? character.health ?? 0);
  const nextMana = patch.mana !== undefined
    ? clampCharacterStat(patch.mana, character.maxMana)
    : (previous.mana ?? character.mana ?? 0);
  const nextGold = patch.gold !== undefined
    ? clampCharacterStat(patch.gold, null)
    : (previous.gold ?? character.gold ?? 0);

  const unchanged =
    nextHealth === (character.health ?? 0) &&
    nextMana === (character.mana ?? 0) &&
    nextGold === (character.gold ?? 0);

  const nextPatches = { ...(baseState.characterPatches ?? {}) };
  if (unchanged) {
    delete nextPatches[key];
  } else {
    nextPatches[key] = {
      sessionId,
      characterId,
      characterName: character.name,
      health: nextHealth,
      mana: nextMana,
      gold: nextGold,
      updatedAt: Math.trunc(Number(updatedAt) || 0),
    };
  }

  return {
    ...baseState,
    sourceName: bundle?.sourceName ?? baseState.sourceName ?? null,
    bundleExportedAt: bundle?.manifest?.exported_at ?? baseState.bundleExportedAt ?? null,
    characterPatches: nextPatches,
  };
}

export function addPlayerNote(
  deltaState,
  bundle,
  { sessionId, characterId = null, author = "", content = "" },
  createdAt = Math.floor(Date.now() / 1000)
) {
  const session = bundle?.sessions?.find((s) => s.id === sessionId);
  if (!session) {
    throw new Error(`Session nicht gefunden: ${sessionId}`);
  }
  let resolvedAuthor = String(author ?? "").trim();
  if (characterId) {
    const character = session.characters.find((c) => c.id === characterId);
    if (!character) {
      throw new Error(`Charakter nicht gefunden: ${characterId}`);
    }
    if (!resolvedAuthor) {
      resolvedAuthor = character.name;
    }
  }
  if (!resolvedAuthor) {
    resolvedAuthor = "Player";
  }
  resolvedAuthor = resolvedAuthor.slice(0, 80);

  const trimmedContent = String(content ?? "").trim().slice(0, MAX_NOTE_LENGTH);
  if (!trimmedContent) {
    throw new Error("Spielernotiz darf nicht leer sein.");
  }

  const baseState = deltaState ?? createEmptyCompanionDelta(bundle);
  const existingNotes = Array.isArray(baseState.playerNotes) ? baseState.playerNotes : [];
  const safeTs = Math.trunc(Number(createdAt) || Math.floor(Date.now() / 1000));
  const existingIds = new Set(existingNotes.map((n) => n.id));
  let noteId = "";
  do {
    noteIdCounter += 1;
    noteId = `note-${safeTs}-${noteIdCounter}-${sessionId}`;
  } while (existingIds.has(noteId));

  const nextNotes = [
    ...existingNotes,
    {
      id: noteId,
      sessionId,
      characterId: characterId || null,
      author: resolvedAuthor,
      content: trimmedContent,
      createdAt: safeTs,
    },
  ].slice(-MAX_PLAYER_NOTES);

  return {
    ...baseState,
    sourceName: bundle?.sourceName ?? baseState.sourceName ?? null,
    bundleExportedAt: bundle?.manifest?.exported_at ?? baseState.bundleExportedAt ?? null,
    playerNotes: nextNotes,
  };
}

export function removePlayerNote(deltaState, noteId) {
  if (!deltaState) {
    return createEmptyCompanionDelta();
  }
  return {
    ...deltaState,
    playerNotes: (deltaState.playerNotes ?? []).filter((note) => note.id !== noteId),
  };
}

export function countDeltaEntries(deltaState) {
  const patchCount = Object.keys(deltaState?.characterPatches ?? {}).length;
  const noteCount = Array.isArray(deltaState?.playerNotes) ? deltaState.playerNotes.length : 0;
  return {
    patchCount,
    noteCount,
    totalCount: patchCount + noteCount,
  };
}

export function buildCompanionDeltaPayload(
  bundle,
  deltaState,
  exportedAt = Math.floor(Date.now() / 1000)
) {
  const safeDelta = deltaState ?? createEmptyCompanionDelta(bundle);
  const patches = Object.values(safeDelta.characterPatches ?? {}).map((entry) => ({
    session_id: entry.sessionId,
    character_id: entry.characterId,
    character_name: entry.characterName,
    health: entry.health,
    mana: entry.mana,
    gold: entry.gold,
    updated_at: entry.updatedAt,
  }));
  const notes = (safeDelta.playerNotes ?? []).map((note) => ({
    id: note.id,
    session_id: note.sessionId,
    character_id: note.characterId ?? null,
    author: note.author,
    content: note.content,
    created_at: note.createdAt,
  }));

  return {
    format: COMPANION_DELTA_FORMAT,
    exported_at: Math.trunc(Number(exportedAt) || Math.floor(Date.now() / 1000)),
    source_bundle: {
      source_name: bundle?.sourceName ?? safeDelta.sourceName ?? "campaign.zip",
      bundle_exported_at: bundle?.manifest?.exported_at ?? safeDelta.bundleExportedAt ?? null,
      schema_version: bundle?.manifest?.app?.schema_version ?? "1.0",
    },
    character_patches: patches,
    player_notes: notes,
  };
}

export function parseCompanionDeltaJson(rawJson) {
  const payload = typeof rawJson === "string" ? JSON.parse(rawJson) : rawJson;
  if (!payload || typeof payload !== "object" || payload.format !== COMPANION_DELTA_FORMAT) {
    throw new Error(`Ungültiges Companion-Delta-Format: ${payload?.format ?? "ohne Kennung"}`);
  }
  const characterPatches = {};
  for (const item of Array.isArray(payload.character_patches) ? payload.character_patches : []) {
    if (!item || typeof item.session_id !== "string" || typeof item.character_id !== "string") {
      continue;
    }
    const key = makePatchKey(item.session_id, item.character_id);
    characterPatches[key] = {
      sessionId: item.session_id,
      characterId: item.character_id,
      characterName: String(item.character_name ?? item.character_id),
      health: clampCharacterStat(item.health ?? 0),
      mana: clampCharacterStat(item.mana ?? 0),
      gold: clampCharacterStat(item.gold ?? 0),
      updatedAt: Math.trunc(Number(item.updated_at) || 0),
    };
  }
  const playerNotes = [];
  for (const note of Array.isArray(payload.player_notes) ? payload.player_notes : []) {
    if (!note || typeof note.session_id !== "string" || typeof note.content !== "string") {
      continue;
    }
    const trimmed = note.content.trim().slice(0, MAX_NOTE_LENGTH);
    if (!trimmed) {
      continue;
    }
    playerNotes.push({
      id: String(note.id || `note-${playerNotes.length + 1}`),
      sessionId: note.session_id,
      characterId: typeof note.character_id === "string" ? note.character_id : null,
      author: String(note.author || "Player").slice(0, 80),
      content: trimmed,
      createdAt: Math.trunc(Number(note.created_at) || 0),
    });
  }
  return {
    version: 1,
    sourceName: payload.source_bundle?.source_name ?? null,
    bundleExportedAt: payload.source_bundle?.bundle_exported_at ?? null,
    characterPatches,
    playerNotes: playerNotes.slice(-MAX_PLAYER_NOTES),
  };
}
