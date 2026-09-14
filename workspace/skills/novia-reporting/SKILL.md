---
name: novia-reporting
description: "Reporting IMMO9 : ingestion des métriques par pièce et par plateforme (exports CSV ou connecteurs analytics) dans learning/METRICS.md (scripts/metrics_ingest.py), rapport hebdomadaire et mensuel (scripts/weekly_digest.py), recommandations d'optimisation, benchmark concurrents et heures de publication. Auto (rapports), Assistant (recommandations)."
metadata: {"openclaw": {"emoji": "📈", "requires": {"bins": ["python3"]}}}
---

# novia-reporting : mesurer honnêtement, conclure lentement

## Sources de métriques
- Exports CSV des plateformes (Meta Business Suite, LinkedIn Pages, YouTube Studio) déposés par l'équipe dans `outbox/_metrics/` : colonnes `date, piece_id, channel, metric, value, source`.
- Connecteurs analytics si configurés (voir `connectors/README.md`) : le script d'ingestion accepte le même format CSV produit par un adaptateur.
- Métriques suivies par format (`doctrine/FORMATS.md`) : reach, impressions, engagement (réactions, commentaires, partages, enregistrements), clics, vues complètes, ouvertures et clics newsletter, réponses reçues.

## Scripts
- `python3 skills/novia-reporting/scripts/metrics_ingest.py outbox/_metrics/<fichier>.csv` : valide, dédoublonne (date, pièce, canal, métrique), ajoute à `learning/METRICS.md` et marque le fichier ingéré.
- `python3 skills/novia-reporting/scripts/weekly_digest.py --days 7` : publications de la période (ledger), métriques disponibles, meilleure et plus faible pièce, ce qui manque (pièces publiées sans métriques). `--days 30` pour le mensuel.

## Rapport hebdomadaire (cron `reporting-hebdo`, lundi)
Cinq lignes dans le groupe : publications de la semaine, meilleure pièce et hypothèse, plus faible et hypothèse, une recommandation, ce qui attend une décision. `NO_REPLY` s'il n'y a eu ni publication ni métrique nouvelle.

## Rapport mensuel (cron `reporting-mensuel`, le 3)
Ajoute : total par canal, comparaison au mois précédent, coût réel du mois (`learning/BUDGET_LEDGER.md`), benchmark concurrents (publications publiques observées dans `learning/VEILLE-HEBDO.md`, jamais publié), recommandations (au plus trois, chacune liée à une observation), heures de publication observées les meilleures (trimestriel, avec le nombre d'observations).

## Règles
- Aucune conclusion sur un format avant six observations ; le rapport dit « pas assez de données » plutôt qu'une tendance.
- Les métriques manquantes sont dites manquantes ; zéro et absent ne sont jamais confondus.
- Les chiffres de concurrents restent internes.
