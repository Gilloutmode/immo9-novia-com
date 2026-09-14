# Matrice des 39 fonctionnalités demandées (mail IMMO9 du 22 mai 2026)

Statuts : **Livré** (fonctionne dès le palier 1), **Livré · connecteur** (le skill est prêt, il attend un branchement côté IMMO9), **Palier 2** (livré, activé après l'onboarding ou une dépendance), **Palier 3** (feuille de route). Régimes : Auto, Semi-auto, Assistant, tels que demandés.

## Création visuelle
| Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| Bannières publicitaires (charte graphique) | Semi-auto, à la demande | Palier 2 | gabarit HTML aux tokens de charte + rendu headless ; besoin des tokens et logos (acte 3) |
| Templates et gabarits de posts | Assistant, mensuel | Livré | `templates/` (carrousel, infographie, newsletter, miniatures), refresh proposé au comité éditorial |
| Infographies taux de crédit et prix du neuf | Auto, mensuel | Palier 2 | `novia-infographie` + cron `infographie-mensuelle` ; refuse tout chiffre sans source et date |
| Vidéos ex nihilo (infographies, cartes) | Semi-auto, à la demande | Palier 2 | `novia-video` avec HyperFrames (skill public) ; voix et musique documentées |
| Montage rushes interviews + cut dynamique | Semi-auto, à la demande | Palier 2 | `novia-video` avec `supermonteur` (livré dans skills-shared) et ffmpeg |
| Déclinaison multi-format (9:16, 1:1, 16:9, 1.91:1) | Auto, à la demande | Livré | `novia-declinaison` (ffmpeg, recadrage ou fond flouté), testé |
| Carrousels LinkedIn et Instagram pédagogiques | Semi-auto, hebdomadaire | Livré | `novia-carousel` : JSON → HTML → PNG et PDF ; comité éditorial du lundi |
| Miniatures YouTube A/B testables | Semi-auto, à chaque upload | Palier 2 | deux gabarits `templates/miniature/`, rendu 1280×720, test dans YouTube Studio |

## Audio et podcast
| Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| Production de podcasts (script, voix off, montage) | Semi-auto, bimensuel | Palier 2 | `novia-podcast` + cron `podcast-prep` ; voix humaine recommandée, synthèse si la doctrine l'autorise |
| Audiograms pour réseaux sociaux | Auto, à chaque épisode | Livré | `audiogram.sh` (ffmpeg, forme d'onde, 1:1 et 9:16), testé |
| Transcription et show notes | Auto, à chaque épisode | Livré · connecteur | outil audio d'OpenClaw ou service de transcription configuré ; procédure dans `novia-podcast` |

## Création éditoriale
| Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| Posts réseaux sociaux | Semi-auto, quotidien | Livré | `novia-editorial` + cron `proposition-du-jour` (au plus deux cartes par jour, contrôle machine, score ≥ 85) |
| Newsletters segmentées (4 personas) | Semi-auto, bimensuel à mensuel | Palier 2 | `novia-newsletter` (HTML email-safe, désinscription obligatoire) + adaptateur Brevo |
| Transformation contenus longs → courts | Auto, à la demande | Livré | `novia-editorial` section « long vers court » |
| Préparation de campagnes thématiques | Assistant, trimestriel | Livré | document de campagne (`novia-editorial`) appuyé sur `novia-calendrier` |
| Calendrier éditorial (marronniers, salons, échéances) | Assistant, mensuel | Livré | `novia-calendrier` + `knowledge/calendrier-marronniers.json` + crons `comite-editorial`, `calendrier-preview` |
| Adaptation par persona | Auto, à la demande | Livré | `novia-editorial` section « adaptation » (faits et sources inchangés, risques pour P2) |
| Hooks et accroches en variantes A/B | Auto, à la demande | Livré | `novia-editorial` section « variantes », angles nommés |

## Veille et analyse
| Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| Veille réseaux sociaux immo | Auto, quotidien | Livré · connecteur | digest du matin ; le pouls social complet demande `last30days` (skill public, clés) |
| Analyse concurrentielle (sujets qui buzzent) | Auto (rapport), hebdomadaire | Livré | cron `veille-hebdo` sur `knowledge/concurrents.json` (pages publiques) |
| Repérage questions Reddit + brouillons de réponses | Semi-auto, quotidien | Livré · connecteur | `reddit_scan.py` (OAuth application « script », usage léger) + brouillons `novia-editorial` |
| Repérage questions Quora et forums | Semi-auto, hebdomadaire | Palier 3 | pas d'API Quora ; lecture par `web_fetch` ou `browser` sur des pages précises, à cadrer |
| Veille des manques Wikipédia | Auto (rapport), mensuel | Palier 2 | procédure dans `novia-veille` (lecture, rapport, aucune modification) |
| Veille réglementaire et fiscale (PTZ, DPE…) | Auto, quotidien | Livré | flux BOFiP et FPI vérifiés, pages ANIL, service-public, Légifrance, ministère ; confirmation « officiel » avant contenu |
| Veille presse et influenceurs (mentions marque, concurrents) | Auto, quotidien | Livré · connecteur | presse nationale et locale (flux vérifiés) ; mentions de marque via alertes Google en RSS (gratuit) |
| Détection de tendances (hashtags, formats, sujets) | Auto (rapport), hebdomadaire | Livré | cron `veille-hebdo`, section tendances (observations de la semaine) |
| Google Trends + People Also Ask | Auto, hebdomadaire | Palier 3 | pas d'API Google Trends ouverte en 2026 ; via fournisseur (DataForSEO ou SerpApi) à budgéter |

## Performance et pilotage
| Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| Reporting de performance par plateforme | Auto, hebdo + mensuel | Livré · connecteur | `novia-reporting` sur exports CSV (Meta, LinkedIn, YouTube) ; API analytics au palier 3 |
| Recommandations d'optimisation | Assistant, mensuel | Livré | rapport mensuel : au plus trois recommandations liées à une observation, six observations minimum |
| Benchmark vs concurrents (part de voix, audience) | Auto, mensuel | Palier 3 | part de voix = outil de social listening payant ; en attendant, observation qualitative du rapport hebdo |
| Heures de publication optimales | Auto, trimestriel | Livré | calcul dans le rapport mensuel dès que six observations par créneau existent |

## Relation et partenariats
| Fonctionnalité | Régime demandé | Statut | Comment |
|---|---|---|---|
| Identification d'influenceurs et partenaires immo | Assistant, mensuel | Livré | recherche à la demande (web_search, `last30days` si installé), fiche par candidat, aucun contact sans « Go publie » |

## Décompte
Livré : 20 · Livré avec connecteur : 6 · Palier 2 : 9 · Palier 3 : 4. Total : 39.
