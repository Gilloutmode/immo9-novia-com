# Mémoire de l'agent et couche mémoire d'IMMO9

## Ce que l'agent a par défaut
- `memory/AAAA-MM-JJ.md` : journal du jour, écrit au fil de l'eau.
- `MEMORY.md` : mémoire longue distillée chaque lundi.
- `learning/` : ledger des pièces, métriques, thèmes couverts, goûts (refus et corrections), état du feed, propositions, questions ouvertes, budget, veille.
- Les hooks internes d'OpenClaw (`session-memory`, `boot-md`) sont compatibles et recommandés.

## Brancher la couche mémoire d'IMMO9 (optionnel)
Deux options, selon ce qui est en place côté IMMO9 :
1. **memory-rag** (daemon existant) : activer le plugin pour l'agent `novia-com` avec une visibilité `team` limitée aux documents de communication (contenus du site, formations, programmes), **jamais** les portefeuilles clients. L'injection automatique de contexte doit rester légère (quelques extraits) ; l'agent continue d'écrire ses fichiers.
2. **GBrain** (si la migration décidée en juin est en place) : une source dédiée `novia-com` alimentée par `learning/` et `memory/`, exposée par un serveur MCP autorisé dans la configuration de l'agent (`tools.alsoAllow: ["gbrain-novia-com__*"]`). Même règle : aucune donnée client dans cette source.
Dans les deux cas, ajouter la ligne correspondante dans `AGENTS.md` §8 (mémoire externe) et vérifier avec une question test que l'agent ne voit rien d'autre que la communication.

## Ce qui ne va jamais dans une mémoire
Données de clients ou prospects, prix négociés, contrats, secrets, contenus de conversations privées hors équipe.
