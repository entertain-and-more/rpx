import json

from manage_translations import LANGUAGE_SLOTS, manage_translations
from translator import SUPPORTED_LANGUAGES, TranslationSystem


def test_legacy_catalog_is_normalized_for_all_language_slots(tmp_path):
    locales = tmp_path / "locales"
    locales.mkdir()
    (locales / "translations.json").write_text(
        json.dumps({"Speichern": {"de": "Speichern", "en": "Save"}}),
        encoding="utf-8",
    )

    translator = TranslationSystem("es", tmp_path)
    assert SUPPORTED_LANGUAGES == LANGUAGE_SLOTS
    assert translator.get_language() == "es"
    assert set(translator.translations["Speichern"]) >= set(LANGUAGE_SLOTS)
    assert translator.translate_ui("Speichern") == "Save"
    assert translator.translate_content("Eigene Kampagnenregel") == "Eigene Kampagnenregel"

    assert translator.set_language("zh-Hans") is True
    assert translator.set_language("xx") is False


def test_curated_spanish_ui_translation_does_not_translate_content(tmp_path):
    translator = TranslationSystem("es", tmp_path)
    translator.add_translation("Welt speichern", "Welt speichern", "Save world")

    assert translator.translate_ui("Welt speichern") == "Guardar mundo"
    assert translator.translate_content("Lore: Elfenwald") == "Lore: Elfenwald"

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
