#!/usr/bin/env bash

# ==============================================================================
# Script d'installation sécurisé et automatisé pour PhoneIntel sous Termux
# Auteur / Mainteneur : HamBlin Teremu (OwnerAdmin v2.0)
# Description : Installe et configure PhoneIntel de manière sécurisée et robuste.
# ==============================================================================

# Quitter immédiatement en cas d'erreur, de variable non définie ou d'échec de pipeline
set -euo pipefail

# --- Palette de couleurs pour les logs ---
readonly RED='\033[1;31m'
readonly GREEN='\033[1;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[1;34m'
readonly NC='\033[0m' # No Color

# --- Fonctions de journalisation ---
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCÈS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERREUR]${NC} $1" >&2
    exit 1
}

# --- 1. Vérification de l'environnement Termux ---
check_termux() {
    log_info "Vérification de l'environnement d'exécution..."
    if [ -z "${TERMUX_VERSION:-}" ] && [ ! -d "/data/data/com.termux" ]; then
        log_error "Ce script est conçu pour s'exécuter exclusivement dans l'environnement Termux."
    fi
    log_success "Environnement Termux détecté avec succès."
}

# --- 2. Mise à jour des paquets et stockage ---
setup_storage_and_packages() {
    log_info "Vérification de l'accès au stockage partagé..."
    if [ ! -d "$HOME/storage" ]; then
        log_warn "Configuration du stockage Termux (une autorisation interactive peut être requise)..."
        termux-setup-storage || log_warn "Échec de configuration du stockage, poursuite de l'installation..."
    fi

    log_info "Mise à jour des miroirs et des paquets système..."
    pkg update -y && pkg upgrade -y || log_error "Échec de la mise à jour des paquets Termux."
}

# --- 3. Installation des dépendances requises ---
install_dependencies() {
    log_info "Installation des dépendances requises (Python, Git, outils de compilation)..."
    local deps=("python" "python-pip" "git" "libffi" "openssl" "clang" "make")
    
    for dep in "${deps[@]}"; do
        if ! dpkg -s "$dep" >/dev/null 2>&1; then
            log_info "Installation de $dep..."
            pkg install -y "$dep" || log_error "Impossible d'installer la dépendance : $dep"
        else
            log_info "$dep est déjà installé."
        fi
    done
    log_success "Dépendances système installées avec succès."
}

# --- 4. Configuration sécurisée de l'environnement Python ---
setup_python_environment() {
    log_info "Mise à jour de l'outil de gestion pip..."
    pip install --upgrade pip --no-cache-dir || log_warn "Impossible de mettre à jour pip, poursuite..."

    log_info "Création d'un environnement virtuel Python isolé (recommandé pour la sécurité)..."
    local venv_dir="$HOME/.venvs/phoneintel"
    
    if [ ! -d "$venv_dir" ]; then
        python -m venv "$venv_dir" || log_error "Échec de la création de l'environnement virtuel Python."
    fi

    log_info "Activation de l'environnement virtuel..."
    # shellcheck source=/dev/null
    source "$venv_dir/bin/activate"

    log_info "Installation sécurisée de PhoneIntel via PyPI..."
    pip install --no-cache-dir phoneintel || log_error "Échec de l'installation du paquet phoneintel."
    
    log_success "PhoneIntel installé et isolé dans l'environnement virtuel."
}

# --- 5. Création d'un wrapper sécurisé global ---
create_wrapper() {
    log_info "Création d'un raccourci global sécurisé..."
    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"

    local wrapper_path="$bin_dir/phoneintel"
    cat << 'EOF' > "$wrapper_path"
#!/usr/bin/env bash
set -e
# Active l'environnement virtuel isolé et exécute l'outil
source "$HOME/.venvs/phoneintel/bin/activate"
exec python -m phoneintel "$@"
EOF

    chmod +x "$wrapper_path"

    # Vérification et ajout au PATH si nécessaire
    if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
        log_info "Ajout de $bin_dir au PATH dans .bashrc..."
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
        # shellcheck source=/dev/null
        source "$HOME/.bashrc"
    fi

    log_success "Raccourci global configuré avec succès."
}

# --- 6. Validation finale ---
verify_installation() {
    log_info "Vérification finale de l'installation..."
    local venv_path="$HOME/.venvs/phoneintel/bin/phoneintel"
    
    if [ -x "$venv_path" ]; then
        log_success "Installation de PhoneIntel terminée avec succès !"
        echo -e "\n${GREEN}Vous pouvez maintenant utiliser l'outil en entrant :${NC}"
        echo -e "  ${BLUE}phoneintel --help${NC} ou ${BLUE}phoneintel --disclaimer${NC}\n"
    else
        log_error "La vérification de l'exécutable a échoué."
    fi
}

# --- Point d'entrée principal ---
main() {
    echo -e "${BLUE}=== Installation Sécurisée de PhoneIntel (Termux) ===${NC}\n"
    check_termux
    setup_storage_and_packages
    install_dependencies
    setup_python_environment
    create_wrapper
    verify_installation
}

main "$@"
