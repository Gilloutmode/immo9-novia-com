---
name: novia-newsletter
description: "Newsletters segmentées IMMO9 par persona (primo-accédants, investisseurs, promoteurs, partenaires) : brouillon bimensuel à mensuel, HTML email-safe 640 px à partir d'un JSON (scripts/newsletter_build.py), version texte, contrôle conformité et désinscription, envoi via l'adaptateur brevo de novia-publish après « Go publie »."
metadata: {"openclaw": {"emoji": "📬", "requires": {"bins": ["python3"]}}}
---

# novia-newsletter : une idée principale, une persona, un rendu propre dans Gmail et Outlook

## Procédure (cron `newsletter-brouillon` le 1er et le 15, ou à la demande)
1. Choisir la persona du numéro (rotation P1, P2, P3, P4 selon `learning/CONTENT_LEDGER.md`) et l'idée principale ancrée (veille du mois, échéance, programme).
2. Écrire `outbox/<id>/newsletter.json` : `subject` (35 à 50 caractères, bénéfice concret), `preheader`, `persona`, `intro` (3 phrases), `sections` (2 à 4 : `title`, `body`, `link`, `link_label`), `signature` (prénom et rôle réels), `footer` (adresse postale, `unsubscribe_url` = balise de l'outil d'emailing, par exemple `{{ unsubscribe }}` pour Brevo).
3. `python3 skills/novia-newsletter/scripts/newsletter_build.py outbox/<id>/newsletter.json` → `newsletter.html` (tables, CSS inline, 640 px, tokens de charte) et `newsletter.txt`. Le script refuse : sujet trop long, absence de lien de désinscription, absence d'adresse, persona P2 sans mention des risques.
4. Contrôle : `caption_check.py --channel newsletter --persona <P>` sur le texte ; aperçu (rendu du HTML par le navigateur headless ou envoi test depuis Brevo).
5. Présentation en carte (objet, pré-en-tête, aperçu en pièce jointe), « Go publie », puis `publish.py <id> --channel newsletter` (adaptateur `brevo`, en brouillon Brevo par défaut).

## Règles
- Destinataires : listes consenties de l'outil d'emailing, jamais un fichier de contacts fourni par un commercial.
- Une newsletter P2 porte la mention des risques et n'inclut aucune simulation individualisée.
- Pas d'images lourdes : une image d'en-tête au maximum, texte alternatif présent.
- Objet sans majuscules criées, sans « urgent », sans émoji.
