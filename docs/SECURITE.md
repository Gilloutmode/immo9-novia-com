# Sécurité et confidentialité

## Secrets
- Aucun secret dans le dépôt, ni dans le workspace, ni dans les crons. Les jetons vivent dans l'environnement du service gateway ; la configuration ne contient que des références (`${VAR}`) et `install.sh` n'injecte que les variables présentes.
- L'agent a pour règle de ne jamais lire, citer ni copier un secret ; une clé manquante se signale par son nom.
- Rotation : changer un jeton = mettre à jour la variable, redémarrer le gateway. Les jetons de plateformes sociales expirent ; le cron `sante` remonte les échecs de publication.

## Isolation
- Agent isolé (`agents add`) : workspace, répertoire d'état et sessions propres. Pas d'accès aux autres agents ni au CRM.
- Compte Telegram dédié avec allowlist des personnes et du groupe (`dmPolicy` et `groupPolicy` en `allowlist`). Une personne hors liste n'obtient pas de réponse.
- Politique d'outils par agent (`config/openclaw.novia-com.patch.json5`) : profil `coding` avec exec, fichiers, navigateur, recherche, image et message ; outils élevés désactivés.
- Le workspace ne contient aucune donnée client ; la charte l'interdit et les scripts ne lisent que le workspace.

## Publication
- Aucune publication sans enregistrement `go2` par une personne de `state/approvers.json`, en réponse à la carte, avec un mot d'approbation, dans les 24 heures ; vérifié par `outbox_approve.py` et `publish.py`, testé par `scripts/acceptance.sh`.
- Les crons n'ont pas le droit de publier ni de dépenser (contrat et prompts).
- Toute publication laisse une trace : manifest, ledger, historique horodaté.

## Skills tiers
- Les skills de `skills-shared/` ont été relus et nettoyés. Les skills à installer depuis une source publique (`skills-shared/INSTALL.md`) se vérifient avec `openclaw skills verify` et une lecture de leur `SKILL.md` et de leurs scripts avant usage.
- Un skill non relu n'entre pas en production.

## Serveur
- Moindre privilège : le gateway tourne sous un utilisateur dédié ; `chromium` en mode headless sans sandbox seulement si l'utilisateur n'est pas root, sinon ajouter un utilisateur.
- Sauvegardes : `openclaw.json` est sauvegardé avant chaque patch (`.bak-novia-<date>`) ; le workspace est dans git ; l'état local (`state/`, `learning/`, `memory/`, `outbox/`) mérite une sauvegarde régulière côté IMMO9.
- Mises à jour d'OpenClaw : pas de mise à jour automatique ; suivre les notes de version, tester sur le profil de développement si disponible.

## Données personnelles
- Newsletters : uniquement des listes consenties de l'outil d'emailing, avec désinscription (le script refuse un HTML sans lien de désinscription).
- Veille : lecture de sources publiques, dédoublonnage local ; pas de collecte de profils.
- Mémoire de l'agent : décisions et apprentissage éditorial, jamais de données de prospects.
