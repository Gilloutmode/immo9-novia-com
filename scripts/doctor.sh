#!/usr/bin/env bash
# Diagnostic de l'installation Novia Com : outils, fichiers, configuration, skills, flux. Lecture seule.
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; WS="$REPO/workspace"; AGENT="novia-com"; OPENCLAW="${OPENCLAW:-openclaw}"
ok=0; ko=0; warn=0
pass() { printf '✓ %s\n' "$*"; ok=$((ok+1)); }
fail() { printf '✗ %s\n' "$*"; ko=$((ko+1)); }
note() { printf '! %s\n' "$*"; warn=$((warn+1)); }
echo "== Outils"
for b in python3 ffmpeg ffprobe; do command -v "$b" >/dev/null && pass "$b : $(command -v "$b")" || fail "$b manquant"; done
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)' && pass "python3 $(python3 -c 'import sys;print(".".join(map(str,sys.version_info[:3])))')" || fail "python3 >= 3.8 requis"
for b in chromium chromium-browser google-chrome google-chrome-stable; do command -v "$b" >/dev/null && { pass "navigateur headless : $b"; BROWSER=1; break; }; done
[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && { pass "navigateur headless : Google Chrome (macOS)"; BROWSER=1; }
[ "${BROWSER:-0}" = 1 ] || note "aucun Chromium : rendu des carrousels via l'outil browser d'OpenClaw ou installer chromium (apt install chromium)"
command -v node >/dev/null && pass "node $(node --version)" || note "node absent (nécessaire pour hyperframes et supermonteur)"
$OPENCLAW --version >/dev/null 2>&1 && pass "OpenClaw $($OPENCLAW --version 2>/dev/null | head -1)" || fail "OpenClaw introuvable ($OPENCLAW)"
echo "== Workspace"
for f in AGENTS.md SOUL.md IDENTITY.md TEAM.md HEARTBEAT.md BOOT.md doctrine/STUDIO_CONTRACT.json doctrine/LINES.md doctrine/VOICE.md; do [ -f "$WS/$f" ] && pass "$f" || fail "$f absent"; done
for f in state/onboarding.json state/approvers.json state/channels.json templates/_tokens.json knowledge/sources-veille.json knowledge/calendrier-marronniers.json; do
  if [ -f "$WS/$f" ]; then python3 -c "import json;json.load(open('$WS/$f'))" 2>/dev/null && pass "$f valide" || fail "$f : JSON invalide"; else fail "$f absent (copier depuis l'exemple)"; fi
done
grep -q '"status": "complete"' "$WS/state/onboarding.json" 2>/dev/null && pass "onboarding : complete" || note "onboarding : $(python3 -c "import json;print(json.load(open('$WS/state/onboarding.json'))['status'])" 2>/dev/null) (production verrouillée jusqu'à complete)"
grep -q '\[À REMPLIR\]' "$WS/TEAM.md" && note "TEAM.md contient encore des [À REMPLIR]" || pass "TEAM.md renseigné"
python3 -c "import json;t=json.load(open('$WS/templates/_tokens.json'));import sys;sys.exit(0 if t.get('color_primary') else 1)" 2>/dev/null && pass "charte : tokens renseignés" || note "charte : templates/_tokens.json vide (acte 3)"
echo "== Variables d'environnement (présence seulement)"
for v in NOVIA_TELEGRAM_BOT_TOKEN UPLOAD_POST_API_KEY META_PAGE_ACCESS_TOKEN LINKEDIN_ACCESS_TOKEN BREVO_API_KEY REDDIT_CLIENT_ID; do [ -n "${!v:-}" ] && pass "$v défini" || note "$v non défini dans cet environnement (normal si porté par le service du gateway)"; done
echo "== OpenClaw"
if $OPENCLAW agents list --json 2>/dev/null | grep -q "\"$AGENT\""; then pass "agent $AGENT déclaré"; else fail "agent $AGENT absent (scripts/install.sh --apply)"; fi
$OPENCLAW config validate >/dev/null 2>&1 && pass "configuration valide" || fail "configuration invalide ($OPENCLAW config validate)"
if $OPENCLAW skills check --agent "$AGENT" >/dev/null 2>&1; then
  missing="$($OPENCLAW skills check --agent "$AGENT" 2>/dev/null | grep -i -E 'missing|manqu' | head -5 || true)"
  [ -z "$missing" ] && pass "skills : aucune dépendance manquante signalée" || note "skills : $missing"
else note "skills check indisponible (agent absent ou gateway arrêté)"; fi
$OPENCLAW cron list >/dev/null 2>&1 && pass "gateway joignable (crons listables)" || note "gateway non joignable : crons non vérifiés"
echo "== Flux de veille (réseau)"
NOVIA_WORKSPACE="$WS" python3 - <<'PY'
import json, os, urllib.request
ws=os.environ["NOVIA_WORKSPACE"]; cfg=json.load(open(ws+"/knowledge/sources-veille.json")); ok=ko=0
for s in cfg["sources"]:
    if not s.get("rss"): continue
    try:
        req=urllib.request.Request(s["rss"], headers={"User-Agent":"Mozilla/5.0 (compatible; NoviaCom/1.0)"})
        with urllib.request.urlopen(req, timeout=12) as r:
            body=r.read(400).decode("utf-8","ignore")
            if "<rss" in body or "<feed" in body or "<?xml" in body: ok+=1
            else: ko+=1; print("! %s : réponse non XML" % s["name"])
    except Exception as e:
        ko+=1; print("! %s : %s" % (s["name"], str(e)[:60]))
print("flux joignables : %d, en échec : %d" % (ok, ko))
PY
echo; echo "Bilan : $ok OK · $warn avertissements · $ko erreurs"
[ "$ko" = 0 ]
