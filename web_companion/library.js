const EOCD_SIGNATURE = 0x06054b50;
const CENTRAL_DIRECTORY_SIGNATURE = 0x02014b50;
const LOCAL_FILE_SIGNATURE = 0x04034b50;

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

export async function loadBundleFromFile(file) {
  return loadBundleFromArrayBuffer(await file.arrayBuffer(), file.name);
}
