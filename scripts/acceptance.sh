#!/usr/bin/env bash
# Tests d'acceptation hors ligne de Novia Com (aucun appel réseau, aucune écriture dans le dépôt).
# Copie le workspace dans un dossier temporaire et vérifie : hygiène du dépôt, scripts, verrous d'approbation et de publication.
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; T="$(mktemp -d -t novia-acc.XXXXXX)"; cp -R "$REPO/workspace" "$T/ws"; export NOVIA_WORKSPACE="$T/ws"; cd "$T/ws" || exit 1
cp state/approvers.json.example state/approvers.json; cp state/channels.json.example state/channels.json
pass=0; fail=0
t() { local name="$1"; shift; if "$@" >/dev/null 2>&1; then printf '✓ %s\n' "$name"; pass=$((pass+1)); else printf '✗ %s\n' "$name"; fail=$((fail+1)); fi; }
tn() { local name="$1"; shift; if "$@" >/dev/null 2>&1; then printf '✗ %s (aurait dû refuser)\n' "$name"; fail=$((fail+1)); else printf '✓ %s\n' "$name"; pass=$((pass+1)); fi; }
echo "== Hygiène du dépôt"
t "aucun chemin personnel (/Users/ ou /home/) dans le dépôt" bash -c "! grep -rIl -E '/Users/[a-z]+/|/home/[a-z]+/' '$REPO' --exclude-dir=.git --exclude-dir=node_modules"
t "aucun secret apparent (clés API, jetons, clés privées)" bash -c "! grep -rIE 'sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY|[0-9]{9,10}:AA[A-Za-z0-9_-]{30,}' '$REPO' --exclude-dir=.git"
t "aucun tiret long dans les fichiers du dépôt" bash -c "! grep -rIl -- '—' '$REPO' --exclude-dir=.git --exclude-dir=node_modules"
t "JSON valides" bash -c "for f in \$(find '$REPO/workspace' '$REPO/crons' -name '*.json' -o -name '*.example' | grep -v node_modules); do python3 -c \"import json,sys;json.load(open(sys.argv[1]))\" \"\$f\" || exit 1; done"
t "scripts Python compilent" bash -c "python3 -m py_compile \$(find '$REPO/workspace/skills' -name '*.py')"
t "scripts shell valides" bash -c "for f in \$(find '$REPO' -name '*.sh' -not -path '*/node_modules/*'); do bash -n \"\$f\" || exit 1; done"
t "chaque SKILL.md a name et description" bash -c "for f in '$REPO'/workspace/skills/*/SKILL.md '$REPO'/skills-shared/*/SKILL.md; do grep -q '^name:' \"\$f\" && grep -q '^description:' \"\$f\" || exit 1; done"
echo "== Cycle d'une pièce"
ID="$(python3 skills/novia-outbox/scripts/outbox_new.py --format F1 --persona P1 --channel linkedin --title "Test" --source https://example.org)"
t "création de pièce" test -f "outbox/$ID/manifest.json"
tn "publication refusée sans approbation" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run
t "présentation" python3 skills/novia-outbox/scripts/outbox_present.py "$ID" --stage final --score 90
tn "Go publie refusé : personne non autorisée" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 999 --text "Go publie"
tn "Go publie refusé : pouce" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "👍"
tn "Go publie refusé : ok seul" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "ok"
tn "Go publie refusé : négation" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "non, pas go publie"
t "Go publie accepté (personne autorisée, réponse claire)" python3 skills/novia-outbox/scripts/outbox_approve.py "$ID" --stage go2 --by 123456789 --text "Go publie"
python3 - "outbox/$ID/manifest.json" <<'PY'
import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["captions"]["linkedin"]="Test. Source : https://example.org"; json.dump(m,open(p,"w"))
PY
t "publication simulée après Go publie" python3 skills/novia-publish/scripts/publish.py "$ID" --dry-run
tn "publication réelle refusée sans connecteur configuré (clé absente)" env -u UPLOAD_POST_API_KEY python3 skills/novia-publish/scripts/publish.py "$ID"
echo "== Contrôles éditoriaux"
t "légende conforme acceptée" python3 skills/novia-editorial/scripts/caption_check.py --channel linkedin --persona P1 --text "Vous achetez à Toulouse ? Selon service-public.fr (2026), le PTZ finance une partie du prix."
tn "légende avec promesse de rendement refusée" python3 skills/novia-editorial/scripts/caption_check.py --channel linkedin --persona P2 --text "Rendement garanti de 5 % selon nous."
tn "légende avec urgence fabriquée refusée" python3 skills/novia-editorial/scripts/caption_check.py --channel instagram --text "Dernières unités disponibles."
tn "légende tutoyant refusée" python3 skills/novia-editorial/scripts/caption_check.py --channel facebook --text "Tu veux acheter ? Source : https://x.fr"
echo "== Production"
cat > "outbox/$ID/carousel.json" <<'J'
{"id":"t","persona":"P1","slides":[{"title":"A","body":"a","cover":true},{"title":"B","body":"b"},{"title":"C","body":"c"},{"title":"D","body":"d"},{"title":"E","body":"e","last":true}],"footer":{"source":"s"}}
J
t "carrousel construit (5 slides)" python3 skills/novia-carousel/scripts/carousel_build.py "outbox/$ID/carousel.json"
tn "infographie refusée sans données sourcées" python3 skills/novia-infographie/scripts/infographie_build.py --out "outbox/$ID/i.html"
cat > "outbox/$ID/nl.json" <<'J'
{"subject":"Objet de test raisonnable","persona":"P2","intro":"Bonjour.","sections":[{"title":"T","body":"Corps."}],"footer":{"address":"Adresse","unsubscribe_url":"{{ unsubscribe }}"}}
J
t "newsletter construite avec mention des risques (P2)" bash -c "python3 skills/novia-newsletter/scripts/newsletter_build.py 'outbox/$ID/nl.json' && grep -q risques 'outbox/$ID/newsletter.html'"
cat > "outbox/$ID/nl2.json" <<'J'
{"subject":"Objet de test raisonnable","persona":"P1","intro":"Bonjour.","sections":[{"title":"T","body":"Corps."}],"footer":{"address":"Adresse"}}
J
tn "newsletter refusée sans lien de désinscription" python3 skills/novia-newsletter/scripts/newsletter_build.py "outbox/$ID/nl2.json"
t "calendrier lisible" python3 skills/novia-calendrier/scripts/calendrier_next.py --days 60
if command -v ffmpeg >/dev/null; then
  ffmpeg -y -loglevel error -f lavfi -i color=c=gray:s=800x600 -frames:v 1 "outbox/$ID/m.png"
  t "déclinaison image (4 formats)" bash -c "bash skills/novia-declinaison/scripts/declinaison.sh 'outbox/$ID/m.png' 'outbox/$ID/d' && [ \$(ls outbox/$ID/d | wc -l) -eq 4 ]"
fi
echo "== Verrou d'onboarding"
tn "passage à complete refusé tant que l'onboarding n'est pas fait" python3 skills/novia-onboarding/scripts/onboarding_state.py --set complete
t "avancement séquentiel accepté" python3 skills/novia-onboarding/scripts/onboarding_state.py --set act1_identite_equipe
tn "saut d'acte refusé" python3 skills/novia-onboarding/scripts/onboarding_state.py --set act4_calibration
rm -rf "$T"
echo; echo "Résultat : $pass réussis, $fail échoués"
[ "$fail" = 0 ]
