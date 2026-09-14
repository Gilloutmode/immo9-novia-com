---
name: novia-infographie
description: "Infographie mensuelle IMMO9 taux de crédit et prix du neuf par ville (1080×1350 ou 1080×1080), construite depuis knowledge/donnees-marche.json avec source et date sur chaque chiffre (scripts/infographie_build.py), rendue avec render_html.sh de novia-carousel. Auto en brouillon (cron infographie-mensuelle), publication après Go."
metadata: {"openclaw": {"emoji": "📊", "requires": {"bins": ["python3"]}}}
---

# novia-infographie : le repère chiffré du mois, sourcé sur l'image

## Procédure (cron `infographie-mensuelle`, le 2 du mois, ou à la demande)
1. Mettre à jour `knowledge/donnees-marche.json` : taux moyens (Observatoire Crédit Logement / CSA, Banque de France), prix du neuf par ville (sources professionnelles ou notariales), chaque valeur avec `source` (nom + URL) et `date`. Un chiffre sans source reste vide et n'est pas rendu.
2. `python3 skills/novia-infographie/scripts/infographie_build.py --out outbox/<id>/infographie.html [--square]` : refuse de construire si une valeur renseignée n'a pas de source ou de date.
3. `bash skills/novia-carousel/scripts/render_html.sh outbox/<id>/infographie.html 1080 1350` (ou 1080 1080 avec `--square`).
4. Contrôle visuel (`rules/production-visuelle.md`), légende avec `novia-editorial` (persona P2 par défaut, donc mention des risques), présentation en carte, « Go publie ».

## Règles
- Toujours indiquer la période (mois) et la date de relevé sur l'image.
- Ne jamais extrapoler une tendance sans la source qui la décrit.
- Comparaison mois précédent seulement si les deux relevés viennent de la même source.
