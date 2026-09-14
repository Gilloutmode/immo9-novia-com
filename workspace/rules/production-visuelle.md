# rules/production-visuelle.md — Visuels à la charte, lisibles, honnêtes

## Avant de produire
1. Lire `doctrine/BRAND_SYSTEM.md` : couleurs, typographies, logo, zones de sécurité par format, ce qui est interdit.
2. Choisir le gabarit dans `templates/` (carrousel, infographie, bannière, miniature, audiogram). Un gabarit existant se réutilise ; on n'improvise pas une mise en page.
3. Vérifier `learning/FEED_STATE.md` : cohérence avec les dernières publications (pas trois visuels identiques d'affilée, alternance des formats).

## Génération d'images
- Modèle et voie de génération : ceux de la configuration (`agents.entries.novia-com.imageModel` ou skill `nano-banana-pro` si configuré). Si la génération échoue, je le dis ; pas de repli silencieux vers un autre fournisseur.
- Un visuel généré ne représente jamais un programme réel comme une photo, ni une personne réelle. Pour un programme, on utilise les perspectives fournies par l'équipe, avec la mention « perspective non contractuelle ».
- Texte dans une image générée : seulement si la charte le permet et après vérification lettre par lettre (les modèles se trompent sur les mots). Sinon, le texte est posé par le gabarit HTML, jamais par le modèle.
- Cohérence des visages et des mains, absence d'éléments absurdes : contrôle visuel avant présentation.

## Formats et déclinaisons
- Canal primaire choisi avant la production ; les déclinaisons se font après validation, avec `novia-declinaison` (recadrage avec zones de sécurité, jamais d'étirement).
- Carrousel : 1080 × 1350 par défaut (Instagram et LinkedIn), 5 à 8 slides, une idée par slide, la première slide se comprend seule, la dernière ouvre (question sincère ou renvoi vers une ressource) sans appel à l'action creux.
- Infographie : 1080 × 1350 ou 1080 × 1080 ; chaque chiffre porte sa source et sa date sur l'image.
- Miniature YouTube : 1280 × 720, texte de 3 à 5 mots, visage ou objet net, contraste élevé ; deux variantes A/B livrées.
- Bannière : dimensions du support demandé ; texte lisible à petite taille ; logo dans la zone prévue.

## Contrôle qualité avant présentation
- Lisibilité sur téléphone (texte ≥ 40 px sur 1080 de large pour un corps de texte, titres plus grands).
- Zones de sécurité respectées (interface des plateformes).
- Orthographe et accents vérifiés.
- Sources et dates présentes sur tout chiffre.
- Fichiers nommés `nc-<id>-<canal>-<format>.<ext>` dans `outbox/<id>/`.
