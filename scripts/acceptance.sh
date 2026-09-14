#!/usr/bin/env bash
# Tests d'acceptation hors ligne de Novia Com : aucun appel réseau, aucune écriture dans le dépôt.
# Copie le workspace dans un dossier temporaire et vérifie l'hygiène du dépôt, les scripts, les verrous d'approbation,
# de publication et d'onboarding, la génération de la configuration Telegram et des crons.
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; T="$(mktemp -d -t novia-acc.XXXXXX)"; cp -R "$REPO/workspace" "$T/ws"; export NOVIA_WORKSPACE="$T/ws"; cd "$T/ws" || exit 1
for f in approvers channels onboarding; do cp "state/$f.json.example" "state/$f.json"; done
cp templates/_tokens.json.example templates/_tokens.json; cp MEMORY.md.example MEMORY.md; cp learning/.templates/*.md learning/
pass=0; fail=0
t() { local name="$1"; shift; if "$@" >/dev/null 2>&1; then printf '✓ %s\n' "$name"; pass=$((pass+1)); else printf '✗ %s\n' "$name"; fail=$((fail+1)); fi; }
tr_() { local name="$1"; shift; local out; out="$("$@" 2>&1)"; local rc=$?; if [ $rc -ne 0 ] && printf '%s' "$out" | grep -q 'REFUS'; then printf '✓ %s\n' "$name"; pass=$((pass+1)); else printf '✗ %s (attendu : REFUS, obtenu rc=%s : %s)\n' "$name" "$rc" "$(printf '%s' "$out" | tail -1 | cut -c1-80)"; fail=$((fail+1)); fi; }
grep_none() { grep -rIlE --exclude-dir=.git --exclude-dir=node_modules "$1" "$REPO"; local rc=$?; [ $rc -eq 1 ]; }
set_status() { python3 - "$1" "$2" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["status"]=sys.argv[2]; m["approvals"]["go2"]=None; json.dump(m,open(p,"w"))
PY
}
set_onboarding() { python3 - "$1" <<'PY'
import json,sys; json.dump({"status": sys.argv[1], "history": []}, open("state/onboarding.json","w"))
PY
}
echo "== Hygiène du dépôt"
t "aucun chemin personnel (/Users/ ou /home/)" grep_none '/Users/[a-z]+/|/home/[a-z]+/'
t "aucun secret apparent" grep_none 'sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY|[0-9]{9,10}:AA[A-Za-z0-9_-]{30,}'
t "aucun tiret long" grep_none "$(printf '\xe2\x80\x94')"
t "JSON et exemples valides" bash -c "for f in \$(find '$T/ws' '$REPO/crons' -name '*.json' -o -name '*.example' | grep -v node_modules | grep -v MEMORY); do python3 -c \"import json,sys;json.load(open(sys.argv[1]))\" \"\$f\" || exit 1; done"
t "scripts Python compilent (copie)" bash -c "python3 -m py_compile \$(find '$T/ws/skills' -name '*.py') '$REPO/crons/install_crons.py' '$REPO/scripts/prepare_patch.py'"
t "scripts shell valides" bash -c "for f in \$(find '$REPO' -name '*.sh' -not -path '*/node_modules/*'); do bash -n \"\$f\" || exit 1; done"
t "chaque SKILL.md a name et description" bash -c "for f in '$REPO'/workspace/skills/*/SKILL.md '$REPO'/skills-shared/*/SKILL.md; do grep -q '^name:' \"\$f\" && grep -q '^description:' \"\$f\" || exit 1; done"
echo "== Configuration et crons (génération, sans gateway)"
t "fragment Telegram : botToken en SecretRef, groupe dans groups, personnes en allowlist" bash -c "python3 '$REPO/scripts/prepare_patch.py' '$REPO/config/openclaw.novia-com.patch.json5' '$T/ws' '$T/patch.json' --with-telegram --allow-example-ids >/dev/null && python3 -c \"
import json,sys; d=json.load(open('$T/patch.json')); a=d['channels']['telegram']['accounts']['novia-com']
assert a['botToken']=={'source':'env','provider':'default','id':'NOVIA_TELEGRAM_BOT_TOKEN'}; assert '-1001234567890' in a['groups']; assert a['groups']['-1001234567890']['requireMention'] is False
assert '123456789' in a['allowFrom'] and '123456789' in a['groupAllowFrom']; assert 'userTimezone' not in d['agents']['entries']['novia-com']\""
tr_ "fragment refusé avec les identifiants d'exemple" python3 "$REPO/scripts/prepare_patch.py" "$REPO/config/openclaw.novia-com.patch.json5" "$T/ws" "$T/patch2.json" --with-telegram
t "variables absentes non injectées" bash -c "env -u UPLOAD_POST_API_KEY -u BREVO_API_KEY python3 '$REPO/scripts/prepare_patch.py' '$REPO/config/openclaw.novia-com.patch.json5' '$T/ws' '$T/patch3.json' --allow-example-ids >/dev/null && python3 -c \"import json; d=json.load(open('$T/patch3.json')); assert 'env' not in d['skills']['entries']['novia-publish'] or not d['skills']['entries']['novia-publish']['env']\""
t "crons : 12 commandes générées, une par job, sans découpe" bash -c "cd '$T/ws' && OPENCLAW=openclaw python3 '$REPO/crons/install_crons.py' --dry-run | grep -c 'cron add' | grep -qx 12"
echo "== Verrou d'onboarding"
ID="$(python3 skills/novia-outbox/scripts/outbox_new.py --format F1 --persona P1 --channel linkedin --title "Test" --source https://example.org)"
tr_ "présentation refusée avant l'acte 4" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90
set_onboarding act4_calibration
tr_ "package final refusé sans conformité consignée" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["linkedin"]="Test. Source : https://example.org"; m["quality"]["compliance_checked"]=True; json.dump(m,open(p,"w"))
PY
tr_ "package final refusé sous le score minimum" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 70
t "présentation du package final (score 90, conformité, légende)" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90 --card-id 4242
echo "== Approbation"
tr_ "refusée : personne non autorisée" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 999 --text "Go publie"
tr_ "refusée : pouce" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "👍"
tr_ "refusée : ok seul" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "ok"
tr_ "refusée : négation" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "ne publie rien"
tr_ "refusée : question" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "est-ce que je publie ?"
tr_ "refusée : condition" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "Go publie si David confirme"
tr_ "refusée : mot noyé dans une phrase" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "je te dis go publie"
tr_ "refusée : réponse à un autre message que la carte" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "Go publie" --reply-to 9999
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["linkedin"]="Texte modifié après présentation"; json.dump(m,open(p,"w"))
PY
tr_ "refusée : package modifié après présentation" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "Go publie" --reply-to 4242
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["linkedin"]="Test. Source : https://example.org"; json.dump(m,open(p,"w"))
PY
t "acceptée : formule en tête, personne autorisée, réponse à la carte" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "Go publie" --reply-to 4242 --message-id 4300
echo "== Publication"
tr_ "refusée : onboarding non terminé" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run
set_onboarding complete
t "aperçu sans approbation ni envoi" python3 skills/novia-publish/scripts/publish.py "$ID" --preview
tr_ "refusée : canal non approuvé" python3 skills/novia-publish/scripts/publish.py "$ID" --channel instagram --dry-run
t "simulation après Go publie" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run
t "la simulation ne compte pas comme publication" bash -c "python3 -c \"import json; m=json.load(open('outbox/$ID/manifest.json')); assert m['status']=='approved' and not m['publication']['results']\""
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["linkedin"]="Modifié après approbation"; json.dump(m,open(p,"w"))
PY
tr_ "refusée : package modifié après approbation" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["linkedin"]="Test. Source : https://example.org"; json.dump(m,open(p,"w"))
PY
t "échec explicite : connecteur non configuré (clé absente)" bash -c "out=\$(env -u UPLOAD_POST_API_KEY python3 skills/novia-publish/scripts/publish.py '$ID' 2>&1); rc=\$?; [ \$rc -ne 0 ] && echo \"\$out\" | grep -qE 'REFUS|ÉCHEC'"
touch "outbox/$ID/.publish.lock"; tr_ "refusée : publication déjà en cours (verrou)" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run; rm -f "outbox/$ID/.publish.lock"
ID2="$(python3 skills/novia-outbox/scripts/outbox_new.py --format F1 --persona P1 --channel linkedin --title "Test calibration")"
python3 - "outbox/$ID2/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["linkedin"]="Test. Source : https://example.org"; m["quality"]["compliance_checked"]=True; json.dump(m,open(p,"w"))
PY
python3 skills/novia-outbox/scripts/outbox_present.py "$ID2" --stage final --score 90 --test >/dev/null
tr_ "pièce test de calibration jamais approuvable pour publication" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID2" --stage go2 --by 123456789 --text "Go publie"
echo "== Contrôles éditoriaux"
t "légende conforme acceptée" python3 skills/novia-editorial/scripts/caption_check.py --channel linkedin --persona P1 --text "Vous achetez à Toulouse ? Selon service-public.fr (2026), le PTZ finance une partie du prix."
tr_() { local name="$1"; shift; if "$@" >/dev/null 2>&1; then printf '✗ %s (aurait dû échouer)\n' "$name"; fail=$((fail+1)); else printf '✓ %s\n' "$name"; pass=$((pass+1)); fi; }
tr_ "promesse de rendement refusée" python3 skills/novia-editorial/scripts/caption_check.py --channel linkedin --persona P2 --text "Rendement garanti de 5 % selon nous."
tr_ "urgence fabriquée refusée" python3 skills/novia-editorial/scripts/caption_check.py --channel instagram --text "Dernières unités disponibles."
tr_ "tutoiement refusé" python3 skills/novia-editorial/scripts/caption_check.py --channel facebook --text "Tu veux acheter ? Source : https://x.fr"
echo "== Production"
cat > "outbox/$ID/carousel.json" <<'J'
{"id":"t","persona":"P1","slides":[{"title":"A","body":"a","cover":true},{"title":"B","body":"b"},{"title":"C","body":"c"},{"title":"D","body":"d"},{"title":"E","body":"e","last":true}],"footer":{"source":"s"}}
J
t "carrousel construit (5 slides)" python3 skills/novia-carousel/scripts/carousel_build.py "outbox/$ID/carousel.json"
tr_ "infographie refusée sans données sourcées" python3 skills/novia-infographie/scripts/infographie_build.py --out "outbox/$ID/i.html"
cat > "outbox/$ID/nl.json" <<'J'
{"subject":"Objet de test raisonnable","persona":"P2","intro":"Bonjour.","sections":[{"title":"T","body":"Corps."}],"footer":{"address":"Adresse","unsubscribe_url":"{{ unsubscribe }}"}}
J
t "newsletter avec mention des risques (P2) et sans %% résiduel" bash -c "python3 skills/novia-newsletter/scripts/newsletter_build.py 'outbox/$ID/nl.json' && grep -q risques 'outbox/$ID/newsletter.html' && ! grep -q '%%' 'outbox/$ID/newsletter.html'"
cat > "outbox/$ID/nl2.json" <<'J'
{"subject":"Objet de test raisonnable","persona":"P1","intro":"Bonjour.","sections":[{"title":"T","body":"Corps."}],"footer":{"address":"Adresse"}}
J
tr_ "newsletter refusée sans lien de désinscription" python3 skills/novia-newsletter/scripts/newsletter_build.py "outbox/$ID/nl2.json"
t "calendrier lisible" python3 skills/novia-calendrier/scripts/calendrier_next.py --days 60
if command -v ffmpeg >/dev/null; then
  ffmpeg -y -loglevel error -f lavfi -i color=c=gray:s=800x600 -frames:v 1 "outbox/$ID/m.png"
  t "déclinaison image (4 formats)" bash -c "bash skills/novia-declinaison/scripts/declinaison.sh 'outbox/$ID/m.png' 'outbox/$ID/d' && [ \$(ls outbox/$ID/d | wc -l) -eq 4 ]"
fi
echo "== Onboarding (états)"
set_onboarding act0_diagnostic
tr_ "passage à complete refusé tant que l'onboarding n'est pas fait" python3 skills/novia-onboarding/scripts/onboarding_state.py --set complete
tr_ "--check signale les conditions manquantes (code 1)" python3 skills/novia-onboarding/scripts/onboarding_state.py --check
t "avancement séquentiel accepté" python3 skills/novia-onboarding/scripts/onboarding_state.py --set act1_identite_equipe
tr_ "saut d'acte refusé" python3 skills/novia-onboarding/scripts/onboarding_state.py --set act4_calibration
rm -rf "$T"
echo; echo "Résultat : $pass réussis, $fail échoués"
[ "$fail" = 0 ]
