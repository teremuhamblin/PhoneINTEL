"""Utilitaires sécurisés de parsing et normalisation pour PhoneINTEL."""

from __future__ import annotations

from typing import Final

# Garde-fou O(1) : aucun numéro légitime formaté ne dépasse 32 caractères
_MAX_RAW_LENGTH: Final[int] = 32
_MIN_E164_DIGITS: Final[int] = 7
_MAX_E164_DIGITS: Final[int] = 15
_ALLOWED_SEPARATORS: Final[frozenset[str]] = frozenset({" ", "-", ".", "(", ")"})


def parse_phone_number(raw_number: str) -> str | None:
    """Valide et normalise un numéro international au format strict E.164.

    Retourne le numéro normalisé (ex: '+33612345678') ou None si invalide/suspect.
    """
    if not isinstance(raw_number, str):
        return None

    # 1. Garde-fou O(1) immédiat avant toute allocation ou boucle
    if not raw_number or len(raw_number) > _MAX_RAW_LENGTH:
        return None

    stripped = raw_number.strip(" ")
    if not stripped.startswith("+"):
        return None

    # 2. Validation caractère par caractère en ASCII strict (anti-Unicode / anti-CRLF / anti-ReDoS)
    digits: list[str] = []
    for ch in stripped[1:]:
        if "0" <= ch <= "9":
            digits.append(ch)
            if len(digits) > _MAX_E164_DIGITS:
                return None
        elif ch in _ALLOWED_SEPARATORS:
            continue
        else:
            # Rejette \n, \r, \x00, lettres, chiffres non-ASCII, '+' supplémentaires, etc.
            return None

    # 3. Contraintes E.164 : 7 à 15 chiffres et premier chiffre entre 1 et 9
    if len(digits) < _MIN_E164_DIGITS or digits[0] == "0":
        return None

    return "+" + "".join(digits)
