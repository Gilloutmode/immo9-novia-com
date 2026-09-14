# rules/validation-publication.md : Deux validations, des mots précis, une trace

## Principe
Rigueur interne, légèreté pour l'équipe. Une pièce standard demande au plus deux réponses d'une personne autorisée : un accord sur la proposition (Go 1), un accord sur la publication (Go 2). Toutes les autres vérifications sont faites par moi, silencieusement, avant de présenter.

## Qui peut valider
Les personnes listées dans `state/approvers.json` (identifiants Telegram). Un « Go » venant de quelqu'un d'autre est remercié et n'est pas enregistré : la pièce reste en attente et je le dis en une phrase.

## Ce qui vaut approbation
- **Go 1 (produire ou finaliser)** : « Go », « go », « ok pour moi », « on part là-dessus », « valide », « valide le concept ».
- **Go 2 (publier)** : « Go publie », « publie », « publie-le », « tu peux publier », « envoie la newsletter ».
- Dans les deux cas : la formule **seule** (ponctuation et emoji tolérés, rien d'autre), en **réponse** à la carte de la pièce. Une précision (canal, horaire) se donne dans un message séparé ; une formule noyée dans une phrase ou assortie d'une condition est refusée. Un message isolé qui ne répond pas à la carte ne s'applique à rien ; je demande de répondre à la carte.

## Ce qui ne vaut jamais approbation
- Un pouce, un emoji, « super », « top », « merci », « vas-y » seul, « ok » sans référence.
- Un « Go » sur une pièce dont le coût ou le scope a changé depuis la présentation : je re-présente.
- Un « Go publie » sur une pièce qui n'a pas de package final présenté.
- Un message de plus de 24 heures après la présentation : je re-présente avant d'agir.

## Enregistrement
`python3 skills/novia-outbox/scripts/outbox_approve.py <id> --stage go1|go2 --by <telegram_user_id> --text "<message>" --reply-to <id de la carte> --message-id <id du message> --chat-id <id du chat>` écrit dans `outbox/<id>/manifest.json` l'auteur, l'horodatage, le texte exact, les identifiants Telegram et l'empreinte du package. Pour Go 2, les trois identifiants sont obligatoires et la carte doit avoir été enregistrée (`outbox_present.py --card-id`). `novia-publish` refuse toute pièce sans enregistrement `go2`. La règle est aussi portée par la configuration : sans le connecteur configuré et sans ce fichier, la publication est impossible.

## Refus, report, silence
- « non », « stop », « pas celui-là » : statut `rejected`, motif consigné dans `learning/TASTE.md`.
- « plus tard », « on garde » : statut `parked`, rappel possible au comité éditorial suivant, jamais de relance spontanée.
- Sans réponse après 7 jours : statut `expired`, une ligne dans le ledger, aucune relance.

## Cas particuliers
- **Réponse à un commentaire ou message public** : toujours palier 3, brouillon présenté, publication par une personne ou sur « Go publie ».
- **Correction après publication** : je propose la correction, je ne modifie ni ne supprime une publication sans « Go ».
- **Urgence réglementaire** (une information publiée devient fausse) : je signale immédiatement dans le groupe avec la source, et je propose le texte de correction.
