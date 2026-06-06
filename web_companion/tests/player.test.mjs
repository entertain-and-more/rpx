import test from "node:test";
import assert from "node:assert/strict";
import { deflateRawSync } from "node:zlib";

import { loadBundleFromArrayBuffer, getCharacterList, getPlayerView } from "../library.js";

function buildZip(entries) {
  const localParts = [];
  const centralParts = [];
  let localOffset = 0;

  for (const entry of entries) {
    const fileName = Buffer.from(entry.path, "utf8");
    const raw = Buffer.from(
      typeof entry.content === "string" ? entry.content : JSON.stringify(entry.content),
      "utf8"
    );
    const compressed = deflateRawSync(raw);
    const localHeader = Buffer.alloc(30);
    localHeader.writeUInt32LE(0x04034b50, 0);
    localHeader.writeUInt16LE(20, 4);
    localHeader.writeUInt16LE(0, 6);
    localHeader.writeUInt16LE(8, 8);
    localHeader.writeUInt32LE(0, 10);
    localHeader.writeUInt32LE(0, 14);
    localHeader.writeUInt32LE(compressed.length, 18);
    localHeader.writeUInt32LE(raw.length, 22);
    localHeader.writeUInt16LE(fileName.length, 26);
    localHeader.writeUInt16LE(0, 28);

    localParts.push(localHeader, fileName, compressed);

    const centralHeader = Buffer.alloc(46);
    centralHeader.writeUInt32LE(0x02014b50, 0);
    centralHeader.writeUInt16LE(20, 4);
    centralHeader.writeUInt16LE(20, 6);
    centralHeader.writeUInt16LE(0, 8);
    centralHeader.writeUInt16LE(8, 10);
    centralHeader.writeUInt32LE(0, 12);
    centralHeader.writeUInt32LE(0, 16);
    centralHeader.writeUInt32LE(compressed.length, 20);
    centralHeader.writeUInt32LE(raw.length, 24);
    centralHeader.writeUInt16LE(fileName.length, 28);
    centralHeader.writeUInt16LE(0, 30);
    centralHeader.writeUInt16LE(0, 32);
    centralHeader.writeUInt16LE(0, 34);
    centralHeader.writeUInt16LE(0, 36);
    centralHeader.writeUInt32LE(0, 38);
    centralHeader.writeUInt32LE(localOffset, 42);
    centralParts.push(centralHeader, fileName);

    localOffset += localHeader.length + fileName.length + compressed.length;
  }

  const centralDirectory = Buffer.concat(centralParts);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(0, 4);
  end.writeUInt16LE(0, 6);
  end.writeUInt16LE(entries.length, 8);
  end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(centralDirectory.length, 12);
  end.writeUInt32LE(localOffset, 16);
  end.writeUInt16LE(0, 20);

  return Buffer.concat([...localParts, centralDirectory, end]);
}

function buildFixtureZip() {
  const manifest = {
    format: "rpx-campaign-bundle-v1",
    exported_at: 1779645600,
    app: { title: "RPX Pro", version: "1.0.0", schema_version: "1.0" },
    worlds: [{ id: "world-1", name: "Nordmark", genre: "Fantasy", file: "worlds/world-1.json" }],
    sessions: [{ id: "session-1", world_id: "world-1", name: "Kapitel Eins", file: "sessions/session-1.json" }],
    rulesets: [{ id: "basic", name: "Basisregeln", file: "rulesets/basic.json" }],
  };
  const world = { id: "world-1", settings: { name: "Nordmark", genre: "Fantasy" }, locations: {}, maps: {} };
  const session = {
    id: "session-1",
    world_id: "world-1",
    name: "Kapitel Eins",
    characters: {
      ayla: { id: "ayla", name: "Ayla", health: 19, max_health: 24, mana: 7, max_mana: 11, gold: 42, image_path: null },
    },
    active_missions: {
      quest1: { id: "quest1", name: "Das verschwundene Siegel", objective: "Finde das Siegel", status: "active" },
    },
    completed_missions: [],
    chat_history: [
      { role: "gm", author: "Leitung", content: "Ihr hört Donner über der Stadt." },
      { role: "player", author: "Ayla", content: "Ich prüfe das Stadttor." },
    ],
  };
  return buildZip([
    { path: "manifest.json", content: manifest },
    { path: "worlds/world-1.json", content: world },
    { path: "sessions/session-1.json", content: session },
    { path: "rulesets/basic.json", content: { ruleset_name: "Basisregeln", weapons: [], spells: [] } },
  ]);
}

// --- getCharacterList ---

test("getCharacterList gibt flache Liste aller Charaktere zurück", async () => {
  const bundle = await loadBundleFromArrayBuffer(buildFixtureZip(), "demo.zip");
  const list = getCharacterList(bundle);

  assert.equal(list.length, 1);
  assert.equal(list[0].characterName, "Ayla");
  assert.equal(list[0].sessionId, "session-1");
  assert.equal(list[0].sessionName, "Kapitel Eins");
  assert.equal(list[0].health, 19);
  assert.equal(list[0].maxHealth, 24);
  assert.equal(list[0].gold, 42);
});

test("getCharacterList gibt leere Liste zurück wenn keine Sessions", async () => {
  const bundle = await loadBundleFromArrayBuffer(buildFixtureZip(), "demo.zip");
  const emptyBundle = { ...bundle, sessions: [] };
  const list = getCharacterList(emptyBundle);

  assert.deepEqual(list, []);
});

// --- getPlayerView ---

test("getPlayerView gibt Charakter + Missionen + Chat zurück", async () => {
  const bundle = await loadBundleFromArrayBuffer(buildFixtureZip(), "demo.zip");
  const view = getPlayerView(bundle, "session-1", "ayla");

  assert.equal(view.character.name, "Ayla");
  assert.equal(view.character.health, 19);
  assert.equal(view.activeMissions.length, 1);
  assert.equal(view.activeMissions[0].name, "Das verschwundene Siegel");
  assert.equal(view.chatExcerpt.length, 2);
});

test("getPlayerView wirft bei unbekannter Session", async () => {
  const bundle = await loadBundleFromArrayBuffer(buildFixtureZip(), "demo.zip");

  assert.throws(
    () => getPlayerView(bundle, "nonexistent", "ayla"),
    /Session nicht gefunden/
  );
});

test("getPlayerView wirft bei unbekanntem Charakter", async () => {
  const bundle = await loadBundleFromArrayBuffer(buildFixtureZip(), "demo.zip");

  assert.throws(
    () => getPlayerView(bundle, "session-1", "nonexistent"),
    /Charakter nicht gefunden/
  );
});
