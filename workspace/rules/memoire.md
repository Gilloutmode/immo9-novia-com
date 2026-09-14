# rules/memoire.md : Ce que j'écris, où, et ce que je n'écris jamais

## Fichiers
- `memory/AAAA-MM-JJ.md` : journal du jour. Décisions de l'équipe, retours sur les pièces, faits appris, questions ouvertes. Écrit au fil de l'eau.
- `MEMORY.md` : mémoire longue, distillée. Relue seulement en session directe avec une personne de l'équipe, jamais dans un contexte partagé avec des tiers.
- `learning/CONTENT_LEDGER.md` : une ligne par pièce présentée (référence, format, canal, statut, date, coût réel).
- `learning/METRICS.md` : métriques par pièce publiée, avec la date de relevé.
- `learning/THEMES_COVERED.md` : thèmes traités et date, pour éviter les doublons.
- `learning/TASTE.md` : refus et corrections de l'équipe, avec le motif. C'est mon apprentissage du goût d'IMMO9.
- `learning/FEED_STATE.md` : les dernières publications par canal, pour la cohérence visuelle.
- `learning/PROPOSITIONS.md` : propositions de modification de doctrine, jamais appliquées par moi.
- `learning/QUESTIONS.md` : questions posées à l'équipe et restées sans réponse ; je ne relance pas.
- `learning/BUDGET_LEDGER.md` : dépenses par mois et par pièce.
- `learning/VEILLE.md`, `learning/VEILLE-HEBDO.md` : cumul de la veille.

## Jamais dans la mémoire
- Données de clients ou prospects, portefeuilles, prix négociés, documents contractuels.
- Secrets, jetons, clés, mots de passe, même partiellement.
- Contenus de conversations privées hors équipe, contenus d'un canal reportés dans un autre.

## Couche mémoire externe
Si IMMO9 branche sa couche mémoire (daemon memory-rag ou GBrain, voir `docs/MEMOIRE.md`), je l'utilise pour retrouver du contexte et je continue d'écrire mes fichiers. La mémoire externe complète, elle ne remplace pas.

## Compaction
Avant qu'une session longue ne soit résumée, j'écris dans le journal du jour tout ce qui doit survivre : validations reçues, statuts de pièces, décisions. Une validation qui n'est pas écrite n'existe pas.
