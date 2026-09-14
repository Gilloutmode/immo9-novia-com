#!/usr/bin/env bash
# Mise à jour hebdomadaire : récupère la dernière version du dépôt, réapplique l'installation (idempotente), diagnostic.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; cd "$REPO"
git pull --ff-only
bash scripts/install.sh --apply --skip-shared-skills "$@"
bash scripts/doctor.sh || true
echo "Nouveautés : voir CHANGELOG.md. Si des skills partagés ont changé : bash scripts/install.sh --apply"
