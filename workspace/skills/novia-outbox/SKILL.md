---
name: novia-outbox
description: "Cycle de vie d'une pièce de contenu IMMO9 : création du manifest (outbox/<id>/manifest.json), présentation, enregistrement des approbations « Go » et « Go publie » par une personne autorisée, statuts (rejected, parked, expired, published) et ledger. À utiliser pour toute pièce destinée à être publiée, avant novia-publish."
metadata: {"openclaw": {"emoji": "🗂️", "requires": {"bins": ["python3"]}}}
---

# novia-outbox : la boîte de sortie et ses approbations

Chaque pièce vit dans `outbox/<id>/` avec un `manifest.json`. Les scripts sont la seule façon légitime de changer un statut : ils vérifient qui approuve, quand, et laissent une trace. `novia-publish` refuse toute pièce sans approbation `go2` enregistrée par ce skill.

## Scripts (tous relatifs au dossier du skill ; `python3 <script> --help` pour l'aide)
- `scripts/outbox_new.py --format F2 --persona P1 --channel linkedin --title "Le PTZ 2026 en 5 questions" [--source URL ...] [--cost 0.4 --ceiling 1.5]`
  Crée `outbox/nc-AAAAMMJJ-NN/manifest.json` (numéro auto-incrémenté) et le dossier de la pièce. Affiche l'identifiant.
- `scripts/outbox_present.py <id> [--stage go1|final] [--score N] [--card-id <id du message Telegram>] [--test]`
  Marque la pièce comme présentée (horodatage), ce qui ouvre la fenêtre d'approbation de 24 heures. Refusé tant que l'onboarding n'a pas atteint l'acte 4. Pour `final` : score qualité ≥ 85, `quality.compliance_checked` à `true` dans le manifest, légendes présentes ; l'empreinte du package (légendes, fichiers, canaux, plafond) est enregistrée. `--test` marque une pièce de calibration, jamais publiable. Après l'envoi de la carte, relancer avec `--card-id` pour lier l'approbation au message.
- `scripts/outbox_approve.py <id> --stage go1|go2 --by <telegram_user_id> --text "<message exact>" [--reply-to <id du message auquel il répond>] [--message-id <id>] [--chat-id <id>]`
  Enregistre l'approbation si l'auteur est dans `state/approvers.json`, si le message est **exactement** une formule d'approbation du contrat (ponctuation et emoji tolérés, aucun autre mot, ni négation, question ou condition), si la présentation date de moins de 24 heures, et, pour Go 2, si le package est celui présenté (empreinte du plan d'envoi : légendes, titre, persona, fichiers dans l'ordre et leurs canaux, plafond) et si `--reply-to`, `--message-id` et `--chat-id` sont fournis et cohérents (carte enregistrée, chat = groupe ou DM d'une personne autorisée). Sinon, explique le refus. Go 2 n'est accepté que sur un package final présenté.
- `scripts/outbox_set.py <id> --status rejected|parked|expired [--note "motif"]`
  Ferme ou met en attente une pièce, avec trace dans `learning/CONTENT_LEDGER.md` et, pour un refus, dans `learning/TASTE.md`.
- `scripts/outbox_status.py [--status presented]`
  Liste les pièces et leur statut (utilisé par le cron `sante` et par BOOT.md).

## Statuts
`draft` → `presented` → `go1` → `final_presented` → `approved` (go2) → `submitted` (envoyé, confirmation en attente) → `published`. Sorties latérales : `rejected`, `parked`, `expired`.

## Règles
- Une approbation se donne **en réponse** à la carte de la pièce ; l'agent transmet au script l'identifiant Telegram de l'auteur et le texte exact du message. Il n'invente jamais une approbation.
- Un « Go » venu d'une personne hors `state/approvers.json` n'est pas enregistré : l'agent remercie et le dit.
- Une pièce présentée depuis plus de 7 jours passe en `expired` (cron `sante`).
- Les fichiers produits pour la pièce (textes, images, vidéos, PDF) sont rangés dans `outbox/<id>/` et listés dans `manifest.assets`.

## Exemple complet
```bash
ID=$(python3 skills/novia-outbox/scripts/outbox_new.py --format F1 --persona P1 --channel linkedin --title "Apport : combien faut-il vraiment ?" --source "https://www.service-public.fr/…")
# … production dans outbox/$ID/ …
python3 skills/novia-outbox/scripts/outbox_present.py $ID --stage final --score 88   # manifest : quality.compliance_checked = true
# envoi de la carte dans le groupe, puis : outbox_present.py $ID --stage final --card-id <message_id>
# L'équipe répond « Go publie » (user 123456789) à la carte (message 4567) :
python3 skills/novia-outbox/scripts/outbox_approve.py $ID --stage go2 --by 123456789 --text "Go publie" --reply-to <id de la carte> --message-id 4567 --chat-id <id du groupe>
python3 skills/novia-publish/scripts/publish.py $ID
```
