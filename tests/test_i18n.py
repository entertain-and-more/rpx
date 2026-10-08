"""
tests/test_i18n.py - Hermetische Vertragstestsuite für Tier-2 6-Sprachen-Lokalisierung (RPX Pro).
===================================================================================================
Prüft Policy P-006 Konformität:
- Alle 6 Sprachen (de, en, es, zh-Hans, ja, ru) lückenlos gepflegt
- Deterministische 4-Stufen-Fallback-Kette (target -> en -> de -> key)
- Autonome Systemsprachenerkennung (detect_system_language)
- CJK- (zh-Hans, ja) und Kyrillisch- (ru) Encoding-Integrität ohne Mojibake
- Strikte Trennung von statischen UI-Texten und dynamischen Spielinhalten (TW-RPG-11)
- CI-Gate (manage_translations --check)
"""

import json
from pathlib import Path

from manage_translations import LANGUAGE_SLOTS, check_translations
from translator import (
    DEFAULT_LANGUAGE,
    FALLBACK_CHAIN,
    LANGUAGE_DISPLAY_NAMES,
    SUPPORTED_LANGUAGES,
    TranslationSystem,
    detect_system_language,
    get_translator,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS_FILE = REPO_ROOT / "locales" / "translations.json"


def test_tier2_constants_and_language_slots():
    assert SUPPORTED_LANGUAGES == ("de", "en", "es", "zh-Hans", "ja", "ru")
    assert LANGUAGE_SLOTS == SUPPORTED_LANGUAGES
    assert DEFAULT_LANGUAGE == "de"
    assert FALLBACK_CHAIN == ("en", "de")
    for lang in SUPPORTED_LANGUAGES:
        assert lang in LANGUAGE_DISPLAY_NAMES
        assert len(LANGUAGE_DISPLAY_NAMES[lang]) > 0


def test_tier2_six_languages_parity_and_catalog_completeness():
    assert TRANSLATIONS_FILE.exists(), f"translations.json must exist at {TRANSLATIONS_FILE}"

    with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    assert len(catalog) >= 170, f"Expected at least 170 UI keys, found {len(catalog)}"

    for key, entry in catalog.items():
        assert isinstance(entry, dict), f"Key '{key}' entry must be dict"
        for lang in SUPPORTED_LANGUAGES:
            assert lang in entry, f"Key '{key}' missing language slot '{lang}'"
            assert entry[lang], f"Key '{key}' has empty translation for '{lang}'"
            assert isinstance(entry[lang], str)

        # Ensure no mojibake in keys or translations
        for corrupted in ("\ufffd", "Ã", "âž•", "ðŸ"):
            assert corrupted not in key, f"Corrupted char in key: {key}"
            for lang in SUPPORTED_LANGUAGES:
                assert corrupted not in entry[lang], f"Corrupted char in '{lang}' translation for '{key}'"


def test_tier2_ttrpg_terms_in_all_six_languages():
    tr = TranslationSystem("de", REPO_ROOT)

    terms_to_check = [
        "Würfeln",
        "Kampf",
        "Charaktere",
        "Inventar",
        "Rundensteuerung",
        "Zug beenden",
        "Schaden",
        "Heilen",
        "Welt",
        "Einstellungen",
    ]

    for term in terms_to_check:
        for lang in SUPPORTED_LANGUAGES:
            tr.set_language(lang)
            translated = tr.t(term)
            assert translated, f"Term '{term}' must have valid translation in '{lang}'"
            assert translated != "", f"Term '{term}' translation empty in '{lang}'"

    # Exact expected translations in each language for key terms
    tr.set_language("de")
    assert tr.t("Würfeln") == "Würfeln"
    assert tr.t("Kampf") == "Kampf"

    tr.set_language("en")
    assert tr.t("Würfeln") == "Roll Dice"
    assert tr.t("Kampf") == "Combat"

    tr.set_language("es")
    assert tr.t("Würfeln") in ("Tirar dados", "Dados")
    assert tr.t("Kampf") == "Combate"

    tr.set_language("zh-Hans")
    assert tr.t("Würfeln") == "掷骰"
    assert tr.t("Kampf") == "战斗"

    tr.set_language("ja")
    assert tr.t("Würfeln") in ("ダイスロール", "ダイスを振る")
    assert tr.t("Kampf") == "戦闘"

    tr.set_language("ru")
    assert tr.t("Würfeln") == "Бросить кости"
    assert tr.t("Kampf") == "Бой"


def test_translator_four_stage_fallback_chain(tmp_path):
    catalog_path = tmp_path / "locales" / "translations.json"
    catalog_path.parent.mkdir(parents=True)

    # 1. Target present
    # 2. Target missing, en present -> falls back to en
    # 3. Target and en missing, de present -> falls back to de
    # 4. Target, en, and de missing -> falls back to key
    mock_data = {
        "KeyFull": {"de": "VollDE", "en": "FullEN", "es": "LlenoES", "zh-Hans": "完整ZH", "ja": "完全JA", "ru": "ПолныйRU"},
        "KeyNoJa": {"de": "StandardDE", "en": "DefaultEN", "es": "DefectoES", "zh-Hans": "默认ZH", "ja": "", "ru": "ПоУмолчаниюRU"},
        "KeyOnlyDe": {"de": "NurDE", "en": "", "es": "", "zh-Hans": "", "ja": "", "ru": ""},
        "KeyEmpty": {"de": "", "en": "", "es": "", "zh-Hans": "", "ja": "", "ru": ""},
    }
    catalog_path.write_text(json.dumps(mock_data), encoding="utf-8")

    tr = TranslationSystem("ja", tmp_path)

    # Full has ja -> returns ja
    assert tr.t("KeyFull") == "完全JA"

    # KeyNoJa lacks ja -> falls back to en
    assert tr.t("KeyNoJa") == "DefaultEN"

    # KeyOnlyDe lacks ja and en -> falls back to de
    assert tr.t("KeyOnlyDe") == "NurDE"

    # KeyEmpty lacks ja, en, de -> falls back to key itself
    assert tr.t("KeyEmpty") == "KeyEmpty"

    # Completely unknown key -> falls back to key itself
    assert tr.t("UnknownKeyXYZ") == "UnknownKeyXYZ"


def test_translator_detect_system_language(monkeypatch):
    monkeypatch.setenv("LANG", "zh_CN.UTF-8")
    assert detect_system_language() == "zh-Hans"

    monkeypatch.setenv("LANG", "ja_JP.UTF-8")
    assert detect_system_language() == "ja"

    monkeypatch.setenv("LANG", "ru_RU.UTF-8")
    assert detect_system_language() == "ru"

    monkeypatch.setenv("LANG", "es_ES.UTF-8")
    assert detect_system_language() == "es"

    monkeypatch.setenv("LANG", "en_US.UTF-8")
    assert detect_system_language() == "en"

    monkeypatch.setenv("LANG", "de_DE.UTF-8")
    assert detect_system_language() == "de"

    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LC_MESSAGES", raising=False)
    # Default fallback
    assert detect_system_language() in SUPPORTED_LANGUAGES


def test_translator_dynamic_switching_and_callbacks():
    tr = get_translator()
    original_lang = tr.get_language()

    notifications = []
    tr.register_language_changed_callback(lambda lang: notifications.append(lang))

    try:
        for lang in SUPPORTED_LANGUAGES:
            assert tr.set_language(lang) is True
            assert tr.get_language() == lang
            assert notifications[-1] == lang

        # Invalid language code rejected
        assert tr.set_language("invalid_xx") is False
        assert tr.get_language() == SUPPORTED_LANGUAGES[-1]
    finally:
        tr.set_language(original_lang)


def test_manage_translations_check_gate():
    assert check_translations(str(REPO_ROOT)) is True


def test_cjk_and_cyrillic_encoding_integrity():
    tr = get_translator()
    orig = tr.get_language()
    try:
        tr.set_language("zh-Hans")
        zh_text = tr.t("Charaktere")
        assert any("\u4e00" <= c <= "\u9fff" for c in zh_text), f"Expected Chinese Hanzi in '{zh_text}'"

        tr.set_language("ja")
        ja_text = tr.t("Inventar")
        assert any("\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in ja_text), f"Expected Japanese in '{ja_text}'"

        tr.set_language("ru")
        ru_text = tr.t("Einstellungen")
        assert any("\u0400" <= c <= "\u04ff" for c in ru_text), f"Expected Cyrillic in '{ru_text}'"
    finally:
        tr.set_language(orig)


def test_ui_vs_content_separation():
    tr = get_translator()
    custom_content = "Ein uralter Drache erwacht im Schattengebirge und fordert 3W6 Feuerschaden."
    # Dynamic campaign content must NEVER be mutated
    assert tr.translate_content(custom_content) == custom_content
