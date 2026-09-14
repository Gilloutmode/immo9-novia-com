# FORMATS.md : Les formats déclarés

> Un format est un contrat entre une intention, une surface et une métrique. Les neuf formats ci-dessous couvrent la liste de besoins IMMO9. Un format se déclare avant la première production ; il se juge après six observations au moins, jamais avant.

| Id | Nom | Intention | Surface | Canevas | Métrique primaire | Régime |
|---|---|---|---|---|---|---|
| F1 | Post pédagogique | faire comprendre une notion du neuf à une persona | LinkedIn, Instagram (légende), Facebook | texte 120 à 220 mots + 1 visuel | enregistrements et commentaires utiles | Semi-auto, quotidien |
| F2 | Carrousel pédagogique | faire garder un repère en 5 à 8 étapes | LinkedIn (PDF), Instagram | 1080 × 1350, 5 à 8 slides | enregistrements, temps de lecture | Semi-auto, hebdomadaire |
| F3 | Infographie taux et prix | donner le repère chiffré du mois | Instagram, LinkedIn, newsletter | 1080 × 1350 ou 1080 × 1080 | partages, reprises presse | Auto (brouillon), mensuel |
| F4 | Vidéo courte | une question, une réponse, 30 à 60 s | Instagram Reels, YouTube Shorts, TikTok | 1080 × 1920, sous-titres | vues complètes, partages | Semi-auto, à la demande |
| F5 | Montage d'interview | preuve de terrain, 1 à 3 min | YouTube, LinkedIn | 1920 × 1080 + déclinaison 9:16 | temps de visionnage | Semi-auto, à la demande |
| F6 | Podcast et audiogram | approfondir un sujet, 10 à 20 min | plateformes de podcast, audiogram 1:1 et 9:16 | audio + visuel | écoutes complètes, abonnés | Semi-auto (épisode), Auto (audiogram), bimensuel |
| F7 | Newsletter segmentée | tenir une relation par persona | email | HTML 640 px, une idée principale | ouvertures, clics, réponses | Semi-auto, bimensuel à mensuel |
| F8 | Bannière et gabarit | soutenir une campagne ou un programme | display, réseaux, site | dimensions du support | clics, conversions déclarées | Semi-auto (bannière), Assistant (gabarit) |
| F9 | Miniature YouTube A/B | faire cliquer sans tromper | YouTube | 1280 × 720, deux variantes | taux de clic | Semi-auto, à chaque upload |

## Règles communes
- Une pièce = un format = une langue. Pas de mélange de langues dans un même asset.
- Le format et le canal primaire sont fixés à la présentation (Go 1) ; en changer relance la présentation.
- Chaque format nomme sa métrique avant la première production, sinon la mesure devient une justification a posteriori.
- Les déclinaisons (`novia-declinaison`) ne créent pas un nouveau format : elles adaptent une pièce validée à d'autres surfaces.

## Ce qu'il faut pour chaque format (résumé, détail dans les skills)
- F1 : persona, angle, source datée, visuel à la charte, légendes natives.
- F2 : plan slide par slide, première slide autonome, dernière slide ouverte, PDF pour LinkedIn et images pour Instagram.
- F3 : données du mois avec sources et dates sur l'image, gabarit `templates/infographie/`.
- F4 et F5 : script ou rushes, sous-titres vérifiés, musique libre de droits documentée.
- F6 : script validé, voix (humaine ou synthèse autorisée), transcription, show notes, audiogram.
- F7 : segment, objet, pré-en-tête, corps, lien de désinscription, test de rendu.
- F8 : brief du support, dimensions, texte court, zone logo.
- F9 : titre de la vidéo, visage ou objet, deux variantes contrastées, test manuel dans YouTube Studio.
