#!/usr/bin/env bash
# Installe (ou met à jour) l'agent Novia Com dans OpenClaw. Simulation par défaut ; --apply pour écrire.
# Usage : scripts/install.sh [--apply] [--model <provider/model>] [--skip-shared-skills] [--update-shared-skills] [--skip-crons] [--allow-example-ids]
# Variables : OPENCLAW (commande, défaut « openclaw »), NOVIA_TELEGRAM_BOT_TOKEN (doit exister dans l'environnement du gateway ;
#             sa présence ici sert seulement à décider d'inclure le compte Telegram ; sa valeur n'est jamais affichée ni copiée).
# Ce que l'installation modifie hors de l'agent : le dossier partagé des skills (skills-shared/) et `cron.skipMissedJobs: true`.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; WS="$REPO/workspace"; AGENT="novia-com"
OPENCLAW="${OPENCLAW:-openclaw}"
APPLY=0; MODEL=""; SKIP_SKILLS=0; UPDATE_SKILLS=0; SKIP_CRONS=0; ALLOW_EXAMPLES=""
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1;; --model) MODEL="$2"; shift;; --skip-shared-skills) SKIP_SKILLS=1;; --update-shared-skills) UPDATE_SKILLS=1;;
    --skip-crons) SKIP_CRONS=1;; --allow-example-ids) ALLOW_EXAMPLES="--allow-example-ids";;
    -h|--help) sed -n '2,6p' "$0"; exit 0;; *) echo "option inconnue : $1" >&2; exit 1;;
  esac; shift
done
TS="$(date +%Y%m%d-%H%M%S)"
say() { printf '\n== %s\n' "$*"; }
run() { if [ "$APPLY" = 1 ]; then "$@"; else printf '[simulation] %s\n' "$(printf '%q ' "$@" | sed -E 's/([0-9]{6,}:[A-Za-z0-9_-]{20,})/***/g')"; fi; }
fail() { echo "ERREUR : $*" >&2; exit 1; }

say "0. Prérequis"
command -v python3 >/dev/null || fail "python3 manquant"
$OPENCLAW --version >/dev/null 2>&1 || fail "OpenClaw introuvable (commande : $OPENCLAW)"
echo "OpenClaw : $($OPENCLAW --version 2>/dev/null | head -1)"
echo "Workspace : $WS"
[ -f "$WS/AGENTS.md" ] || fail "workspace incomplet (AGENTS.md absent)"
[ "$APPLY" = 1 ] || echo "(mode simulation : rien n'est écrit ; relancer avec --apply)"
CFG="$($OPENCLAW config file 2>/dev/null | tail -1 || true)"
if [ "$APPLY" = 1 ] && [ -n "$CFG" ] && [ -f "$CFG" ]; then cp "$CFG" "$CFG.bak-novia-$TS"; echo "sauvegarde de la configuration : $CFG.bak-novia-$TS"; fi

say "1. Fichiers locaux du workspace (jamais écrasés s'ils existent)"
for f in state/approvers.json state/channels.json state/onboarding.json templates/_tokens.json MEMORY.md; do
  if [ ! -f "$WS/$f" ]; then run cp "$WS/$f.example" "$WS/$f"; echo "$f créé depuis l'exemple"; else echo "$f présent"; fi
done
for t in "$WS"/learning/.templates/*.md; do n="$(basename "$t")"; [ -f "$WS/learning/$n" ] || run cp "$t" "$WS/learning/$n"; done
run mkdir -p "$WS/outbox/_metrics" "$WS/memory" "$WS/export"
if grep -q '"123456789"' "$WS/state/approvers.json" 2>/dev/null && [ -z "$ALLOW_EXAMPLES" ]; then
  echo "state/approvers.json contient encore les identifiants d'exemple : à remplacer avant --apply (voir docs/INSTALLATION.md, étape 2)."
  [ "$APPLY" = 1 ] && fail "identifiants d'exemple présents"
fi

say "2. Agent $AGENT (isolé : workspace, état et sessions propres)"
if $OPENCLAW agents list --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); ids=[a.get('id') for a in (d if isinstance(d,list) else d.get('agents',[]))]; sys.exit(0 if '$AGENT' in ids else 1)"; then
  echo "agent déjà déclaré"
else
  if [ -n "$MODEL" ]; then run $OPENCLAW agents add "$AGENT" --workspace "$WS" --model "$MODEL" --non-interactive
  else run $OPENCLAW agents add "$AGENT" --workspace "$WS" --non-interactive; fi
fi

say "3. Configuration (fusion du fragment config/openclaw.novia-com.patch.json5)"
PATCH="$(mktemp -t novia-patch.XXXXXX)"
WITH_TG=""; [ -n "${NOVIA_TELEGRAM_BOT_TOKEN:-}" ] && WITH_TG="--with-telegram"
python3 "$REPO/scripts/prepare_patch.py" "$REPO/config/openclaw.novia-com.patch.json5" "$WS" "$PATCH" $WITH_TG $ALLOW_EXAMPLES || fail "fragment non préparé"
[ -n "$WITH_TG" ] || echo "NOVIA_TELEGRAM_BOT_TOKEN absent de cet environnement : le compte Telegram sera ajouté quand la variable existera (relancer install.sh)."
$OPENCLAW config patch --file "$PATCH" --dry-run >/dev/null && echo "validation du fragment : OK" || fail "fragment refusé par OpenClaw (voir ci-dessus)"
run $OPENCLAW config patch --file "$PATCH"
rm -f "$PATCH"
if [ -n "$WITH_TG" ]; then
  run $OPENCLAW agents bind --agent "$AGENT" --bind "telegram:$AGENT"
  echo "Si OpenClaw signale plusieurs comptes Telegram : $OPENCLAW config set channels.telegram.defaultAccount <votre compte existant>"
fi

say "4. Skills partagés (dossier managé, visibles par tous les agents)"
if [ "$SKIP_SKILLS" = 1 ]; then echo "sauté (--skip-shared-skills)"; else
  for d in "$REPO"/skills-shared/*/; do
    n="$(basename "$d")"
    if $OPENCLAW skills list --json 2>/dev/null | grep -q "\"$n\"" && [ "$UPDATE_SKILLS" = 0 ]; then echo "$n : déjà présent (--update-shared-skills pour rafraîchir)"
    elif [ "$UPDATE_SKILLS" = 1 ]; then run $OPENCLAW skills install "$d" --global --force || echo "$n : à reprendre manuellement"
    else run $OPENCLAW skills install "$d" --global || echo "$n : à reprendre manuellement"; fi
  done
  echo "Les skills novia-* du workspace sont chargés automatiquement. Skills à installer depuis leurs sources publiques : skills-shared/INSTALL.md"
fi

say "5. Crons"
if [ "$SKIP_CRONS" = 1 ]; then echo "sauté (--skip-crons)"
elif [ "$APPLY" = 0 ]; then OPENCLAW="$OPENCLAW" bash "$REPO/crons/install-crons.sh" --dry-run | head -5; echo "…(simulation)"
elif $OPENCLAW cron list >/dev/null 2>&1; then OPENCLAW="$OPENCLAW" bash "$REPO/crons/install-crons.sh"
else echo "gateway non joignable : relancer plus tard « bash crons/install-crons.sh » (puis --enable-p1 après l'onboarding)"; fi

say "6. Vérifications"
if [ "$APPLY" = 1 ]; then
  $OPENCLAW config validate && echo "configuration valide"
  $OPENCLAW agents list 2>/dev/null | grep -i -A2 "$AGENT" || true
  $OPENCLAW skills check --agent "$AGENT" 2>/dev/null | head -12 || true
fi
say "Terminé"
echo "Suite : bash scripts/doctor.sh · $OPENCLAW daemon restart si le gateway tournait déjà · premier message à Novia Com dans Telegram : « Commençons l'onboarding »."
