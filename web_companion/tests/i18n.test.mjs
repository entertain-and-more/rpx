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

  test("translations dictionary contains all 92 required keys with 100% parity across all 6 languages", () => {
    const deKeys = Object.keys(TRANSLATIONS.de).sort();
    assert.equal(deKeys.length, 92, `DE should contain exactly 92 keys, found ${deKeys.length}`);

    for (const lang of ["en", "es", "zh", "ja", "ru"]) {
      const langKeys = Object.keys(TRANSLATIONS[lang]).sort();
      assert.deepEqual(langKeys, deKeys, `${lang.toUpperCase()} keys must be 100% identical to DE keys`);
      for (const k of langKeys) {
        assert.ok(String(TRANSLATIONS[lang][k]).trim().length > 0, `${lang}.${k} must be non-empty`);
      }
    }
  });

  test("t() returns accurate translations for all 6 languages including newly localized chrome & delta keys", () => {
    assert.equal(t("action_clear", {}, "de"), "Ansicht leeren");
    assert.equal(t("action_clear", {}, "en"), "Clear view");
    assert.equal(t("action_clear", {}, "es"), "Limpiar vista");
    assert.equal(t("action_clear", {}, "zh"), "清空视图");
    assert.equal(t("action_clear", {}, "ja"), "表示をクリア");
    assert.equal(t("action_clear", {}, "ru"), "Очистить");

    assert.equal(t("ruleset_weapons", {}, "en"), "Weapons");
    assert.equal(t("ruleset_spells", {}, "es"), "Hechizos");
    assert.equal(t("meta_locations", {}, "zh"), "地点");
    assert.equal(t("meta_main_map", {}, "ja"), "メインマップ");
    assert.equal(t("meta_gold", {}, "ru"), "Золото");
    assert.equal(t("lang_switcher_label", {}, "de"), "Sprachauswahl");
  });

  test("t() interpolates parameters properly across languages", () => {
    const formattedDe = t("status_success", {
      name: "Campaign1",
      worlds: 3,
      sessions: 5,
    }, "de");
    assert.equal(formattedDe, "Campaign1 erfolgreich geladen (3 Welten, 5 Sessions).");

    const mediaLineEn = t("media_meta_line", {
      source: "maps/castle.png",
      exists: t("bool_yes", {}, "en"),
      included: t("bool_no", {}, "en"),
    }, "en");
    assert.equal(mediaLineEn, "Source: maps/castle.png · exists: yes · embedded: no");

    const deltaExportZh = t("action_export_delta", { count: 2 }, "zh");
    assert.equal(deltaExportZh, "导出变更 (2)");
  });

  test("fallback mechanism works correctly", () => {
    assert.equal(normalizeLocale("de-CH"), "de");
    assert.equal(normalizeLocale("en-GB"), "en");
    assert.equal(normalizeLocale("es-MX"), "es");
    assert.equal(normalizeLocale("zh-CN"), "zh");
    assert.equal(normalizeLocale("ja-JP"), "ja");
    assert.equal(normalizeLocale("ru-RU"), "ru");
    assert.equal(normalizeLocale("unknown-lang"), "de");
    assert.equal(DATE_LOCALES.ja, "ja-JP");
    setLocale("es");
    assert.equal(getLocale(), "es");
    assert.ok(SUPPORTED_LOCALES.includes(detectLocale()));
    setLocale("de");
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

  test("translateDocument updates mock DOM attributes including aria-label", () => {
    const node1 = { dataset: { i18n: "action_clear" }, textContent: "old" };
    const node2 = { dataset: { i18n: "action_player_mode" }, textContent: "old" };
    const ariaNode = {
      dataset: { i18nAriaLabel: "lang_switcher_label" },
      attrs: {},
      setAttribute(k, v) {
        this.attrs[k] = v;
      },
    };

    const mockDoc = {
      documentElement: { lang: "de" },
      querySelectorAll(selector) {
        if (selector === "[data-i18n]") return [node1, node2];
        if (selector === "[data-i18n-html]") return [];
        if (selector === "[data-i18n-placeholder]") return [];
        if (selector === "[data-i18n-aria-label]") return [ariaNode];
        return [];
      },
    };

    translateDocument(mockDoc, "en");
    assert.equal(mockDoc.documentElement.lang, "en");
    assert.equal(node1.textContent, "Clear view");
    assert.equal(node2.textContent, "Player Mode");
    assert.equal(ariaNode.attrs["aria-label"], "Language selection");
  });
});
