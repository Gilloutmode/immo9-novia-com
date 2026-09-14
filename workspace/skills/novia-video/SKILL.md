---
name: novia-video
description: "Vidéo IMMO9 : vidéos courtes ex nihilo à partir d'infographies ou de cartes (HyperFrames), montage de rushes d'interviews avec cut dynamique et sous-titres (supermonteur), miniatures YouTube en deux variantes A/B (gabarit HTML). Semi-auto, à la demande. Dépend des skills partagés hyperframes et supermonteur (voir skills-shared/INSTALL.md)."
metadata: {"openclaw": {"emoji": "🎬", "requires": {"bins": ["ffmpeg"]}}}
---

# novia-video : palier 2, prêt dès que les skills partagés sont installés

## Vidéo courte ex nihilo (F4)
1. Script parlé de 30 à 60 secondes (`novia-editorial`), une question, une réponse, un repère. Sources dans la description.
2. Composition HyperFrames (skill `hyperframes`, `npx hyperframes init`) : fond aux couleurs de la charte, titres animés, chiffres sourcés à l'écran, logo. Rendu 1080 × 1920. Voix : enregistrement d'une personne de l'équipe ou synthèse autorisée (coût annoncé).
3. Sous-titres mot à mot avec `supermonteur` (transcription verbatim puis sous-titres animés). Musique libre de droits documentée.
4. Déclinaisons 1:1 et 16:9 avec `novia-declinaison --pad`. Package final, carte, « Go publie ».

## Montage de rushes d'interview (F5)
1. Rushes déposés par l'équipe dans `outbox/<id>/rushes/`. Transcription (`media.audio` ou `supermonteur`).
2. Sélection des passages : ce qui répond à une question précise d'une persona, 1 à 3 minutes. Proposition de découpage (horodatages) présentée en Go 1.
3. Montage : cuts sur les respirations, plans de coupe fournis par l'équipe, sous-titres, carton titre et fin à la charte, niveaux audio. Aucune image générée ne remplace une image réelle d'interview.
4. Déclinaison 9:16 des meilleurs extraits (30 à 60 secondes).

## Miniatures YouTube A/B (F9)
1. Deux gabarits contrastés (fond couleur primaire avec visage ou objet net ; fond photo avec bandeau) dans `templates/miniature/` (HTML 1280 × 720, tokens de charte). Texte de 3 à 5 mots, lisible à 200 px de large.
2. Rendu avec `render_html.sh <dossier> 1280 720`. Livrer `miniature-A.png` et `miniature-B.png`. Le test se fait dans YouTube Studio (fonction « Tester et comparer ») par l'équipe.

## Règles
- Un rendu vidéo long (> 10 minutes de calcul) est annoncé avant d'être lancé.
- Aucune vidéo générative de personnes ou de programmes réels ; les outils génératifs (skills `veo`, `seedance-video` s'ils sont installés) ne servent qu'à des ambiances abstraites, avec coût annoncé.
