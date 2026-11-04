import { test, describe } from "node:test";
import assert from "node:assert/strict";

import {
  SUPPORTED_LOCALES,
  DEFAULT_LOCALE,
  STORAGE_KEY,
  DATE_LOCALES,
  TRANSLATIONS,
  getLocale,
  setLocale,
  normalizeLocale,
  detectLocale,
  formatTimestamp,
  t,
  translateDocument,
} from "../i18n.js";

describe("RPX Pro Web-Companion i18n Contract (Tier-2 6-Languages)", () => {
  test("supported locales include de, en, es, zh, ja, ru with de as default", () => {
    assert.deepEqual(SUPPORTED_LOCALES, ["de", "en", "es", "zh", "ja", "ru"]);
    assert.equal(DEFAULT_LOCALE, "de");
    assert.equal(STORAGE_KEY, "rpx-companion:language");
  });

  test("translations dictionary contains all 64 required keys with 100% parity across all 6 languages", () => {
    const deKeys = Object.keys(TRANSLATIONS.de).sort();
    assert.equal(deKeys.length, 64, `DE should contain exactly 64 keys, found ${deKeys.length}`);

    for (const lang of ["en", "es", "zh", "ja", "ru"]) {
      const langKeys = Object.keys(TRANSLATIONS[lang]).sort();
      assert.deepEqual(langKeys, deKeys, `${lang.toUpperCase()} keys must be 100% identical to DE keys`);
    }
  });

  test("t() returns accurate translations for all 6 languages", () => {
    assert.equal(t("action_clear", {}, "de"), "Ansicht leeren");
    assert.equal(t("action_clear", {}, "en"), "Clear view");
    assert.equal(t("action_clear", {}, "es"), "Limpiar vista");
    assert.equal(t("action_clear", {}, "zh"), "清空视图");
    assert.equal(t("action_clear", {}, "ja"), "表示をクリア");
    assert.equal(t("action_clear", {}, "ru"), "Очистить");

    assert.equal(t("panel_worlds_title", {}, "de"), "Welten");
    assert.equal(t("panel_worlds_title", {}, "en"), "Worlds");
    assert.equal(t("panel_worlds_title", {}, "es"), "Mundos");
    assert.equal(t("panel_worlds_title", {}, "zh"), "游戏世界");
    assert.equal(t("panel_worlds_title", {}, "ja"), "ワールド");
    assert.equal(t("panel_worlds_title", {}, "ru"), "Миры");
  });

  test("t() interpolates parameters properly across languages", () => {
    const formattedDe = t("status_success", {
      name: "Campaign1",
      worlds: 3,
      sessions: 5,
    }, "de");
    assert.equal(formattedDe, "Campaign1 erfolgreich geladen (3 Welten, 5 Sessions).");

    const formattedEn = t("status_success", {
      name: "Campaign1",
      worlds: 3,
      sessions: 5,
    }, "en");
    assert.equal(formattedEn, "Campaign1 loaded successfully (3 worlds, 5 sessions).");

    const formattedZh = t("status_success", {
      name: "Campaign1",
      worlds: 3,
      sessions: 5,
    }, "zh");
    assert.equal(formattedZh, "成功加载 Campaign1（3 个世界，5 个会话）。");
  });

  test("fallback mechanism works correctly", () => {
    assert.equal(normalizeLocale("de-CH"), "de");
    assert.equal(normalizeLocale("en-GB"), "en");
    assert.equal(normalizeLocale("es-MX"), "es");
    assert.equal(normalizeLocale("zh-CN"), "zh");
    assert.equal(normalizeLocale("ja-JP"), "ja");
    assert.equal(normalizeLocale("ru-RU"), "ru");
    assert.equal(normalizeLocale("unknown-lang"), "de");
  });

  test("formatTimestamp respects locale", () => {
    const ts = 1700000000;
    const dateDe = formatTimestamp(ts, "de");
    const dateEn = formatTimestamp(ts, "en");
    assert.ok(dateDe.length > 5);
    assert.ok(dateEn.length > 5);
    assert.equal(formatTimestamp(NaN, "de"), "Unbekannt");
    assert.equal(formatTimestamp(NaN, "en"), "Unknown");
    assert.equal(formatTimestamp(NaN, "es"), "Desconocido");
    assert.equal(formatTimestamp(NaN, "zh"), "未知");
    assert.equal(formatTimestamp(NaN, "ja"), "不明");
    assert.equal(formatTimestamp(NaN, "ru"), "Неизвестно");
  });

  test("translateDocument updates mock DOM attributes", () => {
    const node1 = { dataset: { i18n: "action_clear" }, textContent: "old" };
    const node2 = { dataset: { i18n: "action_player_mode" }, textContent: "old" };
    const textNodes = [node1, node2];

    const mockDoc = {
      documentElement: { lang: "de" },
      querySelectorAll(selector) {
        if (selector === "[data-i18n]") return textNodes;
        if (selector === "[data-i18n-html]") return [];
        if (selector === "[data-i18n-placeholder]") return [];
        if (selector === "[data-i18n-aria-label]") return [];
        return [];
      },
    };

    translateDocument(mockDoc, "en");
    assert.equal(mockDoc.documentElement.lang, "en");
    assert.equal(node1.textContent, "Clear view");
    assert.equal(node2.textContent, "Player Mode");
  });
});
