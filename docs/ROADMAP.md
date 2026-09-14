# Feuille de route

## Palier 1 · installé et fonctionnel dès l'onboarding
Veille quotidienne et hebdomadaire, proposition de posts, carrousel hebdomadaire, déclinaisons, calendrier éditorial, boîte de sortie avec approbations, publication sous « Go publie » (dès qu'un connecteur est branché), reporting sur exports, boucle d'apprentissage, santé.

## Palier 2 · livré, activé quand la dépendance est là
- Infographie mensuelle (données sourcées du mois).
- Newsletters (compte Brevo, listes par persona).
- Podcast et audiograms (enregistrement ou voix autorisée ; hébergeur).
- Vidéo courte, montage d'interviews, miniatures (HyperFrames et supermonteur installés, chromium ou browser).
- Rapport mensuel, manques Wikipédia, bannières.
Activation : `bash crons/install-crons.sh` (les crons du palier 2 sont déclarés désactivés ; `openclaw cron edit <id>` ou re-déclaration pour les activer).

## Palier 3 · à décider avec IMMO9
- Connecteurs analytics par API (Meta Insights, LinkedIn, YouTube Analytics) : plus de fraîcheur, mais revues d'applications et jetons à gérer.
- Tendances de recherche : Google Trends n'a pas d'API ouverte en 2026 ; fournisseurs DataForSEO (SERP et « People Also Ask ») ou SerpApi, à budgéter.
- Part de voix concurrentielle : outil de social listening (Brand24, Mention) ou observation manuelle structurée.
- Quora et forums : lecture par navigateur sur des pages ciblées.
- Recherche multi-moteurs approfondie (`deep-search`) : très efficace pour les dossiers de fond, demande une dizaine de clés payantes.
- Nœud de rendu : si les rendus vidéo pèsent sur le serveur, déporter le rendu sur une machine dédiée connectée au gateway (`openclaw connect`).
- Mémoire externe partagée (memory-rag ou GBrain) : voir `docs/MEMOIRE.md`.
- Budget guard en plugin OpenClaw (hook de politique d'outils) : aujourd'hui le plafond est porté par le contrat et les scripts ; un hook rendrait toute dépense impossible sans devis enregistré.

## Rythme de livraison
Une version par semaine via `scripts/update.sh`, avec `CHANGELOG.md`. Chaque version passe `scripts/acceptance.sh` et une relecture à froid par un second modèle avant d'être poussée.
