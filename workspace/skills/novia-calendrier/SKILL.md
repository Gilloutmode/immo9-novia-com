---
name: novia-calendrier
description: "Calendrier éditorial IMMO9 : marronniers immobilier, échéances réglementaires et fiscales, salons par ville, événements internes, lus depuis knowledge/calendrier-marronniers.json (scripts/calendrier_next.py). Nourrit le comité éditorial du lundi, la prévision mensuelle et la préparation des campagnes. Assistant et cron."
metadata: {"openclaw": {"emoji": "📅", "requires": {"bins": ["python3"]}}}
---

# novia-calendrier : savoir ce qui arrive avant que ça arrive

## Usage
```bash
python3 skills/novia-calendrier/scripts/calendrier_next.py --days 30          # les 30 prochains jours
python3 skills/novia-calendrier/scripts/calendrier_next.py --month 2026-11    # un mois donné
python3 skills/novia-calendrier/scripts/calendrier_next.py --days 90 --kind salon --json
```
Chaque ligne : date, nom, type (réglementaire, fiscal, marché, salon, interne), ville, « à confirmer » si la date d'édition n'est pas confirmée, source, et la séquence de contenu suggérée (annonce J-21, pédagogie J-10, rappel J-2, bilan J+7) pour les échéances importantes.

## Comité éditorial du lundi (cron `comite-editorial`)
1. Lire les 30 prochains jours et `learning/THEMES_COVERED.md`.
2. Proposer le plan de la semaine : un carrousel, les posts du jour à venir (thèmes), les contenus à préparer pour les échéances à moins de 21 jours, ce que l'équipe doit fournir (visuels de programmes, dates).
3. Une seule carte, décisions groupées.

## Ajouter un événement
Éditer `knowledge/calendrier-marronniers.json` (l'équipe ou l'agent sur demande) : `name`, `kind`, `city`, `date` (AAAA-MM-JJ) ou `recurrence` (`{"type": "yearly", "month": 10, "day": 15}` ou `{"type": "monthly", "day": 1}`), `confirmed`, `source`, `note`. Les dates de salons restent `confirmed: false` tant que l'équipe n'a pas vérifié l'édition de l'année.
