# rules/recherche-veille.md : Sources, fraîcheur, citation

## Sources
- Les sources autorisées sont dans `knowledge/sources-veille.json`, avec un niveau de confiance (officiel, professionnel, presse, social). Une information issue d'une source « social » ou « presse » sur un sujet réglementaire est vérifiée sur une source « officiel » avant d'être reprise dans un contenu.
- Les outils, dans l'ordre : le script `skills/novia-veille/scripts/veille_rss.py` (flux RSS et pages listées), l'outil `web_search` d'OpenClaw (si un fournisseur de recherche est configuré), `web_fetch` pour lire une page précise, `reddit-search` pour les questions Reddit, et, s'ils sont installés, `last30days` pour le pouls social et `deep-search` pour une recherche approfondie.
- Reddit, Quora et les forums : lecture seule. Un brouillon de réponse est présenté à l'équipe ; personne ne poste au nom d'IMMO9 sans « Go publie ».

## Fraîcheur
- Chaque item de veille porte une date de publication et une URL. Sans date : « date non trouvée », et l'item ne peut pas nourrir un contenu chiffré.
- Un chiffre de marché a une durée de vie : taux de crédit 1 mois, prix du neuf 1 trimestre, dispositif fiscal jusqu'à la prochaine loi de finances ou décret. Au-delà, je re-vérifie avant de réutiliser.
- Dédoublonnage : `state/veille-seen.json` garde les URL déjà remontées ; je ne répète pas un item, sauf évolution.

## Citation dans un contenu public
- Forme : « selon [source], [date] » ou un lien en commentaire ou en fin de légende selon le canal.
- Jamais de citation textuelle d'un article au-delà d'une phrase courte ; je reformule et je renvoie à la source.
- Jamais de chiffre « environ » ou « on estime » sans source.

## Ce que la veille produit
- Digest du matin dans le groupe (3 à 6 lignes) et fichier `learning/VEILLE.md` (cumul, par date).
- Rapport hebdomadaire concurrents et tendances (cron dédié) dans `learning/VEILLE-HEBDO.md`.
- Propositions de contenus tirées de la veille : au plus deux par jour, présentées au comité éditorial ou dans le digest.
