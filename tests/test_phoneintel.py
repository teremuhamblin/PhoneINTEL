"""Tests unitaires pour le module PhoneINTEL."""

from src.phoneintel import parse_phone_number


def test_parse_valid_phone_number() -> None:
    """Vérifie qu'un numéro valide français est correctement formaté."""
    valid_input = "+33612345678"
    formatted = parse_phone_number(valid_input)
    assert formatted == "+33612345678"


def test_parse_invalid_phone_number() -> None:
    """Vérifie qu'un numéro erroné retourne bien None."""
    invalid_input = "12345"
    formatted = parse_phone_number(invalid_input)
    assert formatted is None
