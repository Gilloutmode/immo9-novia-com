# BOOT.md — Checklist de démarrage du gateway

À chaque démarrage du gateway (hook interne `boot-md`) :

1. Lire `state/onboarding.json`. Si le fichier manque ou si `status` n'est pas `complete`, noter dans `memory/<date>.md` que l'agent est en onboarding : aucune production, aucune publication, aucun cron créatif ne doit produire.
2. Lire `state/channels.json` et `state/approvers.json`. Si l'un des deux manque, l'écrire dans le journal du jour et le signaler au premier message de Julien.
3. Vérifier que `outbox/` ne contient pas de pièce en statut `presented` depuis plus de 7 jours ; si oui, les passer en `expired` et le noter dans `learning/CONTENT_LEDGER.md`.
4. Ne rien envoyer sur Telegram au démarrage.
