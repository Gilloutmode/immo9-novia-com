# rules/crons.md — Contrat des tâches planifiées

## Règles communes
1. Première action : lire `state/onboarding.json`. Si `status` n'est pas `complete`, répondre `NO_REPLY`.
2. Une sortie courte dans le groupe ou `NO_REPLY`. Jamais de message vide de contenu.
3. Ni publication, ni production payante, ni message à un tiers.
4. Écrire son état (`state/`, `learning/`) pour ne pas se répéter.
5. En cas d'erreur d'outil : une ligne dans `memory/<date>.md`, et le signaler dans la prochaine sortie si l'erreur persiste deux fois.

## Les crons livrés (déclarés dans `crons/crons.json`, installés par `scripts/install-crons.sh`)
Palier 1, activés après l'onboarding :
- `veille-matin` : du lundi au vendredi à 7h30, digest de veille (marché, réglementaire, presse, concurrents).
- `proposition-du-jour` : du lundi au vendredi à 9h00, au plus deux propositions de posts ancrées dans la veille ou le calendrier, présentées en cartes.
- `comite-editorial` : lundi 8h30, plan de la semaine (carrousel, sujets, marronniers à venir sur 30 jours).
- `veille-hebdo` : vendredi 16h00, rapport concurrents et tendances de la semaine.
- `reporting-hebdo` : lundi 9h30, rapport des publications de la semaine passée si des métriques existent.
- `learning-loop` : lundi 20h30, boucle d'apprentissage (fichiers `learning/`), sans message si rien ne change.
- `sante` : tous les jours 6h00, vérification silencieuse (fichiers d'état présents, outbox sans pièce bloquée), message seulement en cas de problème.

Palier 2, livrés désactivés :
- `infographie-mensuelle` : le 2 du mois, brouillon d'infographie taux et prix.
- `newsletter-brouillon` : le 1er et le 15, brouillon de newsletter par persona.
- `podcast-prep` : un vendredi sur deux, script de podcast à valider.
- `reporting-mensuel` : le 3 du mois, rapport mensuel et benchmark.
- `calendrier-preview` : le 25 du mois, marronniers du mois suivant.

## Ce qu'un cron ne fait jamais
Décider seul d'un sujet sensible, publier, contacter quelqu'un, modifier la doctrine, dépenser.
