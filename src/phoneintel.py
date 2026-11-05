"""Module principal de PhoneINTEL pour l'analyse et l'OSINT de numéros."""

import sys
from typing import Optional
import phonenumbers
from phonenumbers import NumberParseException


def parse_phone_number(number: str, region: Optional[str] = None) -> Optional[str]:
    """Parse et valide un numéro de téléphone au format international ou local.

    Args:
        number: La chaîne représentant le numéro de téléphone.
        region: Le code pays ISO (ex: 'FR') si le numéro est local.

    Returns:
        Le numéro formaté en E.164 si valide, None sinon.
    """
    try:
        parsed_number = phonenumbers.parse(number, region)
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
    except NumberParseException:
        pass
    return None


def main() -> None:
    """Point d'entrée principal de l'application CLI."""
    if len(sys.argv) < 2:
        print("Usage: python src/phoneintel.py <numero>")
        sys.exit(1)

    target_number = sys.argv[1]
    result = parse_phone_number(target_number)

    if result:
        print(f"[+] Numéro valide : {result}")
    else:
        print("[-] Numéro invalide ou mal formaté.")
        sys.exit(1)


if __name__ == "__main__":
    main()
