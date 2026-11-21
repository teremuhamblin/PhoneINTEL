"""Module principal de PhoneINTEL : analyse OSINT sécurisée et assistant interactif."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Dict, Final, List, Optional, Sequence
import urllib.parse
import webbrowser

import phonenumbers
from phonenumbers import (
    NumberParseException,
    PhoneNumberFormat,
    PhoneNumberType,
    carrier,
    geocoder,
    timezone,
)

# ── Constantes de sécurité & limites O(1) ─────────────────────────────────────
VERSION: Final[str] = "1.1.0-alpha"
MAX_INPUT_LENGTH: Final[int] = 32
MAX_BATCH_FILE_BYTES: Final[int] = 1_048_576  # 1 Mo max
MAX_BATCH_LINES: Final[int] = 1_000
ALLOWED_PHONE_CHARS: Final[frozenset[str]] = frozenset("0123456789+ -().")

DORK_CATEGORIES: Final[Dict[str, str]] = {
    "social_networks": 'site:facebook.com OR site:instagram.com OR site:linkedin.com OR site:x.com "{num}"',
    "forums": 'site:reddit.com OR site:quora.com OR inurl:forum "{num}"',
    "pastes": 'site:pastebin.com OR site:ghostbin.co OR site:dpaste.org "{num}"',
    "ecommerce": 'site:leboncoin.fr OR site:ebay.com OR site:amazon.fr "{num}"',
    "news": 'site:news.google.com OR inurl:article "{num}"',
    "phone_directories": 'site:pagesjaunes.fr OR site:whitepages.com OR site:truecaller.com "{num}"',
    "reputation": '"{num}" ("arnaque" OR "spam" OR "scam" OR "signalement")',
}

LINE_TYPE_LABELS: Final[Dict[int, str]] = {
    PhoneNumberType.MOBILE: "Mobile",
    PhoneNumberType.FIXED_LINE: "Ligne fixe",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixe ou Mobile",
    PhoneNumberType.VOIP: "VoIP",
    PhoneNumberType.TOLL_FREE: "Numéro vert / gratuit",
    PhoneNumberType.PREMIUM_RATE: "Numéro surtaxé",
    PhoneNumberType.SHARED_COST: "Coût partagé",
    PhoneNumberType.PAGER: "Pager",
    PhoneNumberType.UAN: "Numéro universel (UAN)",
}


# ── Palette ANSI Ice-Blue (désactivée automatiquement si non-TTY ou NO_COLOR) ─
class Palette:
    """Gestion propre des couleurs terminal."""

    def __init__(self, enabled: bool = True) -> None:
        use_color = enabled and sys.stdout.isatty()
        self.ice = "\033[96m" if use_color else ""
        self.blue = "\033[94m" if use_color else ""
        self.green = "\033[92m" if use_color else ""
        self.yellow = "\033[93m" if use_color else ""
        self.red = "\033[91m" if use_color else ""
        self.dim = "\033[90m" if use_color else ""
        self.bold = "\033[1m" if use_color else ""
        self.reset = "\033[0m" if use_color else ""


@dataclass(frozen=True)
class PhoneIntelReport:
    """Rapport structuré d'analyse OSINT sur un numéro."""

    input_masked: str
    e164: str
    international: str
    national: str
    rfc3966: str
    country_code: int
    region_code: str
    line_type: str
    carrier_name: str
    location: str
    timezones: List[str]
    risk_hint: str


@dataclass
class AssistantConfig:
    """Préférences intelligentes de session pour l'assistant interactif."""

    default_region: Optional[str] = "FR"
    rgpd_mask_output: bool = False
    search_engine: str = "google"  # google | duckduckgo
    use_color: bool = True


# ── Fonctions cœur sécurisées ─────────────────────────────────────────────────
def _sanitize_region(region: Optional[str]) -> Optional[str]:
    """Valide un code pays ISO-3166-1 alpha-2 strict."""
    if region is None:
        return None
    if not isinstance(region, str):
        return None
    cleaned = region.strip().upper()
    if len(cleaned) != 2 or not cleaned.isascii() or not cleaned.isalpha():
        return None
    return cleaned


def mask_phone_number(e164: str) -> str:
    """Masque un numéro pour un affichage/log conforme RGPD (ex: +33******78)."""
    if len(e164) <= 5:
        return "*" * len(e164)
    prefix = e164[:3] if e164.startswith("+") else e164[:2]
    suffix = e164[-2:]
    middle = "*" * max(1, len(e164) - len(prefix) - len(suffix))
    return f"{prefix}{middle}{suffix}"


def parse_phone_number(number: str, region: Optional[str] = None) -> Optional[str]:
    """Parse et valide un numéro de téléphone avec garde-fous de sécurité O(1).

    Args:
        number: La chaîne représentant le numéro de téléphone.
        region: Le code pays ISO (ex: 'FR') si le numéro est local.

    Returns:
        Le numéro formaté en E.164 si valide, None sinon.
    """
    if not isinstance(number, str):
        return None

    # 1. Garde-fou O(1) anti-DoS avant tout parsing
    if not number or len(number) > MAX_INPUT_LENGTH:
        return None

    # 2. Rejet strict des caractères non-ASCII (anti-homoglyphes/Unicode) et de contrôle
    if not number.isascii():
        return None

    stripped = number.strip(" ")
    if not stripped:
        return None

    if any(ch not in ALLOWED_PHONE_CHARS for ch in stripped):
        return None

    if "+" in stripped and (not stripped.startswith("+") or stripped.count("+") > 1):
        return None

    valid_region = _sanitize_region(region)
    if region is not None and valid_region is None:
        return None

    try:
        parsed_number = phonenumbers.parse(stripped, valid_region)
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
    except NumberParseException:
        pass
    return None


def analyze_phone_number(
    number: str,
    region: Optional[str] = None,
    mask_output: bool = False,
) -> Optional[PhoneIntelReport]:
    """Effectue une analyse OSINT complète et structurée sur un numéro valide."""
    e164 = parse_phone_number(number, region=region)
    if e164 is None:
        return None

    parsed = phonenumbers.parse(e164, None)
    num_type = phonenumbers.number_type(parsed)
    line_label = LINE_TYPE_LABELS.get(num_type, "Indéterminé")
    region_code = phonenumbers.region_code_for_number(parsed) or "N/A"
    carrier_name = carrier.name_for_number(parsed, "fr") or carrier.name_for_number(parsed, "en") or "Inconnu"
    location = geocoder.description_for_number(parsed, "fr") or geocoder.description_for_number(parsed, "en") or "Inconnue"
    tz_list = list(timezone.time_zones_for_number(parsed))

    if num_type == PhoneNumberType.VOIP:
        risk_hint = "Moyen (Ligne VoIP / virtuelle)"
    elif num_type == PhoneNumberType.PREMIUM_RATE:
        risk_hint = "Élevé (Numéro surtaxé)"
    else:
        risk_hint = "Standard (Numéro attribué valide)"

    display_e164 = mask_phone_number(e164) if mask_output else e164

    return PhoneIntelReport(
        input_masked=mask_phone_number(e164),
        e164=display_e164,
        international=phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL) if not mask_output else display_e164,
        national=phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL) if not mask_output else display_e164,
        rfc3966=phonenumbers.format_number(parsed, PhoneNumberFormat.RFC3966) if not mask_output else f"tel:{display_e164}",
        country_code=parsed.country_code or 0,
        region_code=region_code,
        line_type=line_label,
        carrier_name=carrier_name,
        location=location,
        timezones=tz_list,
        risk_hint=risk_hint,
    )


def generate_dorks(
    e164: str,
    categories: Sequence[str],
    engine: str = "google",
) -> Dict[str, str]:
    """Génère des URLs OSINT encodées de façon sûre pour les catégories demandées."""
    selected = list(DORK_CATEGORIES.keys()) if "all" in categories else [c for c in categories if c in DORK_CATEGORIES]
    base_url = "https://duckduckgo.com/?q=" if engine == "duckduckgo" else "https://www.google.com/search?q="

    results: Dict[str, str] = {}
    for cat in selected:
        query = DORK_CATEGORIES[cat].format(num=e164)
        results[cat] = base_url + urllib.parse.quote_plus(query)
    return results


def build_map_url(location_query: str) -> str:
    """Construit un lien cartographique HTTPS sûr."""
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(location_query)


def open_safe_url(url: str) -> bool:
    """Ouvre une URL uniquement si son schéma est strictement HTTPS."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    return webbrowser.open(url)


def read_batch_file(file_path: str) -> List[str]:
    """Lit un fichier texte de numéros avec protection taille, symlink et déduplication."""
    path = Path(file_path)
    if not path.exists() or path.is_symlink() or not path.is_file():
        raise ValueError(f"Fichier invalide ou non autorisé : {file_path}")

    if path.stat().st_size > MAX_BATCH_FILE_BYTES:
        raise ValueError(f"Fichier trop volumineux (> {MAX_BATCH_FILE_BYTES} octets).")

    seen: Dict[str, None] = {}
    with path.open("r", encoding="utf-8", errors="strict") as handle:
        for idx, line in enumerate(handle, start=1):
            if idx > MAX_BATCH_LINES:
                break
            candidate = line.strip()
            if not candidate or candidate.startswith("#"):
                continue
            seen[candidate] = None
    return list(seen.keys())


def export_reports_json(reports: Sequence[PhoneIntelReport], output_path: str) -> Path:
    """Exporte les rapports en JSON UTF-8 propre."""
    target = Path(output_path)
    if target.is_symlink():
        raise ValueError("Export refusé sur un lien symbolique.")
    payload = [asdict(r) for r in reports]
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


# ── Interface Interactive & Choix Multiple Avancé ─────────────────────────────
class PhoneIntelAssistant:
    """Assistant CLI interactif complet avec options intelligentes et choix multiple."""

    def __init__(self, config: Optional[AssistantConfig] = None) -> None:
        self.cfg = config or AssistantConfig()
        self.p = Palette(enabled=self.cfg.use_color)

    def _banner(self) -> None:
        p = self.p
        print(f"\n{p.ice}{p.bold}╭──────────────────────────────────────────────────────────────╮")
        print(f"│  🫆  PHONEINTEL v{VERSION}  •  ASSISTANT OSINT INTELLIGENT    │")
        print(f"╰──────────────────────────────────────────────────────────────╯{p.reset}")
        rgpd_txt = f"{p.green}ON{p.reset}" if self.cfg.rgpd_mask_output else f"{p.dim}OFF{p.reset}"
        print(
            f"{p.dim}  Région par défaut : {p.ice}{self.cfg.default_region or 'Aucune'}{p.dim} │ "
            f"Masquage RGPD : {rgpd_txt}{p.dim} │ "
            f"Moteur : {p.ice}{self.cfg.search_engine}{p.reset}\n"
        )

    def _prompt(self, label: str, default: Optional[str] = None) -> str:
        suffix = f" [{default}]" if default else ""
        raw = input(f"{self.p.ice}❯ {self.p.bold}{label}{suffix}:{self.p.reset} ").strip()
        return raw if raw else (default or "")

    def prompt_multi_choice(
        self,
        title: str,
        options: Sequence[tuple[str, str]],
        default_keys: Optional[Sequence[str]] = None,
    ) -> List[str]:
        """Sélecteur avancé à choix multiple (accepte '1,3', '1-4', 'all', 'none')."""
        p = self.p
        print(f"\n{p.blue}{p.bold}▸ {title}{p.reset}")
        for idx, (key, label) in enumerate(options, start=1):
            marker = f"{p.green}*{p.reset}" if default_keys and key in default_keys else " "
            print(f"  {p.ice}[{idx}]{p.reset}{marker} {label} {p.dim}({key}){p.reset}")

        print(f"{p.dim}  Astuce : saisissez '1,3', '1-3', 'all' ou Entrée pour défaut.{p.reset}")

        while True:
            raw = self._prompt("Votre sélection", "défaut" if default_keys else "all").lower()
            if raw in ("défaut", "defaut", "") and default_keys is not None:
                return list(default_keys)
            if raw == "all":
                return [k for k, _ in options]
            if raw == "none":
                return []

            chosen_indices: List[int] = []
            valid = True
            for token in raw.replace(" ", ",").split(","):
                if not token:
                    continue
                if "-" in token:
                    parts = token.split("-", 1)
                    if parts[0].isdigit() and parts[1].isdigit():
                        start_i, end_i = int(parts[0]), int(parts[1])
                        if 1 <= start_i <= end_i <= len(options):
                            chosen_indices.extend(range(start_i, end_i + 1))
                            continue
                    valid = False
                    break
                elif token.isdigit() and 1 <= int(token) <= len(options):
                    chosen_indices.append(int(token))
                else:
                    valid = False
                    break

            if valid and chosen_indices:
                # Déduplication en conservant l'ordre
                unique = list(dict.fromkeys(chosen_indices))
                return [options[i - 1][0] for i in unique]

            print(f"{p.red}[-] Sélection invalide. Exemple valide : 1,2 ou 1-3 ou all.{p.reset}")

    def _smart_read_number(self) -> tuple[Optional[str], Optional[str]]:
        """Lit un numéro et suggère intelligemment une région s'il manque l'indicatif '+'."""
        raw = self._prompt("Numéro cible (ex: +33612345678 ou 0612345678)")
        if not raw:
            return None, None

        region = None
        if not raw.strip().startswith("+"):
            print(f"{self.p.yellow}[!] Format local détecté (sans '+').{self.p.reset}")
            region = self._prompt("Code pays ISO (FR, BE, CH, CA, US...)", self.cfg.default_region or "FR")

        return raw, region

    def print_report(self, report: PhoneIntelReport) -> None:
        """Affiche un rapport lisible et stylisé dans le terminal."""
        p = self.p
        print(f"\n{p.green}{p.bold}[+] RAPPORT OSINT VALIDÉ ({report.region_code}){p.reset}")
        print(f"  {p.ice}E.164         :{p.reset} {report.e164}")
        print(f"  {p.ice}International :{p.reset} {report.international}")
        print(f"  {p.ice}National      :{p.reset} {report.national}")
        print(f"  {p.ice}Type de ligne :{p.reset} {report.line_type}")
        print(f"  {p.ice}Opérateur     :{p.reset} {report.carrier_name}")
        print(f"  {p.ice}Localisation  :{p.reset} {report.location}")
        print(f"  {p.ice}Fuseau(x)     :{p.reset} {', '.join(report.timezones) or 'N/A'}")
        print(f"  {p.ice}Niveau risque :{p.reset} {report.risk_hint}")
        print(f"  {p.dim}Masqué RGPD   : {report.input_masked}{p.reset}")

    def _flow_analyze(self) -> None:
        number, region = self._smart_read_number()
        if not number:
            return

        report = analyze_phone_number(number, region=region, mask_output=self.cfg.rgpd_mask_output)
        if not report:
            print(f"{self.p.red}[-] Numéro invalide, hors format ou bloqué par les contrôles sécurité.{p.reset}")
            return

        # Choix multiple avancé des actions post-analyse
        actions = self.prompt_multi_choice(
            "Actions à exécuter sur cette cible",
            [
                ("info", "Afficher la fiche OSINT complète"),
                ("dorks", "Générer des Dorks OSINT ciblés"),
                ("map", "Générer le lien cartographique"),
                ("json", "Exporter le rapport en JSON"),
                ("browser", "Ouvrir la localisation dans le navigateur"),
            ],
            default_keys=["info"],
        )

        if "info" in actions:
            self.print_report(report)

        if "dorks" in actions:
            dork_opts = [(k, f"Catégorie {k}") for k in DORK_CATEGORIES]
            chosen_cats = self.prompt_multi_choice("Catégories de Dorks", dork_opts, default_keys=["social_networks", "reputation"])
            e164_real = parse_phone_number(number, region=region) or report.e164
            dorks = generate_dorks(e164_real, chosen_cats, engine=self.cfg.search_engine)
            print(f"\n{self.p.ice}{p.bold}[+] Dorks générés ({len(dorks)}) :{p.reset}" if (p := self.p) else "")
            for cat, url in dorks.items():
                print(f"  {p.blue}• {cat:18s}{p.reset} ➔ {url}")

        if "map" in actions or "browser" in actions:
            loc_query = report.location if report.location != "Inconnue" else report.region_code
            map_url = build_map_url(loc_query)
            print(f"\n{self.p.ice}[🗺️] Lien carte :{p.reset} {map_url}")
            if "browser" in actions:
                open_safe_url(map_url)

        if "json" in actions:
            out_file = self._prompt("Nom du fichier JSON", f"report_{report.region_code.lower()}.json")
            saved = export_reports_json([report], out_file)
            print(f"{self.p.green}[+] Export JSON enregistré : {saved}{p.reset}")

    def _flow_batch(self) -> None:
        file_path = self._prompt("Chemin du fichier liste (.txt)")
        if not file_path:
            return
        try:
            candidates = read_batch_file(file_path)
        except (OSError, ValueError) as exc:
            print(f"{self.p.red}[-] Erreur lecture batch : {exc}{p.reset}")
            return

        region = self._prompt("Région fallback pour numéros locaux (vide = aucune)", self.cfg.default_region or "") or None
        options = self.prompt_multi_choice(
            "Options du traitement par lot",
            [
                ("mask", "Masquer les numéros dans la sortie (RGPD)"),
                ("export", "Exporter les résultats valides en JSON"),
            ],
            default_keys=["mask" if self.cfg.rgpd_mask_output else ""],
        )
        mask = "mask" in options or self.cfg.rgpd_mask_output

        reports: List[PhoneIntelReport] = []
        invalid_count = 0
        for item in candidates:
            rep = analyze_phone_number(item, region=region, mask_output=mask)
            if rep:
                reports.append(rep)
                print(f"  {self.p.green}[✓]{p.reset} {rep.e164} | {rep.line_type} | {rep.carrier_name} | {rep.location}")
            else:
                invalid_count += 1
                print(f"  {self.p.red}[✗]{p.reset} Rejeté : {item[:20]}")

        print(f"\n{self.p.ice}[*] Bilan : {len(reports)} valide(s), {invalid_count} invalide(s).{p.reset}")
        if "export" in options and reports:
            out_path = self._prompt("Fichier JSON de sortie", "batch_results.json")
            saved = export_reports_json(reports, out_path)
            print(f"{self.p.green}[+] Exporté : {saved}{p.reset}")

    def _flow_settings(self) -> None:
        choices = self.prompt_multi_choice(
            "Paramètres intelligents à modifier",
            [
                ("region", f"Région par défaut (actuel: {self.cfg.default_region})"),
                ("rgpd", f"Basculer masquage RGPD (actuel: {self.cfg.rgpd_mask_output})"),
                ("engine", f"Moteur Dorks (actuel: {self.cfg.search_engine})"),
                ("color", f"Basculer couleurs ANSI (actuel: {self.cfg.use_color})"),
            ],
        )
        if "region" in choices:
            new_reg = self._prompt("Nouveau code pays ISO (ex: FR, BE, US, ou 'none')", "FR")
            self.cfg.default_region = None if new_reg.lower() == "none" else _sanitize_region(new_reg)
        if "rgpd" in choices:
            self.cfg.rgpd_mask_output = not self.cfg.rgpd_mask_output
        if "engine" in choices:
            eng = self._prompt("Moteur (google / duckduckgo)", self.cfg.search_engine).lower()
            if eng in ("google", "duckduckgo"):
                self.cfg.search_engine = eng
        if "color" in choices:
            self.cfg.use_color = not self.cfg.use_color
            self.p = Palette(enabled=self.cfg.use_color)

    def run(self) -> None:
        """Boucle principale de l'assistant interactif."""
        try:
            while True:
                self._banner()
                print("  [1] 🔎 Analyse OSINT intelligente (avec choix multiple)")
                print("  [2] 📂 Traitement par lots sécurisé (.txt)")
                print("  [3] ⚙️  Options intelligentes & préférences")
                print("  [4] ⚖️  Crédits & avertissement légal")
                print("  [0] 🚪 Quitter\n")

                choice = self._prompt("Menu principal")
                if choice == "1":
                    self._flow_analyze()
                elif choice == "2":
                    self._flow_batch()
                elif choice == "3":
                    self._flow_settings()
                elif choice == "4":
                    print(
                        f"\n{self.p.yellow}PhoneINTEL v{VERSION} — Usage strictement éducatif et "
                        f"évaluations autorisées uniquement (Licence BSD-3).{self.p.reset}"
                    )
                elif choice == "0":
                    print(f"{self.p.ice}Au revoir.{p.reset if (p := self.p) else ''}")
                    break
                else:
                    print(f"{self.p.red}[-] Choix invalide.{self.p.reset}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{self.p.dim}Interruption utilisateur. Fermeture propre.{self.p.reset}")


# ── Point d'entrée CLI ────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phoneintel",
        description="PhoneINTEL — Outil OSINT sécurisé & assistant interactif.",
    )
    parser.add_argument("target", nargs="?", help="Numéro cible (ex: +33612345678)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Lancer l'assistant interactif complet")
    parser.add_argument("--info", metavar="NUM", help="Afficher l'analyse OSINT complète d'un numéro")
    parser.add_argument("--region", metavar="ISO", help="Code pays ISO à 2 lettres pour numéro local (ex: FR)")
    parser.add_argument("--input", metavar="FILE", help="Analyser un fichier texte de numéros (batch)")
    parser.add_argument("--dorks", metavar="NUM", help="Générer des dorks OSINT pour un numéro")
    parser.add_argument("--type", dest="dork_types", default="all", help="Catégories de dorks séparées par virgule ou 'all'")
    parser.add_argument("--engine", choices=["google", "duckduckgo"], default="google", help="Moteur de recherche Dorks")
    parser.add_argument("--map", action="store_true", help="Générer le lien cartographique")
    parser.add_argument("--browser", action="store_true", help="Ouvrir le lien carte dans le navigateur")
    parser.add_argument("--mask", action="store_true", help="Masquer les numéros (RGPD)")
    parser.add_argument("--json", action="store_true", help="Sortie structurée au format JSON")
    parser.add_argument("--no-color", action="store_true", help="Désactiver les couleurs ANSI")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Point d'entrée principal CLI et Assistant."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Lancement automatique de l'assistant si aucun argument ou si --interactive
    if args.interactive or len(sys.argv if argv is None else argv) == 0 or (
        not args.target and not args.info and not args.input and not args.dorks
    ):
        cfg = AssistantConfig(
            default_region=_sanitize_region(args.region) or "FR",
            rgpd_mask_output=args.mask,
            search_engine=args.engine,
            use_color=not args.no_color,
        )
        PhoneIntelAssistant(cfg).run()
        return 0

    if args.input:
        try:
            items = read_batch_file(args.input)
        except (OSError, ValueError) as exc:
            print(f"[-] Erreur batch : {exc}", file=sys.stderr)
            return 1
        reports = [r for item in items if (r := analyze_phone_number(item, region=args.region, mask_output=args.mask))]
        if args.json:
            print(json.dumps([asdict(r) for r in reports], indent=2, ensure_ascii=False))
        else:
            for r in reports:
                print(f"[+] {r.e164} | {r.line_type} | {r.carrier_name} | {r.location}")
        return 0

    if args.dorks:
        e164 = parse_phone_number(args.dorks, region=args.region)
        if not e164:
            print("[-] Numéro invalide ou bloqué par les contrôles de sécurité.", file=sys.stderr)
            return 1
        cats = [c.strip() for c in args.dork_types.split(",") if c.strip()]
        dorks = generate_dorks(e164, cats, engine=args.engine)
        if args.json:
            print(json.dumps(dorks, indent=2, ensure_ascii=False))
        else:
            for cat, url in dorks.items():
                print(f"[{cat}] {url}")
        return 0

    target_number = args.info or args.target
    if not target_number:
        parser.print_help()
        return 1

    # Compatibilité stricte avec l'appel direct `python src/phoneintel.py +33612345678`
    if args.info or args.json or args.map or args.browser or args.mask:
        report = analyze_phone_number(target_number, region=args.region, mask_output=args.mask)
        if not report:
            print("[-] Numéro invalide ou mal formaté.", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
        else:
            PhoneIntelAssistant(AssistantConfig(use_color=not args.no_color)).print_report(report)
        if args.map or args.browser:
            url = build_map_url(report.location if report.location != "Inconnue" else report.region_code)
            print(f"[+] Carte : {url}")
            if args.browser:
                open_safe_url(url)
        return 0

    result = parse_phone_number(target_number, region=args.region)
    if result:
        print(f"[+] Numéro valide : {result}")
        return 0

    print("[-] Numéro invalide ou mal formaté.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
