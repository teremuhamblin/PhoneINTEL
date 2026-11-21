#!/usr/bin/env bash
# ==============================================================================
# Script d'installation sécurisé et automatisé pour PhoneINTEL (v1.1-alpha)
# Auteur / Mainteneur : HamBlin Teremu
# Supporte : Termux (Android 16), Debian/Ubuntu/Kali, Arch, Fedora & macOS
# ==============================================================================

set -euo pipefail
IFS=$'\n\t'

# --- Palette Ice-Blue (désactivée automatiquement si non-TTY) ---
if [ -t 1 ]; then
    readonly ICE='\033[1;96m'
    readonly GREEN='\033[1;32m'
    readonly YELLOW='\033[1;33m'
    readonly RED='\033[1;31m'
    readonly DIM='\033[0;90m'
    readonly NC='\033[0m'
else
    readonly ICE='' GREEN='' YELLOW='' RED='' DIM='' NC=''
fi

# --- Chemins & options par défaut ---
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
readonly VENV_DIR="${HOME}/.venvs/phoneintel"
readonly BIN_DIR="${HOME}/.local/bin"
readonly WRAPPER_PATH="${BIN_DIR}/phoneintel"
readonly LOG_DIR="${XDG_DATA_HOME:-${HOME}/.local/share}/phoneintel"
readonly LOG_FILE="${LOG_DIR}/install.log"

INSTALL_MODE="auto"     # auto | local | pypi
DEV_EXTRAS=false
AUTO_YES=false
PLATFORM="unknown"

# --- Journalisation sécurisée ---
mkdir -p "$LOG_DIR"
chmod 700 "$LOG_DIR"
touch "$LOG_FILE"
chmod 600 "$LOG_FILE"

_log() {
    local level="$1"
    local color="$2"
    local msg="$3"
    printf '%b[%s]%b %s\n' "$color" "$level" "$NC" "$msg"
    printf '[%s] [%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$level" "$msg" >> "$LOG_FILE"
}

log_info()    { _log "INFO" "$ICE" "$1"; }
log_success() { _log "OK" "$GREEN" "$1"; }
log_warn()    { _log "WARN" "$YELLOW" "$1"; }
log_error()   { _log "ERR" "$RED" "$1" >&2; exit 1; }

trap 'log_error "Interruption ou erreur inattendue à la ligne ${LINENO}."' ERR

usage() {
    cat << EOF
Usage: bash install.sh [OPTIONS]

Options:
  --local        Force l'installation depuis le dépôt local (src/phoneintel.py)
  --pypi         Force l'installation depuis PyPI (pip install phoneintel)
  --dev          Installe aussi les outils dev/CI (pytest, ruff, mypy, bandit)
  -y, --yes      Mode non-interactif (accepte automatiquement les mises à jour)
  -h, --help     Affiche cette aide
EOF
    exit 0
}

parse_args() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --local) INSTALL_MODE="local" ;;
            --pypi)  INSTALL_MODE="pypi" ;;
            --dev)   DEV_EXTRAS=true ;;
            -y|--yes) AUTO_YES=true ;;
            -h|--help) usage ;;
            *) log_error "Option inconnue : $1 (voir --help)" ;;
        esac
        shift
    done

    if [ "$INSTALL_MODE" = "auto" ]; then
        if [ -f "${SCRIPT_DIR}/src/phoneintel.py" ]; then
            INSTALL_MODE="local"
        else
            INSTALL_MODE="pypi"
        fi
    fi
}

# --- 1. Détection de l'environnement ---
detect_platform() {
    log_info "Détection de l'environnement d'exécution..."
    if [ -n "${TERMUX_VERSION:-}" ] || [ -d "/data/data/com.termux" ]; then
        PLATFORM="termux"
    elif command -v apt-get >/dev/null 2>&1; then
        PLATFORM="debian"
    elif command -v pacman >/dev/null 2>&1; then
        PLATFORM="arch"
    elif command -v dnf >/dev/null 2>&1; then
        PLATFORM="fedora"
    elif [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
        PLATFORM="macos"
    else
        PLATFORM="generic"
    fi
    log_success "Plateforme détectée : ${PLATFORM} (mode installation : ${INSTALL_MODE})"
}

# --- 2. Dépendances système & stockage Termux ---
install_system_dependencies() {
    case "$PLATFORM" in
        termux)
            if [ ! -d "${HOME}/storage" ] && [ "$AUTO_YES" = false ] && command -v termux-setup-storage >/dev/null 2>&1; then
                log_warn "Configuration du stockage Termux (autorisation Android possible)..."
                termux-setup-storage || log_warn "Stockage non configuré, poursuite..."
            fi
            log_info "Mise à jour des paquets Termux..."
            pkg update -y || log_warn "pkg update partiel, poursuite..."
            DEBIAN_FRONTEND=noninteractive pkg upgrade -y \
                -o Dpkg::Options::="--force-confdef" \
                -o Dpkg::Options::="--force-confold" || log_warn "pkg upgrade ignoré."
            for dep in python git libffi openssl clang make; do
                if ! dpkg -s "$dep" >/dev/null 2>&1; then
                    log_info "Installation Termux : $dep"
                    pkg install -y "$dep" || log_error "Échec installation : $dep"
                fi
            done
            ;;
        debian)
            if ! command -v python3 >/dev/null 2>&1 || ! python3 -m venv --help >/dev/null 2>&1; then
                log_info "Installation de python3, python3-venv et git via apt..."
                local sudo_cmd=""
                [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1 && sudo_cmd="sudo"
                $sudo_cmd apt-get update -y
                $sudo_cmd apt-get install -y python3 python3-venv python3-pip git
            fi
            ;;
        arch)
            if ! command -v python3 >/dev/null 2>&1; then
                local sudo_cmd=""
                [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1 && sudo_cmd="sudo"
                $sudo_cmd pacman -Sy --noconfirm python python-pip git
            fi
            ;;
        fedora)
            if ! command -v python3 >/dev/null 2>&1; then
                local sudo_cmd=""
                [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1 && sudo_cmd="sudo"
                $sudo_cmd dnf install -y python3 python3-pip git
            fi
            ;;
        macos)
            command -v python3 >/dev/null 2>&1 || brew install python git
            ;;
        *)
            log_warn "Gestionnaire non reconnu : vérification directe de python3..."
            ;;
    esac

    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python 3.8+ est introuvable. Installez Python avant de relancer."
    fi

    # Vérification Python >= 3.8
    if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'; then
        log_error "Python 3.8+ requis (détecté : $(python3 --version 2>&1))."
    fi
    log_success "Prérequis Python validés ($(python3 --version 2>&1))."
}

# --- 3. Environnement virtuel Python isolé (conforme PEP 668) ---
setup_python_venv() {
    log_info "Préparation du venv isolé dans ${VENV_DIR}..."
    mkdir -p "$(dirname "$VENV_DIR")"

    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR" || log_error "Impossible de créer le venv Python."
    fi

    local venv_python="${VENV_DIR}/bin/python"
    "$venv_python" -m pip install --upgrade pip --no-cache-dir >/dev/null || log_warn "Mise à jour pip ignorée."

    if [ "$INSTALL_MODE" = "local" ]; then
        log_info "Installation locale depuis ${SCRIPT_DIR}..."
        if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
            "$venv_python" -m pip install --no-cache-dir -r "${SCRIPT_DIR}/requirements.txt"
        else
            "$venv_python" -m pip install --no-cache-dir phonenumbers
        fi
        if [ -f "${SCRIPT_DIR}/pyproject.toml" ]; then
            "$venv_python" -m pip install --no-cache-dir -e "${SCRIPT_DIR}" --no-deps
        fi
    else
        log_info "Installation depuis PyPI (phoneintel)..."
        "$venv_python" -m pip install --no-cache-dir --upgrade phoneintel
    fi

    if [ "$DEV_EXTRAS" = true ]; then
        log_info "Installation des outils dev/sécurité (pytest, ruff, mypy, bandit)..."
        "$venv_python" -m pip install --no-cache-dir pytest pytest-cov ruff mypy bandit
    fi

    log_success "Environnement Python configuré."
}

# --- 4. Wrapper global sécurisé (sans source activate) ---
create_wrapper() {
    log_info "Création du lanceur global dans ${WRAPPER_PATH}..."
    mkdir -p "$BIN_DIR"

    if [ "$INSTALL_MODE" = "local" ] && [ -f "${SCRIPT_DIR}/src/phoneintel.py" ]; then
        cat > "$WRAPPER_PATH" << EOF
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${SCRIPT_DIR}\${PYTHONPATH:+:\$PYTHONPATH}"
exec "${VENV_DIR}/bin/python" "${SCRIPT_DIR}/src/phoneintel.py" "\$@"
EOF
    else
        cat > "$WRAPPER_PATH" << EOF
#!/usr/bin/env bash
set -euo pipefail
exec "${VENV_DIR}/bin/python" -m phoneintel "\$@"
EOF
    fi

    chmod 755 "$WRAPPER_PATH"

    # Ajout idempotent au PATH dans .bashrc / .zshrc sans jamais les sourcer
    local path_line='export PATH="$HOME/.local/bin:$PATH"'
    for rc in "${HOME}/.bashrc" "${HOME}/.zshrc"; do
        if [ -f "$rc" ] && ! grep -Fq '.local/bin' "$rc"; then
            printf '\n# Added by PhoneINTEL installer\n%s\n' "$path_line" >> "$rc"
            log_info "PATH mis à jour dans $(basename "$rc")."
        fi
    done
    export PATH="${BIN_DIR}:${PATH}"
    log_success "Commande 'phoneintel' installée."
}

# --- 5. Validation réelle de bout en bout ---
verify_installation() {
    log_info "Validation fonctionnelle de l'installation..."
    [ -x "$WRAPPER_PATH" ] || log_error "Lanceur introuvable : $WRAPPER_PATH"

    if "$WRAPPER_PATH" --help >/dev/null 2>&1; then
        log_success "PhoneINTEL installé et opérationnel !"
        printf '\n%bCommandes prêtes :%b\n' "$GREEN" "$NC"
        printf '  %bphoneintel%b                          # Assistant interactif complet\n' "$ICE" "$NC"
        printf '  %bphoneintel --info +33612345678%b      # Analyse OSINT rapide\n' "$ICE" "$NC"
        printf '  %bphoneintel --help%b                   # Aide complète\n' "$ICE" "$NC"
        printf '%b  (Si la commande est introuvable dans ce terminal : export PATH="$HOME/.local/bin:$PATH")%b\n\n' "$DIM" "$NC"
    else
        log_error "Le test d'exécution 'phoneintel --help' a échoué."
    fi
}

main() {
    printf '%b=== 🫆 Installation Sécurisée PhoneINTEL (v1.1-alpha) ===%b\n\n' "$ICE" "$NC"
    parse_args "$@"
    detect_platform
    install_system_dependencies
    setup_python_venv
    create_wrapper
    verify_installation
}

main "$@"
