#!/usr/bin/env bash
# Déclare les crons de Novia Com (idempotent : clé novia-com:<key>). Nécessite un gateway démarré.
# Usage : install-crons.sh [--dry-run] [--enable-p1] [--disable-all]
#   sans option : crée les jobs absents (désactivés) sans toucher à l'état des jobs existants
#   --enable-p1  : active les jobs du palier 1 (après l'onboarding) ; --disable-all : désactive tout
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/install_crons.py" "$@"
