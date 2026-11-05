import pytest
import phonenumbers

def test_valid_phone_number():
    # Test basique de validation de parsing d'un numéro
    parsed = phonenumbers.parse("+33612345678", None)
    assert phonenumbers.is_valid_number(parsed) is True
