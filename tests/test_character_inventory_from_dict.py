from rpx_pro.models.entities import Character
from rpx_pro.models.session import Session


def test_character_from_dict_coerces_invalid_inventory_payloads_to_empty_dict():
    for payload in (None, "", "broken", 42):
        character = Character.from_dict({
            "id": "char-broken",
            "name": "Broken",
            "inventory": payload,
        })

        assert character.inventory == {}
        assert list(character.inventory.items()) == []


def test_character_from_dict_keeps_legacy_inventory_list_compatibility():
    character = Character.from_dict({
        "id": "char-legacy",
        "name": "Legacy",
        "inventory": ["torch", "rope"],
    })

    assert character.inventory == {"torch": 1, "rope": 1}


def test_session_load_with_null_character_inventory_is_save_path_safe():
    session = Session.from_dict({
        "characters": {
            "char-null-inventory": {
                "id": "char-null-inventory",
                "name": "Null Inventory",
                "inventory": None,
            },
        },
    })

    character = session.characters["char-null-inventory"]
    assert character.inventory == {}
    assert character.to_dict()["inventory"] == {}
