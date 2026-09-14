---
name: novia-onboarding
description: "Onboarding de Novia Com chez IMMO9 en cinq actes : diagnostic (acte 0), identité et équipe (acte 1), voix extraite des publications réelles (acte 2), lignes rouges, personas, formats et charte (acte 3), calibration sur trois pièces test gratuites (acte 4), puis statut complete. Verrou : tant que state/onboarding.json n'est pas complete, aucune production publiable ni publication. Scripts : onboarding_state.py."
metadata: {"openclaw": {"emoji": "🧭", "requires": {"bins": ["python3"]}}}
---

# novia-onboarding — apprendre IMMO9 avant de produire pour IMMO9

## Règles de conduite (tous les actes)
- Un message = une décision. Jamais deux questions dans un message.
- Je propose une hypothèse tirée de ce qui existe (site, comptes, documents), l'équipe corrige. Je ne demande jamais « décrivez votre style ».
- Chaque acte se termine par un fichier de doctrine écrit et une ligne dans `state/onboarding.json`.
- Le verrou est technique : `python3 skills/novia-onboarding/scripts/onboarding_state.py --check` refuse de passer à `complete` si une condition manque. Je n'essaie pas de le contourner.

## Acte 0 · Diagnostic (premier contact, Julien)
1. `bash scripts/doctor.sh` (à la racine du dépôt) : outils, variables, skills prêts, flux RSS joignables. Rendre trois listes : ce qui marche, ce que le studio ajoute, ce qui manque (connecteurs, clés, charte).
2. Lire `TEAM.md`, `state/approvers.json`, `state/channels.json` : signaler les `[À REMPLIR]`.
3. `onboarding_state.py --set act1_identite_equipe`.

## Acte 1 · Identité et équipe (David, Julien)
- Confirmer le nom et le ton de l'agent (`IDENTITY.md`), les personnes et leurs identifiants Telegram (`TEAM.md`, `state/approvers.json`), le canal de travail (`state/channels.json`), les plafonds de coût (`doctrine/STUDIO_CONTRACT.json` → `budget`).
- `onboarding_state.py --set act2_voix`.

## Acte 2 · Voix (équipe communication)
- Lire le corpus réel : site, LinkedIn, Instagram, newsletters passées (URL fournies ou `web_fetch`). Extraire rythme, ouvertures, finitions, lexique signature et banni, registres. Écrire `doctrine/VOICE.md` (remplacer chaque `[À REMPLIR]`) et compléter `knowledge/lexique-banni.json`.
- Proposer trois courts textes « dans la voix » et trois « hors voix » ; l'équipe dit lesquels lui ressemblent ; consigner dans `learning/TASTE.md`.
- `onboarding_state.py --set act3_lignes_personas_charte`.

## Acte 3 · Lignes rouges, personas, formats, charte (David + équipe)
- `doctrine/LINES.md` : sections propres à IMMO9 (une décision par message). `doctrine/PERSONAS.md` : objections et questions réelles des commerciaux. `doctrine/FORMATS.md` : les formats réellement tenus au départ (trois suffisent). `templates/_tokens.json` et `templates/_brand/` : charte. `knowledge/calendrier-marronniers.json` : salons confirmés, livraisons. `knowledge/concurrents.json`. `knowledge/sources-veille.json` : presse locale suivie.
- `onboarding_state.py --set act4_calibration`.

## Acte 4 · Calibration (équipe communication)
- Produire trois pièces test gratuites (un post F1, un carrousel F2, un digest de veille), présentées comme des tests. Corriger selon les retours, consigner dans `TASTE.md`.
- `onboarding_state.py --check` puis `--set complete` quand tout est vert. Activer les crons du palier 1 (`scripts/install-crons.sh --enable-p1`).

## Après
Rappeler à l'équipe les deux mots qui comptent (« Go », « Go publie »), et que le silence est une réponse valide.
