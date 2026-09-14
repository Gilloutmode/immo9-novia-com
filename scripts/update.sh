#!/usr/bin/env bash
# Mise à jour hebdomadaire : récupère la dernière version du dépôt, réapplique l'installation (idempotente), diagnostic.
# Vos fichiers locaux (state/, learning/, MEMORY.md, outbox/, memory/, tokens) ne sont pas suivis par git : ils ne bougent pas.
# Vos éditions de doctrine (doctrine/*.md, TEAM.md) sont mises de côté le temps du pull puis réappliquées ; en cas d'échec,
# elles sont restaurées et le script s'arrête avec un message précis.
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; cd "$REPO" || exit 1
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "== récupération"
git fetch origin || { echo "ERREUR : dépôt distant injoignable ; rien n'a été modifié." >&2; exit 1; }
if ! git merge-base --is-ancestor HEAD "origin/$BRANCH"; then echo "ERREUR : la branche locale a divergé de origin/$BRANCH ; résoudre manuellement (git status)." >&2; exit 1; fi
STASH=""
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  STASH="novia-update-$(date +%Y%m%d-%H%M%S)"; git stash push -m "$STASH" >/dev/null || { echo "ERREUR : impossible de mettre les éditions de côté." >&2; exit 1; }
  echo "éditions locales mises de côté ($STASH)"
fi
restore() { if [ -n "$STASH" ]; then if git stash pop >/dev/null 2>&1; then echo "éditions locales réappliquées"; else echo "CONFLIT : vos éditions sont dans « git stash list » ($STASH) ; résoudre puis « git stash drop »" >&2; return 1; fi; fi; }
if ! git merge --ff-only "origin/$BRANCH"; then echo "ERREUR : mise à jour impossible (fast-forward refusé)." >&2; restore; exit 1; fi
restore || exit 1
echo "== installation"
bash scripts/install.sh --apply --update-shared-skills "$@" || { echo "ERREUR : installation en échec ; la configuration précédente est sauvegardée (openclaw.json.bak-novia-<date>)." >&2; exit 1; }
echo "== diagnostic"
if bash scripts/doctor.sh; then echo "diagnostic : OK"; else echo "diagnostic : des points à corriger (voir ci-dessus)" >&2; exit 1; fi
echo "Nouveautés : voir CHANGELOG.md"
