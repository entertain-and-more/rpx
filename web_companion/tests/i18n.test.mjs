import test from "node:test";
import assert from "node:assert/strict";
import {
  catalogs,
  getLocale,
  getDateLocale,
  setLocale,
  t,
  availableLocales,
} from "../i18n.mjs";

test("availableLocales contains de and en", () => {
  const locales = availableLocales();
  assert.ok(locales.includes("de"));
  assert.ok(locales.includes("en"));
});

test("de and en catalogs have 1:1 key parity", () => {
  const deKeys = Object.keys(catalogs.de).sort();
  const enKeys = Object.keys(catalogs.en).sort();
  assert.deepEqual(deKeys, enKeys, "DE and EN translation keys must match exactly");
});

test("setLocale switches active language and date locale", () => {
  setLocale("en");
  assert.equal(getLocale(), "en");
  assert.equal(getDateLocale(), "en-US");

  setLocale("de");
  assert.equal(getLocale(), "de");
  assert.equal(getDateLocale(), "de-DE");
});

test("t() translates keys and interpolates parameters", () => {
  setLocale("de");
  assert.equal(t("hero.title"), "RPX Pro Companion");
  assert.equal(t("status.loading", { name: "demo.zip" }), "Lade demo.zip …");

  setLocale("en");
  assert.equal(t("status.loading", { name: "demo.zip" }), "Loading demo.zip …");

  setLocale("de");
});

test("t() falls back gracefully for unknown keys", () => {
  assert.equal(t("non.existent.key"), "non.existent.key");
});
