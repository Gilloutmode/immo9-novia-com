# Matrice des 32 fonctionnalités demandées (mail IMMO9 du 22 mai 2026)

Chaque ligne reprend une exigence du mail, dans l'ordre et sans regroupement (8 création visuelle, 3 audio, 7 éditorial, 9 veille, 4 performance, 1 partenariats). Identifiants R01 à R32.

Statuts : **Livré** (fonctionne dès le palier 1), **Livré · connecteur** (le skill est prêt, il attend un branchement côté IMMO9), **Palier 2** (livré, activé après l'onboarding ou une dépendance), **Palier 3** (feuille de route). Régimes : Auto, Semi-auto, Assistant, tels que demandés.

## Création visuelle
| Id · Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| R01 Bannières publicitaires (charte graphique) | Semi-auto, à la demande | Palier 2 | gabarit HTML aux tokens de charte + rendu headless ; besoin des tokens et logos (acte 3) |
| R02 Templates et gabarits de posts | Assistant, mensuel | Livré | `templates/` (carrousel, infographie, newsletter, miniatures), refresh proposé au comité éditorial |
| R03 Infographies taux de crédit et prix du neuf | Auto, mensuel | Palier 2 | `novia-infographie` + cron `infographie-mensuelle` ; refuse tout chiffre sans source et date |
| R04 Vidéos ex nihilo (infographies, cartes) | Semi-auto, à la demande | Palier 2 | `novia-video` avec HyperFrames (skill public) ; voix et musique documentées |
| R05 Montage rushes interviews + cut dynamique | Semi-auto, à la demande | Palier 2 | `novia-video` avec `supermonteur` (livré dans skills-shared) et ffmpeg |
| R06 Déclinaison multi-format (9:16, 1:1, 16:9, 1.91:1) | Auto, à la demande | Livré | `novia-declinaison` (ffmpeg, recadrage ou fond flouté), testé |
| R07 Carrousels LinkedIn et Instagram pédagogiques | Semi-auto, hebdomadaire | Livré | `novia-carousel` : JSON → HTML → PNG et PDF ; comité éditorial du lundi |
| R08 Miniatures YouTube A/B testables | Semi-auto, à chaque upload | Palier 2 | deux gabarits `templates/miniature/`, rendu 1280×720, test dans YouTube Studio |

## Audio et podcast
| Id · Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| R09 Production de podcasts (script, voix off, montage) | Semi-auto, bimensuel | Palier 2 | `novia-podcast` + cron `podcast-prep` ; voix humaine recommandée, synthèse si la doctrine l'autorise |
| R10 Audiograms pour réseaux sociaux | Auto, à chaque épisode | Livré | `audiogram.sh` (ffmpeg, forme d'onde, 1:1 et 9:16), testé |
| R11 Transcription et show notes | Auto, à chaque épisode | Livré · connecteur | outil audio d'OpenClaw ou service de transcription configuré ; procédure dans `novia-podcast` |

## Création éditoriale
| Id · Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| R12 Posts réseaux sociaux | Semi-auto, quotidien | Livré | `novia-editorial` + cron `proposition-du-jour` (au plus deux cartes par jour, contrôle machine, score ≥ 85) |
| R13 Newsletters segmentées (4 personas) | Semi-auto, bimensuel à mensuel | Palier 2 | `novia-newsletter` (HTML email-safe, désinscription obligatoire) + adaptateur Brevo |
| R14 Transformation contenus longs → courts | Auto, à la demande | Livré | `novia-editorial` section « long vers court » |
| R15 Préparation de campagnes thématiques | Assistant, trimestriel | Livré | document de campagne (`novia-editorial`) appuyé sur `novia-calendrier` |
| R16 Calendrier éditorial (marronniers, salons, échéances) | Assistant, mensuel | Livré | `novia-calendrier` + `knowledge/calendrier-marronniers.json` + crons `comite-editorial`, `calendrier-preview` |
| R17 Adaptation par persona | Auto, à la demande | Livré | `novia-editorial` section « adaptation » (faits et sources inchangés, risques pour P2) |
| R18 Hooks et accroches en variantes A/B | Auto, à la demande | Livré | `novia-editorial` section « variantes », angles nommés |

## Veille et analyse
| Id · Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| R19 Veille réseaux sociaux immo | Auto, quotidien | Livré · connecteur | digest du matin ; le pouls social complet demande `last30days` (skill public, clés) |
| R20 Analyse concurrentielle (sujets qui buzzent) | Auto (rapport), hebdomadaire | Livré | cron `veille-hebdo` sur `knowledge/concurrents.json` (pages publiques) |
| R21 Repérage questions Reddit + brouillons de réponses | Semi-auto, quotidien | Livré · connecteur | `reddit_scan.py` (OAuth application « script », usage léger) + brouillons `novia-editorial` |
| R22 Repérage questions Quora et forums | Semi-auto, hebdomadaire | Palier 3 | pas d'API Quora ; lecture par `web_fetch` ou `browser` sur des pages précises, à cadrer |
| R23 Veille des manques Wikipédia | Auto (rapport), mensuel | Palier 2 | procédure dans `novia-veille` (lecture, rapport, aucune modification) |
| R24 Veille réglementaire et fiscale (PTZ, DPE…) | Auto, quotidien | Livré | flux BOFiP et FPI vérifiés, pages ANIL, service-public, Légifrance, ministère ; confirmation « officiel » avant contenu |
| R25 Veille presse et influenceurs (mentions marque, concurrents) | Auto, quotidien | Livré · connecteur | presse nationale et locale (flux vérifiés) ; mentions de marque via alertes Google en RSS (gratuit) |
| R26 Détection de tendances (hashtags, formats, sujets) | Auto (rapport), hebdomadaire | Livré | cron `veille-hebdo`, section tendances (observations de la semaine) |
| R27 Google Trends + People Also Ask | Auto, hebdomadaire | Palier 3 | pas d'API Google Trends ouverte en 2026 ; via fournisseur (DataForSEO ou SerpApi) à budgéter |

## Performance et pilotage
| Id · Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| R28 Reporting de performance par plateforme | Auto, hebdo + mensuel | Livré · connecteur | `novia-reporting` sur exports CSV (Meta, LinkedIn, YouTube) ; API analytics au palier 3 |
| R29 Recommandations d'optimisation | Assistant, mensuel | Livré | rapport mensuel : au plus trois recommandations liées à une observation, six observations minimum |
| R30 Benchmark vs concurrents (part de voix, audience) | Auto, mensuel | Palier 3 | part de voix = outil de social listening payant ; en attendant, observation qualitative du rapport hebdo |
| R31 Heures de publication optimales | Auto, trimestriel | Palier 2 | nécessite l'heure de publication dans le ledger et six observations par créneau ; calcul ajouté au rapport mensuel quand ces données existent |

## Relation et partenariats
| Id · Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| R32 Identification d'influenceurs et partenaires immo | Assistant, mensuel | Livré | recherche à la demande (web_search, `last30days` si installé), fiche par candidat, aucun contact sans « Go publie » |

## Décompte
Livré : 19 · Livré avec connecteur : 6 · Palier 2 : 10 · Palier 3 : 4 (R21 Quora, R27 Google Trends et People Also Ask, R30 benchmark part de voix, et les connecteurs analytics par API). Total : 32 lignes, une par exigence du mail. « Livré » = script ou procédure testés dans ce dépôt ; « Livré · connecteur » = prêt, attend un branchement côté IMMO9 ; « Palier 2 » = livré, activé après onboarding ou dépendance ; « Palier 3 » = feuille de route.
