# Feuille de route

## Palier 1 · installé et fonctionnel dès l'onboarding
Veille quotidienne et hebdomadaire, proposition de posts, carrousel hebdomadaire, déclinaisons, calendrier éditorial, boîte de sortie avec approbations, publication sous « Go publie » (dès qu'un connecteur est branché), reporting sur exports, boucle d'apprentissage, santé.

## Palier 2 · livré, activé quand la dépendance est là
- Infographie mensuelle (données sourcées du mois).
- Newsletters (compte Brevo, listes par persona).
- Podcast et audiograms (enregistrement ou voix autorisée ; hébergeur).
- Vidéo courte, montage d'interviews, miniatures (HyperFrames et supermonteur installés, chromium ou browser).
- Rapport mensuel, manques Wikipédia, bannières.
Activation : les crons du palier 2 sont déclarés désactivés ; `openclaw cron enable <id>` (identifiants dans `openclaw cron list`) quand la dépendance est branchée.

## Palier 3 · à décider avec IMMO9
- Connecteurs analytics par API (Meta Insights, LinkedIn, YouTube Analytics) : plus de fraîcheur, mais revues d'applications et jetons à gérer.
- Tendances de recherche : Google Trends n'a pas d'API ouverte en 2026 ; fournisseurs DataForSEO (SERP et « People Also Ask ») ou SerpApi, à budgéter.
- Part de voix concurrentielle : outil de social listening (Brand24, Mention) ou observation manuelle structurée.
- Quora et forums : lecture par navigateur sur des pages ciblées.
- Recherche multi-moteurs approfondie (`deep-search`) : très efficace pour les dossiers de fond, demande une dizaine de clés payantes.
- Nœud de rendu : si les rendus vidéo pèsent sur le serveur, déporter le rendu sur une machine dédiée connectée au gateway (`openclaw connect`).
- Mémoire externe partagée (memory-rag ou GBrain) : voir `docs/MEMOIRE.md`.
- **Publication isolée de l'agent (priorité du palier 2)**. Aujourd'hui, les verrous d'approbation et de publication sont des scripts que l'agent exécute lui-même : ils empêchent l'erreur et la validation par une personne non autorisée, ils n'empêchent pas un agent qui voudrait les contourner (il a l'exécution de commandes et l'écriture du workspace). L'étape suivante sépare la publication de l'agent : un service « publisher » sous un autre utilisateur système, seul détenteur des jetons de publication, qui lit les manifests en `approved`, re-vérifie l'approbation contre l'enregistrement du message Telegram côté gateway (auteur, texte, date), et publie. L'agent perd alors les variables des connecteurs (`skills.entries.novia-publish.env` retiré) et ne peut plus que demander. Même logique pour les dépenses : un hook de politique d'outils (plugin OpenClaw) qui refuse tout appel payant sans devis enregistré.

## Rythme de livraison
Une version par semaine via `scripts/update.sh`, avec `CHANGELOG.md`. Chaque version passe `scripts/acceptance.sh` et une relecture à froid par un second modèle avant d'être poussée.
