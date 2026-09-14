#!/usr/bin/env bash
# Installe (ou met à jour) l'agent Novia Com dans OpenClaw. Simulation par défaut ; --apply pour écrire.
# Usage : scripts/install.sh [--apply] [--model <provider/model>] [--skip-shared-skills] [--skip-crons] [--enable-p1]
# Variables : OPENCLAW (commande, défaut « openclaw »), NOVIA_TELEGRAM_BOT_TOKEN (jeton du bot, optionnel à l'installation).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; WS="$REPO/workspace"; AGENT="novia-com"
OPENCLAW="${OPENCLAW:-openclaw}"
APPLY=0; MODEL=""; SKIP_SKILLS=0; SKIP_CRONS=0; ENABLE_P1=0
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1;; --model) MODEL="$2"; shift;; --skip-shared-skills) SKIP_SKILLS=1;; --skip-crons) SKIP_CRONS=1;; --enable-p1) ENABLE_P1=1;;
    -h|--help) sed -n '2,5p' "$0"; exit 0;; *) echo "option inconnue : $1" >&2; exit 1;;
  esac; shift
done
TS="$(date +%Y%m%d-%H%M%S)"
say() { printf '\n== %s\n' "$*"; }
run() { if [ "$APPLY" = 1 ]; then "$@"; else printf '[simulation] %s\n' "$*"; fi; }
fail() { echo "ERREUR : $*" >&2; exit 1; }

say "0. Prérequis"
command -v python3 >/dev/null || fail "python3 manquant"
$OPENCLAW --version >/dev/null 2>&1 || fail "OpenClaw introuvable (commande : $OPENCLAW)"
echo "OpenClaw : $($OPENCLAW --version 2>/dev/null | head -1)"
echo "Workspace : $WS"
[ -f "$WS/AGENTS.md" ] || fail "workspace incomplet (AGENTS.md absent)"
[ "$APPLY" = 1 ] || echo "(mode simulation : rien n'est écrit ; relancer avec --apply)"

say "1. Fichiers d'état du workspace"
for f in approvers channels; do
  if [ ! -f "$WS/state/$f.json" ]; then run cp "$WS/state/$f.json.example" "$WS/state/$f.json"; echo "state/$f.json créé depuis l'exemple : À COMPLÉTER (identifiants Telegram, connecteurs)"; else echo "state/$f.json présent"; fi
done
run mkdir -p "$WS/outbox/_metrics" "$WS/memory"

say "2. Agent $AGENT"
if $OPENCLAW agents list --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); ids=[a.get('id') for a in (d if isinstance(d,list) else d.get('agents',[]))]; sys.exit(0 if '$AGENT' in ids else 1)"; then
  echo "agent déjà déclaré"
else
  if [ -n "$MODEL" ]; then run $OPENCLAW agents add "$AGENT" --workspace "$WS" --model "$MODEL" --non-interactive
  else run $OPENCLAW agents add "$AGENT" --workspace "$WS" --non-interactive; fi
fi

say "3. Telegram (compte de bot dédié)"
if [ -n "${NOVIA_TELEGRAM_BOT_TOKEN:-}" ]; then
  run $OPENCLAW channels add --channel telegram --account "$AGENT" --token "$NOVIA_TELEGRAM_BOT_TOKEN" --name "Novia Com"
  run $OPENCLAW agents bind --agent "$AGENT" --bind "telegram:$AGENT"
else
  echo "NOVIA_TELEGRAM_BOT_TOKEN non défini : étape sautée. Plus tard :"
  echo "  export NOVIA_TELEGRAM_BOT_TOKEN=... && $OPENCLAW channels add --channel telegram --account $AGENT --token \"\$NOVIA_TELEGRAM_BOT_TOKEN\" --name 'Novia Com'"
  echo "  $OPENCLAW agents bind --agent $AGENT --bind telegram:$AGENT"
fi

say "4. Configuration (fusion du fragment config/openclaw.novia-com.patch.json5)"
PATCH="$(mktemp -t novia-patch.XXXXXX)"
python3 - "$REPO/config/openclaw.novia-com.patch.json5" "$WS" "$PATCH" "${NOVIA_TELEGRAM_BOT_TOKEN:-}" <<'PY'
import json, re, sys
src, ws, out, token = sys.argv[1:5]
text = open(src, encoding="utf-8").read().replace("__WORKSPACE__", ws)
# JSON5 minimal → JSON : commentaires // et virgules finales
text = re.sub(r"^\s*//.*$", "", text, flags=re.M); text = re.sub(r"(?m)\s+//[^\n\"]*$", "", text)
text = re.sub(r",(\s*[}\]])", r"\1", text)
text = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_-]*)\s*:", r'\1"\2":', text)
data = json.loads(text)
def load(p):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return {}
approvers = [str(a.get("telegram_id")) for a in load(ws + "/state/approvers.json").get("approvers", []) if a.get("telegram_id") and not str(a.get("telegram_id")).startswith("1234")]
group = load(ws + "/state/channels.json").get("telegram_group_id", "")
import os
env = data.get("skills", {}).get("entries", {}).get("novia-publish", {}).get("env", {})
present = {k: v for k, v in env.items() if os.environ.get(k)}
absent = [k for k in env if k not in present]
if present:
    data["skills"]["entries"]["novia-publish"]["env"] = present
else:
    data["skills"]["entries"]["novia-publish"].pop("env", None)
print("variables de connecteurs injectées : %s" % (", ".join(sorted(present)) or "aucune"))
if absent:
    print("non définies pour l'instant (relancer install.sh après les avoir déclarées) : %s" % ", ".join(absent))
if token:
    acc = data["channels"]["telegram"]["accounts"]["novia-com"]
    acc.pop("botToken", None)  # le jeton est posé par `channels add`
    acc["allowFrom"] = approvers
    acc["groupAllowFrom"] = [group] if group and not group.startswith("-1001234") else []
else:
    data.pop("channels", None)
json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("fragment préparé : %d approbateurs, groupe %s" % (len(approvers), group or "(non renseigné)"))
PY
CFG="$($OPENCLAW config file 2>/dev/null | tail -1 || true)"
if [ "$APPLY" = 1 ] && [ -n "$CFG" ] && [ -f "$CFG" ]; then cp "$CFG" "$CFG.bak-novia-$TS"; echo "sauvegarde : $CFG.bak-novia-$TS"; fi
$OPENCLAW config patch --file "$PATCH" --dry-run >/dev/null && echo "validation du fragment : OK" || fail "le fragment de configuration est refusé par OpenClaw (voir ci-dessus)"
run $OPENCLAW config patch --file "$PATCH"
rm -f "$PATCH"

say "5. Skills partagés (installés pour tous les agents)"
if [ "$SKIP_SKILLS" = 1 ]; then echo "sauté (--skip-shared-skills)"; else
  for d in "$REPO"/skills-shared/*/; do
    n="$(basename "$d")"
    if $OPENCLAW skills list --json 2>/dev/null | grep -q "\"$n\""; then echo "$n : déjà présent"; else run $OPENCLAW skills install "$d" --global || echo "$n : installation à reprendre manuellement ($OPENCLAW skills install $d --global)"; fi
  done
  echo "Les skills novia-* du workspace sont chargés automatiquement (workspace/skills)."
  echo "Skills à installer depuis leurs sources publiques : voir skills-shared/INSTALL.md"
fi

say "6. Crons"
if [ "$SKIP_CRONS" = 1 ]; then echo "sauté (--skip-crons)"; elif [ "$APPLY" = 0 ]; then echo "[simulation] crons/install-crons.sh $( [ "$ENABLE_P1" = 1 ] && echo --enable-p1 )"; elif $OPENCLAW cron list >/dev/null 2>&1; then
  OPENCLAW="$OPENCLAW" bash "$REPO/crons/install-crons.sh" $( [ "$ENABLE_P1" = 1 ] && echo --enable-p1 )
else echo "gateway non joignable : relancer plus tard « bash crons/install-crons.sh » (avec --enable-p1 après l'onboarding)"; fi

say "7. Vérifications"
if [ "$APPLY" = 1 ]; then
  $OPENCLAW config validate && echo "configuration valide"
  $OPENCLAW agents list 2>/dev/null | grep -i "$AGENT" || true
  $OPENCLAW skills check --agent "$AGENT" 2>/dev/null | head -40 || true
fi
say "Terminé"
echo "Suite : bash scripts/doctor.sh · redémarrer le gateway si demandé ($OPENCLAW daemon restart) · premier message à Novia Com dans Telegram : « Commençons l'onboarding »."
