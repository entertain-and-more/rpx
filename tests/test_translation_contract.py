import json
from pathlib import Path

from manage_translations import (
    LANGUAGE_SLOTS,
    check_translations,
    manage_translations,
)
from translator import (
    SUPPORTED_LANGUAGES,
    TranslationSystem,
    get_translator,
    t,
)


def test_legacy_catalog_is_normalized_for_all_language_slots(tmp_path):
    locales = tmp_path / "locales"
    locales.mkdir()
    (locales / "translations.json").write_text(
        json.dumps({
            "UnbekannterKey": {"de": "UnbekannterKey", "en": "UnknownKey"},
            "Speichern": {"de": "Speichern", "en": "Save"},
        }),
        encoding="utf-8",
    )

    translator = TranslationSystem("es", tmp_path)
    assert SUPPORTED_LANGUAGES == LANGUAGE_SLOTS
    assert translator.get_language() == "es"
    assert set(translator.translations["Speichern"]) >= set(LANGUAGE_SLOTS)

    # Curated Spanish term returns Spanish
    assert translator.translate_ui("Speichern") == "Guardar"

    # Uncurated term falls back to English in Spanish mode
    assert translator.translate_ui("UnbekannterKey") == "UnknownKey"

    # Dynamic campaign content is never translated
    assert translator.translate_content("Eigene Kampagnenregel") == "Eigene Kampagnenregel"

    assert translator.set_language("zh-Hans") is True
    assert translator.set_language("xx") is False


def test_curated_spanish_ui_translation_does_not_translate_content(tmp_path):
    translator = TranslationSystem("es", tmp_path)
    translator.add_translation("Welt speichern", "Welt speichern", "Save world")

    # UI translation returns curated Spanish
    assert translator.translate_ui("Welt speichern") == "Guardar mundo"

    # Content translation preserves exact lore / notes / chat
    assert translator.translate_content("Lore: Elfenwald") == "Lore: Elfenwald"
    assert translator.translate_content("Regelwerk: D20 System") == "Regelwerk: D20 System"

    # Language switch to Japanese falls back to English
    assert translator.set_language("ja") is True
    assert translator.translate_ui("Welt speichern") == "Save world"


def test_scanner_persists_reserved_language_slots(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "ui.py").write_text('label.setText("Speichern")\n', encoding="utf-8")
    locales = source / "locales"
    locales.mkdir()
    (locales / "translations.json").write_text(
        json.dumps({"Bestand": {"de": "Bestand", "en": "Inventory"}}),
        encoding="utf-8",
    )

    manage_translations(str(source))
    saved = json.loads((locales / "translations.json").read_text(encoding="utf-8"))
    assert set(LANGUAGE_SLOTS) <= set(saved["Bestand"])
    assert set(LANGUAGE_SLOTS) <= set(saved["Speichern"])


def test_production_catalog_integrity_and_spanish_coverage():
    repo_root = Path(__file__).resolve().parents[1]
    trans_file = repo_root / "locales" / "translations.json"
    assert trans_file.exists(), f"translations.json must exist at {trans_file}"

    with open(trans_file, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    assert len(catalog) >= 150, f"Expected at least 150 UI keys, got {len(catalog)}"

    for key, entry in catalog.items():
        # Every entry must have all 6 language slots
        for slot in LANGUAGE_SLOTS:
            assert slot in entry, f"Key '{key}' missing slot '{slot}'"

        # de, en, and es must be non-empty strings
        assert entry["de"], f"Key '{key}' has empty German translation"
        assert entry["en"], f"Key '{key}' has empty English translation"
        assert entry["es"], f"Key '{key}' has empty Spanish translation"

        # Check for mojibake or corrupt characters
        for char in ("\ufffd", "Ã", "âž•", "ðŸ"):
            assert char not in key, f"Mojibake detected in key '{key}'"
            assert char not in entry["de"], f"Mojibake in de for '{key}'"
            assert char not in entry["en"], f"Mojibake in en for '{key}'"
            assert char not in entry["es"], f"Mojibake in es for '{key}'"

    # manage_translations --check must pass
    assert check_translations(str(repo_root)) is True


def test_spanish_ttrpg_vocabulary_coverage():
    tr = TranslationSystem("es")
    # Verify key TTRPG terms translate properly to Spanish
    assert tr.t("Würfeln") in ("Tirar dados", "Dados")
    assert tr.t("Rundensteuerung") == "Control de rondas"
    assert tr.t("Zug beenden") == "Terminar turno"
    assert tr.t("Nächste Runde") == "Siguiente ronda"
    assert tr.t("Kampf") == "Combate"
    assert tr.t("Charaktere") == "Personajes"
    assert tr.t("Inventar") == "Inventario"
    assert tr.t("Einstellungen") == "Configuración"
    assert tr.t("Schaden") == "Daño"
    assert tr.t("Heilen") == "Curar"


def test_global_translator_and_language_listeners():
    tr = get_translator()
    original_lang = tr.get_language()

    received = []
    tr.register_language_changed_callback(lambda lang: received.append(lang))

    try:
        assert tr.set_language("es") is True
        assert tr.get_language() == "es"
        assert received == ["es"]

        # Shortcut t() reflects new language
        assert t("Abbrechen") == "Cancelar"

        # Language display names
        names = tr.get_language_display_names()
        assert names["es"] == "Español"
        assert names["de"] == "Deutsch"
        assert names["en"] == "English"
    finally:
        tr.set_language(original_lang)
