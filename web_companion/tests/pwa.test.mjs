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
  assert.equal(manifest.id, "./");
  assert.equal(manifest.scope, "./");
  assert.equal(manifest.orientation, "portrait-primary");
  assert.ok(manifest.name.includes("RPX"));
  assert.ok(Array.isArray(manifest.display_override));
  assert.ok(manifest.display_override.includes("standalone"));
  assert.ok(Array.isArray(manifest.categories));
  assert.ok(manifest.categories.includes("games"));
  assert.ok(Array.isArray(manifest.icons));
  assert.ok(manifest.icons.length >= 2);
});

test("HTML-Shell bietet lokalen ZIP-Import an", async () => {
  const html = await readFile(resolve(baseDir, "index.html"), "utf8");

  assert.match(html, /type="file"/);
  assert.match(html, /accept="\.zip,application\/zip"/);
  assert.match(html, /rpx-campaign-bundle-v1/);
  assert.match(html, /Kampagnenstand/);
  assert.match(html, /viewport-fit=cover/);
  assert.match(html, /apple-mobile-web-app-capable/);
  assert.match(html, /apple-mobile-web-app-title/);
  assert.match(html, /install-hints/);
});

test("Service Worker cached nur lokale Shell-Dateien", async () => {
  const sw = await readFile(resolve(baseDir, "sw.js"), "utf8");

  assert.match(sw, /CACHE_NAME = "rpx-companion-v3"/);
  assert.match(sw, /index\.html/);
  assert.doesNotMatch(sw, /https?:\/\//);
  assert.match(sw, /skipWaiting/, "skipWaiting fehlt");
  assert.match(sw, /clients\.claim/, "clients.claim fehlt");
  assert.match(sw, /ignoreSearch\s*:\s*true/, "ignoreSearch fehlt");
});

test("App und Styles sichern Mobile-Restore und Safe-Area-Verhalten", async () => {
  const app = await readFile(resolve(baseDir, "app.js"), "utf8");
  const styles = await readFile(resolve(baseDir, "styles.css"), "utf8");

  assert.match(app, /rpx-companion:last-bundle:v1/);
  assert.match(app, /localStorage\.setItem/);
  assert.match(app, /restoreBundleSnapshot/);
  assert.match(app, /renderInstallHints/);
  assert.match(styles, /safe-area-inset-top/);
  assert.match(styles, /min-height:\s*44px/);
});
