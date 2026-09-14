#!/usr/bin/env bash
# Mise à jour hebdomadaire : récupère la dernière version du dépôt, réapplique l'installation (idempotente), diagnostic.
# Vos fichiers locaux (state/, learning/, MEMORY.md, outbox/, memory/, tokens) ne sont pas suivis par git : ils ne bougent pas.
# Vos éditions de doctrine (doctrine/*.md, TEAM.md) sont mises de côté (git stash) puis réappliquées ; en cas de conflit, git le signale.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; cd "$REPO"
STASHED=0
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then git stash push -m "novia-update-$(date +%Y%m%d-%H%M%S)" >/dev/null && STASHED=1; echo "éditions locales mises de côté"; fi
git pull --ff-only
if [ "$STASHED" = 1 ]; then
  if git stash pop; then echo "éditions locales réappliquées"; else echo "CONFLIT : résoudre les fichiers marqués puis « git stash drop »" >&2; exit 1; fi
fi
bash scripts/install.sh --apply --update-shared-skills "$@"
if bash scripts/doctor.sh; then echo "diagnostic : OK"; else echo "diagnostic : des points à corriger (voir ci-dessus)" >&2; exit 1; fi
echo "Nouveautés : voir CHANGELOG.md"
