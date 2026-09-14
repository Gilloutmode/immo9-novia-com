# Novia Com · agent OpenClaw de communication pour IMMO9

Novia Com est un agent OpenClaw dédié au pôle communication d'IMMO9 (promoteur et distributeur de logements neufs à Toulouse, Bordeaux, Montpellier, Nantes et Rennes). Il fait la veille du marché du neuf chaque matin, propose et produit des contenus dans la voix d'IMMO9 pour quatre audiences, décline chaque pièce dans les formats des plateformes, mesure ce qui a été publié, et **ne publie jamais sans un « Go publie » d'une personne autorisée**.

Ce dépôt contient tout ce qu'il faut pour l'installer sur un serveur OpenClaw existant (2026.9.1 ou plus récent), le brancher aux comptes d'IMMO9 et le faire évoluer chaque semaine par un simple `git pull`.

## Ce que contient le dépôt
```
workspace/            le workspace de l'agent (ce qu'OpenClaw charge à chaque session)
  AGENTS.md           charte opérationnelle : régimes d'autonomie, cycle d'une pièce, règles dures, crons, mémoire
  SOUL.md · IDENTITY.md · TEAM.md · HEARTBEAT.md · BOOT.md
  rules/              procédures détaillées (autonomie, validation, conformité immobilier, veille, visuel, coûts, crons…)
  doctrine/           voix, lignes rouges, personas, formats, légendes par plateforme, charte, qualité, contrat machine
  knowledge/          glossaire neuf et VEFA, dispositifs 2026 avec niveaux de confiance, sources de veille vérifiées, calendrier, villes
  skills/             13 skills novia-* avec leurs scripts (Python 3.8+ et bash, sans dépendance externe)
  templates/          gabarits HTML (carrousel, infographie, newsletter, miniatures) pilotés par les tokens de charte
  state/ · learning/ · outbox/ · memory/   état, apprentissage, pièces produites, journal (propres à chaque installation)
skills-shared/        6 skills réutilisables installés pour tous les agents, et la liste des skills à prendre à leur source publique
config/               fragment de configuration OpenClaw (sans secret) et exemple de variables d'environnement
crons/                12 tâches planifiées déclarées de façon idempotente (7 au palier 1, 5 au palier 2)
scripts/              install.sh · doctor.sh · acceptance.sh · update.sh
connectors/           ce que Julien branche : Telegram, publication (upload-post ou APIs natives), newsletter, analytics, veille
docs/                 installation pas à pas, architecture, matrice des 32 fonctionnalités, feuille de route, sécurité, mémoire, état de l'art, limites, prompt Claude Code
```

## Installation en six étapes (détail : `docs/INSTALLATION.md`)
1. Sur le serveur OpenClaw : `git clone <ce dépôt> && cd immo9-novia-com && bash scripts/doctor.sh`
2. Créer le bot Telegram « Novia Com » (@BotFather), le groupe de travail, relever les identifiants des personnes autorisées ; remplir `workspace/state/approvers.json` et `workspace/state/channels.json` (des exemples sont fournis).
3. Déclarer les variables d'environnement (`config/env.example`, au minimum le jeton du bot) dans l'environnement du service gateway et dans le shell qui lancera l'installation.
4. `bash scripts/install.sh` (simulation) puis `bash scripts/install.sh --apply` : déclare l'agent isolé, le compte Telegram (jeton référencé, jamais copié), fusionne la configuration, installe les skills partagés. Puis redémarrer le gateway.
5. Dans Telegram : « Commençons l'onboarding ». L'agent mène cinq actes (diagnostic, équipe, voix, lignes rouges et charte, calibration). Tant que ce n'est pas terminé, il ne produit rien de publiable.
6. À la fin de l'onboarding : `bash crons/install-crons.sh --enable-p1`, puis une première publication test avec « Go publie ».

**Avec Claude Code sur le serveur** : coller le prompt de `docs/PROMPT-CLAUDE-CODE.md` ; il guide chaque étape, vérifie, et n'écrit rien sans confirmation.

## Comment l'agent travaille
- **Trois régimes**, issus de la liste de besoins d'IMMO9 : *Auto* (veilles, déclinaisons, transcriptions, reporting : livré dans le groupe, jamais publié), *Semi-auto* (posts, carrousels, vidéos, newsletters : présentés, puis « Go »), *Assistant* (templates, campagnes, calendrier, recommandations : à la demande).
- **Deux validations maximum par pièce** : « Go » sur la proposition, « Go publie » sur le package final, toujours en réponse à la carte de la pièce, par une personne de `state/approvers.json`. Un pouce, un « ok », une question ou une phrase conditionnelle ne publient jamais. Les scripts enregistrent l'auteur, l'heure, le texte et l'empreinte du package ; la publication est refusée sans cet enregistrement ou si le package a changé. Ces verrous protègent contre l'erreur et la validation non autorisée ; leur portée exacte et l'isolation prévue ensuite sont décrites dans `docs/SECURITE.md`.
- **Faits sourcés et datés**, conformité immobilier (aucune promesse de rendement, mention des risques, aucune urgence fabriquée, aucune donnée client), coûts annoncés avant toute dépense.
- **Verrou d'onboarding** : la production est fermée tant que `state/onboarding.json` ne porte pas `complete`.

## Paliers
- **Palier 1 (livré, fonctionnel)** : veille quotidienne et hebdomadaire, posts, carrousels, déclinaisons multi-format, calendrier éditorial, boîte de sortie et publication sous « Go publie », reporting sur exports, onboarding.
- **Palier 2 (livré, à activer)** : infographie mensuelle, newsletters segmentées, podcast et audiograms, vidéo (HyperFrames, supermonteur), miniatures YouTube, rapport mensuel.
- **Palier 3 (feuille de route)** : connecteurs analytics par API, tendances et Google Trends via fournisseur, influenceurs, recherche multi-moteurs.
La correspondance ligne par ligne avec les 32 fonctionnalités demandées : `docs/MATRICE-FONCTIONNALITES.md`.

## Mises à jour
Chaque semaine : `bash scripts/update.sh` (récupère la dernière version, réapplique l'installation, relance le diagnostic). Les changements sont listés dans `CHANGELOG.md`. Les fichiers d'état et de mémoire ne sont jamais écrasés.

## Sécurité
Aucun secret dans le dépôt ni dans le workspace ; politique d'outils par agent ; publication impossible sans approbation enregistrée ; skills tiers relus avant installation. Détail : `docs/SECURITE.md`.

## Contact
Gil Benittah · iformy.gil@gmail.com
