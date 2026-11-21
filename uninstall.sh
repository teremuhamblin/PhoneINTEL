#!/usr/bin/env bash
set -euo pipefail

readonly VENV_DIR="${HOME}/.venvs/phoneintel"
readonly WRAPPER_PATH="${HOME}/.local/bin/phoneintel"
readonly LOG_DIR="${XDG_DATA_HOME:-${HOME}/.local/share}/phoneintel"

PURGE=false
[ "${1:-}" = "--purge" ] && PURGE=true

echo "🧹 Désinstallation de PhoneINTEL..."

[ -e "$WRAPPER_PATH" ] && rm -f "$WRAPPER_PATH" && echo "✅ Supprimé : $WRAPPER_PATH"
[ -d "$VENV_DIR" ]     && rm -rf "$VENV_DIR"    && echo "✅ Supprimé : $VENV_DIR"

if [ "$PURGE" = true ] && [ -d "$LOG_DIR" ]; then
    rm -rf "$LOG_DIR"
    echo "✅ Journaux purgés : $LOG_DIR"
fi

echo "✅ Désinstallation terminée."
