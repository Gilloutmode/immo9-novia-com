#!/usr/bin/env bash
# Tests d'acceptation hors ligne de Novia Com : aucun appel réseau, aucune écriture dans le dépôt.
# Copie le dépôt (sans .git) dans un dossier temporaire et y vérifie : hygiène, scripts, verrous d'approbation, de publication
# et d'onboarding, génération de la configuration Telegram, déclaration et activation des crons (OpenClaw simulé), reprise.
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; T="$(mktemp -d -t novia-acc.XXXXXX)"
mkdir -p "$T/repo" && (cd "$REPO" && tar --exclude=.git --exclude=node_modules --exclude='__pycache__' -cf - .) | (cd "$T/repo" && tar -xf -)
R="$T/repo"; WS="$R/workspace"; export NOVIA_WORKSPACE="$WS"; cd "$WS" || exit 1
for f in approvers channels onboarding; do cp "state/$f.json.example" "state/$f.json"; done
cp templates/_tokens.json.example templates/_tokens.json; cp MEMORY.md.example MEMORY.md; cp learning/.templates/*.md learning/
pass=0; fail=0
t() { local name="$1"; shift; if "$@" >/dev/null 2>&1; then printf '✓ %s\n' "$name"; pass=$((pass+1)); else printf '✗ %s\n' "$name"; fail=$((fail+1)); fi; }
tr_() { local name="$1"; shift; local out; out="$("$@" 2>&1)"; local rc=$?; if [ $rc -ne 0 ] && printf '%s' "$out" | grep -qE 'REFUS|ÉCHEC'; then printf '✓ %s\n' "$name"; pass=$((pass+1)); else printf '✗ %s (attendu : refus, obtenu rc=%s : %s)\n' "$name" "$rc" "$(printf '%s' "$out" | tail -1 | cut -c1-90)"; fail=$((fail+1)); fi; }
tf() { local name="$1"; shift; if "$@" >/dev/null 2>&1; then printf '✗ %s (aurait dû échouer)\n' "$name"; fail=$((fail+1)); else printf '✓ %s\n' "$name"; pass=$((pass+1)); fi; }
grep_none() { grep -rIlE --exclude-dir=.git --exclude-dir=node_modules "$1" "$R"; local rc=$?; [ $rc -eq 1 ]; }
set_status() { python3 - "$1" "$2" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["status"]=sys.argv[2]; m["approvals"]["go2"]=None; json.dump(m,open(p,"w"))
PY
}
set_onboarding() { python3 - "$1" <<'PY'
import json,sys; json.dump({"status": sys.argv[1], "history": []}, open("state/onboarding.json","w"))
PY
}
set_caption() { python3 - "$1" "$2" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["linkedin"]=sys.argv[2]; m["quality"]["compliance_checked"]=True; json.dump(m,open(p,"w"))
PY
}
APPROVE=(python3 skills/novia-outbox/scripts/outbox_approve.py)
echo "== Hygiène du dépôt"
t "aucun chemin personnel (/Users/ ou /home/)" grep_none '/Users/[a-z]+/|/home/[a-z]+/'
t "aucun secret apparent" grep_none 'sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY|[0-9]{9,10}:AA[A-Za-z0-9_-]{30,}'
t "aucun tiret long" grep_none "$(printf '\xe2\x80\x94')"
t "JSON et exemples valides" bash -c "for f in \$(find '$WS' '$R/crons' -name '*.json' -o -name '*.example' | grep -v MEMORY); do python3 -c \"import json,sys;json.load(open(sys.argv[1]))\" \"\$f\" || exit 1; done"
t "scripts Python compilent (copie)" bash -c "python3 -m py_compile \$(find '$R' -name '*.py')"
t "scripts shell valides (copie)" bash -c "for f in \$(find '$R' -name '*.sh'); do bash -n \"\$f\" || exit 1; done"
t "chaque SKILL.md a name et description" bash -c "for f in '$WS'/skills/*/SKILL.md '$R'/skills-shared/*/SKILL.md; do grep -q '^name:' \"\$f\" && grep -q '^description:' \"\$f\" || exit 1; done"
echo "== Configuration Telegram (génération)"
t "fragment : botToken en SecretRef, groupe dans groups, personnes en allowlist, pas de userTimezone" bash -c "python3 '$R/scripts/prepare_patch.py' '$R/config/openclaw.novia-com.patch.json5' '$WS' '$T/patch.json' --with-telegram --allow-example-ids >/dev/null && python3 -c \"
import json; d=json.load(open('$T/patch.json')); a=d['channels']['telegram']['accounts']['novia-com']
assert a['botToken']=={'source':'env','provider':'default','id':'NOVIA_TELEGRAM_BOT_TOKEN'}; assert list(a['groups'])==['-1001234567890']; assert a['groups']['-1001234567890']['requireMention'] is False
assert '123456789' in a['allowFrom'] and '123456789' in a['groupAllowFrom']; assert 'userTimezone' not in d['agents']['entries']['novia-com']\""
tr_ "fragment refusé avec les identifiants d'exemple" python3 "$R/scripts/prepare_patch.py" "$R/config/openclaw.novia-com.patch.json5" "$WS" "$T/patch2.json" --with-telegram
t "variables absentes non injectées" bash -c "env -u UPLOAD_POST_API_KEY -u BREVO_API_KEY -u REDDIT_CLIENT_ID python3 '$R/scripts/prepare_patch.py' '$R/config/openclaw.novia-com.patch.json5' '$WS' '$T/patch3.json' --allow-example-ids >/dev/null && python3 -c \"import json; d=json.load(open('$T/patch3.json')); assert not d['skills']['entries']['novia-publish'].get('env')\""
echo "== Crons (OpenClaw simulé)"
mkdir -p "$T/bin"; cat > "$T/bin/openclaw" <<'PY'
#!/usr/bin/env python3
import json, os, sys, uuid
state = os.environ["FAKE_CRON_STATE"]; a = sys.argv[1:]
jobs = json.load(open(state)) if os.path.exists(state) else []
def save(): json.dump(jobs, open(state, "w"))
if a[:2] == ["cron", "list"]:
    if os.environ.get("FAKE_CRON_DROP_FINAL"):  # simule une disparition des jobs à la 3e lecture
        c = int(os.environ.get("FAKE_CRON_CALLS", "0")) + 1; os.environ["FAKE_CRON_CALLS"] = str(c)
        cnt = state + ".calls"; n = int(open(cnt).read()) + 1 if os.path.exists(cnt) else 1; open(cnt, "w").write(str(n))
        if n >= 3: print(json.dumps({"jobs": []})); sys.exit(0)
    print(json.dumps({"jobs": jobs if "--all" in a else [j for j in jobs if j["enabled"]]})); sys.exit(0)
if a[:2] == ["cron", "add"]:
    key = a[a.index("--declaration-key") + 1]; name = a[a.index("--name") + 1]
    if "\n" in " ".join(a[:3]): sys.exit(2)
    if not any(j["declarationKey"] == key for j in jobs):
        jobs.append({"id": str(uuid.uuid4()), "name": name, "declarationKey": key, "enabled": "--disabled" not in a}); save()
    sys.exit(0)
if a[:2] in (["cron", "enable"], ["cron", "disable"]):
    for j in jobs:
        if j["id"] == a[2]: j["enabled"] = (a[1] == "enable")
    save(); sys.exit(0)
sys.exit(0)
PY
chmod +x "$T/bin/openclaw"; export FAKE_CRON_STATE="$T/cronstate.json"
t "déclaration : 12 jobs créés désactivés, une commande par job" bash -c "OPENCLAW='$T/bin/openclaw' python3 '$R/crons/install_crons.py' >/dev/null && python3 -c \"import json; j=json.load(open('$FAKE_CRON_STATE')); assert len(j)==12 and not any(x['enabled'] for x in j)\""
t "redéclaration : aucun doublon" bash -c "OPENCLAW='$T/bin/openclaw' python3 '$R/crons/install_crons.py' >/dev/null && python3 -c \"import json; assert len(json.load(open('$FAKE_CRON_STATE')))==12\""
t "--enable-p1 : 7 jobs actifs, 5 désactivés, retrouvés malgré leur état" bash -c "OPENCLAW='$T/bin/openclaw' python3 '$R/crons/install_crons.py' --enable-p1 >/dev/null && python3 -c \"import json; j=json.load(open('$FAKE_CRON_STATE')); assert sum(1 for x in j if x['enabled'])==7\""
t "--disable-all : 0 actif" bash -c "OPENCLAW='$T/bin/openclaw' python3 '$R/crons/install_crons.py' --disable-all >/dev/null && python3 -c \"import json; j=json.load(open('$FAKE_CRON_STATE')); assert sum(1 for x in j if x['enabled'])==0\""
tf "job disparu à la vérification finale : échec signalé" bash -c "OPENCLAW='$T/bin/openclaw' FAKE_CRON_DROP_FINAL=1 python3 '$R/crons/install_crons.py' --enable-p1"
echo "== Verrou d'onboarding et présentation"
ID="$(python3 skills/novia-outbox/scripts/outbox_new.py --format F1 --persona P1 --channel linkedin --title "Test" --source https://example.org)"
tr_ "présentation refusée avant l'acte 4" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90
set_onboarding act4_calibration
tr_ "package final refusé sans conformité consignée" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90
set_caption "outbox/$ID/manifest.json" "Test. Source : https://example.org"
tr_ "package final refusé sous le score minimum" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 70
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["assets"]=[{"file":"absent.png"}]; json.dump(m,open(p,"w"))
PY
tr_ "package final refusé avec un fichier déclaré absent" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["assets"]=[]; json.dump(m,open(p,"w"))
PY
tr_ "carte refusée sans son chat" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90 --card-id 4242
t "présentation du package final (score 90, conformité, légende)" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90
t "carte enregistrée après envoi (chat du groupe, message 4242)" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --card-only --card-id 4242 --card-chat-id -1001234567890
echo "== Approbation"
OK=(--reply-to 4242 --message-id 4300 --chat-id -1001234567890)
tr_ "refusée : personne non autorisée" "${APPROVE[@]}" "$ID" --stage go2 --by 999 --text "Go publie" "${OK[@]}"
tr_ "refusée : pouce" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "👍" "${OK[@]}"
tr_ "refusée : ok seul" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "ok" "${OK[@]}"
tr_ "refusée : négation" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "ne publie rien" "${OK[@]}"
tr_ "refusée : question" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "est-ce que je publie ?" "${OK[@]}"
tr_ "refusée : condition (si)" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie si David confirme" "${OK[@]}"
tr_ "refusée : condition (à moins que)" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie, à moins que David refuse" "${OK[@]}"
tr_ "refusée : formule suivie de texte libre" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie sur LinkedIn mardi 8h30" "${OK[@]}"
tr_ "refusée : mot noyé dans une phrase" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "je te dis go publie" "${OK[@]}"
tr_ "refusée : sans identifiants Telegram" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie"
tr_ "refusée : réponse à un autre message que la carte" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie" --reply-to 9999 --message-id 4300 --chat-id -1001234567890
tr_ "refusée : chat inconnu" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie" --reply-to 4242 --message-id 4300 --chat-id 55555
tr_ "refusée : même numéro de message mais autre chat autorisé (DM)" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie" --reply-to 4242 --message-id 4300 --chat-id 123456789
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["subject"]="Objet B"; json.dump(m,open(p,"w"))
PY
tr_ "refusée : objet de newsletter modifié après présentation" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie" "${OK[@]}"
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"].pop("subject",None); json.dump(m,open(p,"w"))
PY
t "formule du contrat avec trait d'union acceptée (Go 1 : « on part là-dessus »)" bash -c "python3 skills/novia-outbox/scripts/outbox_present.py '$ID' --stage go1 >/dev/null && python3 skills/novia-outbox/scripts/outbox_present.py '$ID' --card-only --card-id 4242 --card-chat-id -1001234567890 >/dev/null && python3 skills/novia-outbox/scripts/outbox_approve.py '$ID' --stage go1 --by 123456789 --text 'On part là-dessus' --reply-to 4242 --message-id 4301 --chat-id -1001234567890"
t "nouvelle présentation : ancienne carte et approbations invalidées" bash -c "python3 skills/novia-outbox/scripts/outbox_present.py '$ID' --stage final --score 90 >/dev/null && python3 -c \"import json; m=json.load(open('outbox/$ID/manifest.json')); assert m['card_message_id'] is None and m['approvals']['go1'] is None\""
t "carte enregistrée à nouveau" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --card-only --card-id 4242 --card-chat-id -1001234567890
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["title"]="Titre modifié après présentation"; json.dump(m,open(p,"w"))
PY
tr_ "refusée : titre modifié après présentation" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie" "${OK[@]}"
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["title"]="Test"; m["persona"]="P2"; json.dump(m,open(p,"w"))
PY
tr_ "refusée : persona modifiée après présentation" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie" "${OK[@]}"
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["persona"]="P1"; json.dump(m,open(p,"w"))
PY
t "acceptée : « Go publie ! » seul, personne autorisée, réponse à la carte, chat du groupe" "${APPROVE[@]}" "$ID" --stage go2 --by 123456789 --text "Go publie !" "${OK[@]}"
echo "== Publication"
tr_ "refusée : onboarding non terminé" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run
set_onboarding complete
t "aperçu sans approbation ni envoi" python3 skills/novia-publish/scripts/publish.py "$ID" --preview
tr_ "refusée : canal non approuvé" python3 skills/novia-publish/scripts/publish.py "$ID" --channel instagram --dry-run
t "simulation après Go publie" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run
t "la simulation ne compte pas comme publication" python3 -c "import json; m=json.load(open('outbox/$ID/manifest.json')); assert m['status']=='approved' and not m['publication']['results']"
set_caption "outbox/$ID/manifest.json" "Modifié après approbation"
tr_ "refusée : package modifié après approbation" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run
set_caption "outbox/$ID/manifest.json" "Test. Source : https://example.org"
tr_ "échec explicite : connecteur non configuré (clé absente)" env -u UPLOAD_POST_API_KEY python3 skills/novia-publish/scripts/publish.py "$ID"
touch "outbox/$ID/.publish.lock"; tr_ "refusée : publication déjà en cours (verrou avant lecture)" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run; rm -f "outbox/$ID/.publish.lock"
cat > skills/novia-publish/adapters/fake_submitted.py <<'PY'
def publish(channel, settings, caption, assets, manifest):
    return {"state": "submitted", "id": "req-123", "url": None}
PY
python3 - <<'PY'
import json; c=json.load(open("state/channels.json")); c["channels"]["linkedin"]={"adapter":"fake_submitted"}; json.dump(c,open("state/channels.json","w"))
PY
t "envoi accepté par le prestataire : statut submitted, résultat et ledger enregistrés" bash -c "python3 skills/novia-publish/scripts/publish.py '$ID' >/dev/null && python3 -c \"import json; m=json.load(open('outbox/$ID/manifest.json')); assert m['status']=='submitted'; r=m['publication']['results']; assert len(r)==1 and r[0]['state']=='submitted' and r[0].get('idempotency_key')\" && grep -q 'soumise' learning/CONTENT_LEDGER.md"
t "reprise : une cible en attente n'est pas resoumise" bash -c "python3 skills/novia-publish/scripts/publish.py '$ID' | grep -q 'déjà soumis' && python3 -c \"import json; m=json.load(open('outbox/$ID/manifest.json')); assert len(m['publication']['results'])==1\""
t "cible répétée sur la ligne de commande : un seul envoi" bash -c "python3 skills/novia-publish/scripts/publish.py '$ID' --channel linkedin --channel linkedin | grep -c 'déjà soumis' | grep -qx 1"
t "réparation des traces : ligne de ledger absente régénérée à la reprise" bash -c "sed -i.bak '/soumise/d' learning/CONTENT_LEDGER.md && python3 skills/novia-publish/scripts/publish.py '$ID' >/dev/null; grep -q 'soumise' learning/CONTENT_LEDGER.md"
ID3="$(python3 skills/novia-outbox/scripts/outbox_new.py --format F1 --persona P1 --channel linkedin --title "Test timeout")"
set_caption "outbox/$ID3/manifest.json" "Test. Source : https://example.org"
python3 skills/novia-outbox/scripts/outbox_present.py "$ID3" --stage final --score 90 >/dev/null && python3 skills/novia-outbox/scripts/outbox_present.py "$ID3" --card-only --card-id 7 --card-chat-id -1001234567890 >/dev/null
"${APPROVE[@]}" "$ID3" --stage go2 --by 123456789 --text "Go publie" --reply-to 7 --message-id 8 --chat-id -1001234567890 >/dev/null
cat > skills/novia-publish/adapters/fake_timeout.py <<'PY'
def publish(channel, settings, caption, assets, manifest):
    raise TimeoutError("réponse perdue après envoi")
PY
python3 - <<'PY'
import json; c=json.load(open("state/channels.json")); c["channels"]["linkedin"]={"adapter":"fake_timeout"}; json.dump(c,open("state/channels.json","w"))
PY
tr_ "réponse perdue après envoi : échec rapporté, issue inconnue conservée" python3 skills/novia-publish/scripts/publish.py "$ID3"
t "issue inconnue : tentative conservée dans le manifest et tracée" bash -c "python3 -c \"import json; m=json.load(open('outbox/$ID3/manifest.json')); r=m['publication']['results']; assert len(r)==1 and r[0]['state']=='unknown'\" && grep -q 'issue inconnue' learning/CONTENT_LEDGER.md"
tr_ "reprise bloquée tant que l'issue est inconnue" python3 skills/novia-publish/scripts/publish.py "$ID3"
t "après vérification manuelle (--resolve linkedin=published) : pièce publiée sans renvoi" bash -c "python3 skills/novia-publish/scripts/publish.py '$ID3' --resolve linkedin=published >/dev/null && python3 -c \"import json; m=json.load(open('outbox/$ID3/manifest.json')); assert m['status']=='published' and len(m['publication']['results'])==1\""
ID2="$(python3 skills/novia-outbox/scripts/outbox_new.py --format F1 --persona P1 --channel linkedin --title "Test calibration")"
set_caption "outbox/$ID2/manifest.json" "Test. Source : https://example.org"
python3 skills/novia-outbox/scripts/outbox_present.py "$ID2" --stage final --score 90 --test --card-id 1 >/dev/null
tr_ "pièce test de calibration jamais approuvable pour publication" "${APPROVE[@]}" "$ID2" --stage go2 --by 123456789 --text "Go publie" --reply-to 1 --message-id 2 --chat-id -1001234567890
echo "== Contrôles éditoriaux"
t "légende conforme acceptée" python3 skills/novia-editorial/scripts/caption_check.py --channel linkedin --persona P1 --text "Vous achetez à Toulouse ? Selon service-public.fr (2026), le PTZ finance une partie du prix."
tf "promesse de rendement refusée" python3 skills/novia-editorial/scripts/caption_check.py --channel linkedin --persona P2 --text "Rendement garanti de 5 % selon nous."
tf "urgence fabriquée refusée" python3 skills/novia-editorial/scripts/caption_check.py --channel instagram --text "Dernières unités disponibles."
tf "tutoiement refusé" python3 skills/novia-editorial/scripts/caption_check.py --channel facebook --text "Tu veux acheter ? Source : https://x.fr"
echo "== Production"
cat > "outbox/$ID/carousel.json" <<'J'
{"id":"t","persona":"P1","slides":[{"title":"A","body":"a","cover":true},{"title":"B","body":"b"},{"title":"C","body":"c"},{"title":"D","body":"d"},{"title":"E","body":"e","last":true}],"footer":{"source":"s"}}
J
t "carrousel construit (5 slides)" python3 skills/novia-carousel/scripts/carousel_build.py "outbox/$ID/carousel.json"
tf "infographie refusée sans données sourcées" python3 skills/novia-infographie/scripts/infographie_build.py --out "outbox/$ID/i.html"
cat > "outbox/$ID/nl.json" <<'J'
{"subject":"Objet de test raisonnable","persona":"P2","intro":"Bonjour.","sections":[{"title":"T","body":"Corps."}],"footer":{"address":"Adresse","unsubscribe_url":"{{ unsubscribe }}"}}
J
t "newsletter avec mention des risques (P2) et sans %% résiduel" bash -c "python3 skills/novia-newsletter/scripts/newsletter_build.py 'outbox/$ID/nl.json' && grep -q risques 'outbox/$ID/newsletter.html' && ! grep -q '%%' 'outbox/$ID/newsletter.html'"
cat > "outbox/$ID/nl2.json" <<'J'
{"subject":"Objet de test raisonnable","persona":"P1","intro":"Bonjour.","sections":[{"title":"T","body":"Corps."}],"footer":{"address":"Adresse"}}
J
tf "newsletter refusée sans lien de désinscription" python3 skills/novia-newsletter/scripts/newsletter_build.py "outbox/$ID/nl2.json"
t "calendrier lisible" python3 skills/novia-calendrier/scripts/calendrier_next.py --days 60
printf 'date,piece_id,channel,metric,value,source\n2026-09-14,%s,linkedin,impressions,100,test\n' "$ID" > outbox/_metrics/t.csv 2>/dev/null || { mkdir -p outbox/_metrics; printf 'date,piece_id,channel,metric,value,source\n2026-09-14,%s,linkedin,impressions,100,test\n' "$ID" > outbox/_metrics/t.csv; }
t "reporting : ingestion et bilan par (pièce, canal)" bash -c "python3 skills/novia-reporting/scripts/metrics_ingest.py outbox/_metrics/t.csv >/dev/null && python3 skills/novia-reporting/scripts/weekly_digest.py --days 7 | grep -q 'Publications'"
if command -v ffmpeg >/dev/null; then
  ffmpeg -y -loglevel error -f lavfi -i color=c=gray:s=800x600 -frames:v 1 "outbox/$ID/m.png"
  t "déclinaison image (4 formats)" bash -c "bash skills/novia-declinaison/scripts/declinaison.sh 'outbox/$ID/m.png' 'outbox/$ID/d' && [ \$(ls outbox/$ID/d | wc -l) -eq 4 ]"
fi
echo "== Onboarding (états)"
set_onboarding act0_diagnostic
tr_ "passage à complete refusé tant que l'onboarding n'est pas fait" python3 skills/novia-onboarding/scripts/onboarding_state.py --set complete
tf "--check signale les conditions manquantes (code 1)" python3 skills/novia-onboarding/scripts/onboarding_state.py --check
t "avancement séquentiel accepté" python3 skills/novia-onboarding/scripts/onboarding_state.py --set act1_identite_equipe
tr_ "saut d'acte refusé" python3 skills/novia-onboarding/scripts/onboarding_state.py --set act4_calibration
rm -rf "$T"
echo; echo "Résultat : $pass réussis, $fail échoués"
[ "$fail" = 0 ]
