# Limites connues et points de vigilance

## Côté agent
- **Rendu HTML** : les carrousels et infographies sont rendus par Chromium headless. Sans Chromium sur le serveur, l'outil `browser` d'OpenClaw fait les captures (plus lent, moins automatisable). Recommandé : `apt install chromium`.
- **Texte sur les audiograms** : le filtre `drawtext` de ffmpeg (libfreetype) est nécessaire pour incruster le titre ; le script détecte son absence et rend sans titre.
- **Reddit** : lecture bloquée sans application OAuth ; volumes faibles, usage non commercial. Quora : pas d'API.
- **Instagram en API native** : exige une URL publique par média ; l'adaptateur upload-post évite cette contrainte.
- **Tendances Google** : pas d'API ouverte ; palier 3 via fournisseur.
- **Faits réglementaires** : la base `knowledge/dispositifs-2026.md` porte des niveaux de confiance ; plusieurs chiffres (barèmes PTZ, statut du bailleur privé, date de fin de l'exonération de donation) restent à confirmer sur le texte officiel avant publication. L'agent a pour règle de ne citer qu'au niveau officiel.
- **Dates de salons** : seules celles de Toulouse sont confirmées par le site de l'organisateur ; les autres sont marquées « à confirmer ».

## Côté OpenClaw (observé en septembre 2026)
- Un bug ouvert sur la sélection des skills (issue openclaw #143155, 2026.9.3) peut pousser l'agent à agir avant d'avoir lu un skill à étapes. La charte impose la lecture du skill et les scripts portent les verrous : l'effet est limité, mais à surveiller lors des premières semaines.
- Les crons demandent un gateway démarré ; `crons/install-crons.sh` s'arrête proprement sinon.
- `channels.telegram.defaultAccount` doit être défini quand plusieurs comptes Telegram existent (l'installateur le rappelle).
- Les références `${VAR}` de la configuration doivent pointer vers des variables existantes : l'installateur n'injecte que celles qui sont définies ; relancer `scripts/install.sh --apply` après en avoir ajouté.

## Côté organisation
- L'agent ne remplace pas la validation : deux « Go » par pièce sont attendus. Sans réponse, les pièces expirent au bout de sept jours, sans relance.
- La qualité de la voix dépend de l'acte 2 de l'onboarding (corpus réel d'IMMO9) : plus l'équipe corrige au début, plus l'agent ressemble à IMMO9.
- Les plafonds de coût sont des valeurs de départ (2 € par pièce, 60 € par mois) à ajuster avec David.
