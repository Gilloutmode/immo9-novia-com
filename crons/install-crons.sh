#!/usr/bin/env bash
# Déclare les crons de Novia Com de façon idempotente (clé de déclaration novia-com:<key>).
# Usage : install-crons.sh [--enable-p1] [--dry-run]
# Nécessite un gateway OpenClaw démarré (les crons sont gérés via le gateway).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$HERE/.." && pwd)"; WS="$REPO/workspace"
OPENCLAW="${OPENCLAW:-openclaw}"
ENABLE_P1=0; DRY=0
for a in "$@"; do case "$a" in --enable-p1) ENABLE_P1=1;; --dry-run) DRY=1;; *) echo "option inconnue : $a" >&2; exit 1;; esac; done
GROUP="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('telegram_group_id',''))" "$WS/state/channels.json" 2>/dev/null || true)"
if [ -z "$GROUP" ]; then echo "state/channels.json : telegram_group_id manquant (les crons livrent leur sortie dans ce groupe)" >&2; exit 1; fi
python3 - "$HERE/crons.json" "$GROUP" "$ENABLE_P1" "$DRY" <<'PY' | while IFS= read -r line; do
import json, shlex, sys
spec = json.load(open(sys.argv[1])); group = sys.argv[2]; enable_p1 = sys.argv[3] == "1"; dry = sys.argv[4] == "1"
for j in spec["jobs"]:
    disabled = not (enable_p1 and j["palier"] == 1)
    msg = spec["preamble"] + "\n\n" + j["message"]
    cmd = ["cron", "add", "--name", j["name"], "--cron", j["cron"], "--tz", spec["timezone"], "--agent", spec["agent"],
           "--message", msg, "--declaration-key", "novia-com:" + j["key"], "--description", j["description"],
           "--session", "isolated", "--announce", "--channel", "telegram", "--to", group,
           "--timeout-seconds", str(j.get("timeout_seconds", 900))]
    if disabled:
        cmd.append("--disabled")
    print(" ".join(shlex.quote(c) for c in cmd))
PY
  if [ "$DRY" = 1 ]; then echo "$OPENCLAW $line" | cut -c1-160; else eval "$OPENCLAW $line" >/dev/null && echo "✓ $(echo "$line" | sed -n 's/.*--declaration-key \([^ ]*\).*/\1/p')"; fi
done
echo "Crons déclarés (palier 1 $( [ "$ENABLE_P1" = 1 ] && echo activé || echo désactivé ) · palier 2 désactivé). Vérifier : $OPENCLAW cron list"
