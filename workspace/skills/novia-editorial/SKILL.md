---
name: novia-editorial
description: "Rédaction éditoriale IMMO9 : posts réseaux sociaux quotidiens (semi-auto), adaptation d'un texte validé par persona (auto), variantes d'accroches pour test A/B (auto), transformation d'un contenu long en formats courts (auto), préparation de campagnes thématiques et brouillons de réponses forums (assistant). Contrôle machine des légendes par plateforme (limites, mots bannis, conformité) avec scripts/caption_check.py."
metadata: {"openclaw": {"emoji": "✍️", "requires": {"bins": ["python3"]}}}
---

# novia-editorial : écrire dans la voix d'IMMO9, pour une personne précise

## Avant d'écrire (obligatoire)
1. `doctrine/LINES.md` puis `rules/conformite-immobilier.md` : ce qui bloque.
2. `doctrine/VOICE.md` et `doctrine/PERSONAS.md` : la voix, la persona visée, ses questions réelles.
3. `learning/THEMES_COVERED.md` : pas de doublon à moins de 60 jours sans angle neuf.
4. `doctrine/CAPTIONS_MATRIX.md` : le canal primaire et ses limites.
5. La promesse de la pièce (`doctrine/NARRATIVE_QUALITY.md` §1) remplie dans le manifest (`novia-outbox`).

## Post réseaux sociaux (F1, semi-auto, quotidien via le cron `proposition-du-jour`)
1. Ancrage : un item de la veille du jour, une question client relayée, une échéance du calendrier ou un programme. Sans ancrage, pas de proposition.
2. Structure LinkedIn : ouverture autonome (situation du lecteur ou fait daté), 3 à 5 courts paragraphes, une source citée, une fin qui donne un repère ou pose une question sincère. 120 à 220 mots. Vouvoiement.
3. Légende Instagram et Facebook seulement si ces canaux sont destinés à publier cette pièce (transformation selon la matrice, pas de copier-coller).
4. Visuel : gabarit `templates/` ou visuel fourni par l'équipe (voir `rules/production-visuelle.md`).
5. Contrôle : `python3 skills/novia-editorial/scripts/caption_check.py --channel linkedin --persona P1 --file outbox/<id>/linkedin.txt`. Un `FAIL` bloque la présentation.
6. Scorecard `NARRATIVE_QUALITY.md` ≥ 85, puis `outbox_present.py <id> --stage final --score <n>` et la carte dans le groupe.

## Adaptation par persona (auto, après validation d'un texte)
Reprendre le texte validé, changer la situation d'ouverture, le vocabulaire (`PERSONAS.md` : mots à utiliser et à éviter), l'exemple et la fin. Ne pas changer les faits ni les sources. Livrer dans `outbox/<id>/adaptations/<persona>.txt` et signaler dans le groupe en une ligne. Un contenu adapté pour P2 porte la mention des risques.

## Variantes d'accroches (auto)
Trois à cinq premières lignes différentes pour un même texte, chacune avec son angle nommé : situation, fait daté, question, contradiction, chiffre. Jamais de question rhétorique creuse ni d'urgence. Livrer dans `outbox/<id>/hooks.txt` ; l'équipe choisit ou teste.

## Long vers court (auto)
À partir d'un article, d'une transcription ou d'une newsletter validée : extraire 3 à 6 idées autonomes, chacune devient un post court ou une slide de carrousel. Conserver les sources. Livrer dans `outbox/<id>/short/`.

## Campagnes thématiques et calendrier (assistant, sur demande)
Un document `outbox/<id>/campagne.md` : objectif, persona, message central, séquence (annonce, pédagogie, rappel, bilan), formats par étape, sources, ce que l'équipe doit fournir. Le calendrier s'appuie sur `novia-calendrier`.

## Réponses Reddit, Quora, forums (semi-auto)
Le cron `veille-matin` remonte les questions ; pour chacune, un brouillon de réponse utile, sourcé, sans promotion, signé « IMMO9 » seulement si l'équipe le souhaite. Livré dans le digest ; une personne publie ou donne « Go publie » si un connecteur existe.

## Le contrôle machine (`scripts/caption_check.py`)
Vérifie : longueur par canal, nombre de hashtags, mots bannis (`knowledge/lexique-banni.json`), promesses de rendement et urgence fabriquée, tutoiement dans un texte public, mention des risques pour P2, tirets longs, formules IA, présence d'une source (URL ou « selon ») quand le texte contient un chiffre. Sortie : `OK` ou `FAIL` avec la liste des motifs ; code de retour 1 en cas d'échec.
