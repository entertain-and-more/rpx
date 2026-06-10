import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const baseDir = resolve(import.meta.dirname, "..");

test("manifest beschreibt eine installierbare RPX-PWA", async () => {
  const manifest = JSON.parse(
    await readFile(resolve(baseDir, "manifest.webmanifest"), "utf8")
  );

  assert.equal(manifest.display, "standalone");
  assert.equal(manifest.lang, "de");
  assert.ok(manifest.name.includes("RPX"));
  assert.ok(Array.isArray(manifest.icons));
  assert.ok(manifest.icons.length >= 2);
});

test("HTML-Shell bietet lokalen ZIP-Import an", async () => {
  const html = await readFile(resolve(baseDir, "index.html"), "utf8");

  assert.match(html, /type="file"/);
  assert.match(html, /accept="\.zip,application\/zip"/);
  assert.match(html, /rpx-campaign-bundle-v1/);
  assert.match(html, /Kampagnenstand/);
});

test("Service Worker cached nur lokale Shell-Dateien", async () => {
  const sw = await readFile(resolve(baseDir, "sw.js"), "utf8");

  assert.match(sw, /CACHE_NAME = "rpx-companion-v2"/);
  assert.match(sw, /index\.html/);
  assert.doesNotMatch(sw, /https?:\/\//);
  assert.match(sw, /skipWaiting/, "skipWaiting fehlt — neue SW-Version wartet auf Tab-Schließung");
  assert.match(sw, /clients\.claim/, "clients.claim fehlt — bestehende Seiten nicht sofort kontrolliert");
  assert.match(sw, /ignoreSearch\s*:\s*true/, "ignoreSearch fehlt — Offline-Anfragen mit Query-Params verfehlen Cache");
});
