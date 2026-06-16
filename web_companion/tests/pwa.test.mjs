import test from "node:test";
import assert from "node:assert/strict";
import { readFile, access } from "node:fs/promises";
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
  assert.doesNotMatch(html, /apple-mobile-web-app-capable/, "apple-mobile-web-app-capable gesetzt — deprecated iOS 11.3, soll nicht gesetzt sein");
  assert.match(html, /apple-mobile-web-app-title/);
  assert.match(html, /install-hints/);
});

test("Service Worker cached nur lokale Shell-Dateien", async () => {
  const sw = await readFile(resolve(baseDir, "sw.js"), "utf8");

  assert.match(sw, /CACHE_NAME = "rpx-companion-v4"/);
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

test("iOS PWA: apple-touch-icon-180.png existiert physisch", async () => {
  await assert.doesNotReject(
    access(resolve(baseDir, "icons", "apple-touch-icon-180.png")),
    "apple-touch-icon-180.png fehlt — iOS-Homescreen-Icon nicht generiert"
  );
});

test("iOS PWA: apple-touch-icon verweist auf 180px-Icon mit sizes=180x180", async () => {
  const html = await readFile(resolve(baseDir, "index.html"), "utf8");
  assert.match(
    html,
    /rel="apple-touch-icon" sizes="180x180" href="\.\/icons\/apple-touch-icon-180\.png"/,
    "apple-touch-icon muss sizes=\"180x180\" und apple-touch-icon-180.png haben"
  );
});

test("iOS PWA: apple-mobile-web-app-title gesetzt", async () => {
  const html = await readFile(resolve(baseDir, "index.html"), "utf8");
  assert.match(html, /name="apple-mobile-web-app-title"/, "apple-mobile-web-app-title fehlt");
});

test("iOS PWA: apple-mobile-web-app-status-bar-style gesetzt", async () => {
  const html = await readFile(resolve(baseDir, "index.html"), "utf8");
  assert.match(html, /name="apple-mobile-web-app-status-bar-style"/, "apple-mobile-web-app-status-bar-style fehlt");
});

test("iOS PWA: kein apple-mobile-web-app-capable (deprecated seit iOS 11.3)", async () => {
  const html = await readFile(resolve(baseDir, "index.html"), "utf8");
  assert.doesNotMatch(html, /apple-mobile-web-app-capable/, "apple-mobile-web-app-capable gesetzt — deprecated");
});

test("Service Worker cached apple-touch-icon-180.png", async () => {
  const sw = await readFile(resolve(baseDir, "sw.js"), "utf8");
  assert.match(sw, /apple-touch-icon-180\.png/, "apple-touch-icon-180.png fehlt im SW-Cache");
});
