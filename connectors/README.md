# Connecteurs : ce que Julien branche, et dans quel ordre

Novia Com produit dans `workspace/outbox/`. La publication passe par un **adaptateur** (`workspace/skills/novia-publish/adapters/`) choisi canal par canal dans `workspace/state/channels.json`. Les secrets vivent dans l'environnement du gateway OpenClaw (`config/env.example`), jamais dans le dépôt ni dans le workspace.

## Ordre conseillé
1. **Telegram** (obligatoire) : bot dédié via @BotFather, groupe « Novia Com » avec l'équipe, identifiants des personnes (commande `openclaw directory` ou @userinfobot). → `NOVIA_TELEGRAM_BOT_TOKEN`, `state/channels.json` (`telegram_group_id`), `state/approvers.json`.
2. **Publication multi-plateformes en une clé** : upload-post.com (recommandé pour démarrer). L'entreprise (Espagne) publie son accord de traitement des données ; c'est elle qui détient les applications validées par Meta, LinkedIn, Google et TikTok, donc aucune revue d'application à passer côté IMMO9. Plan Basic : 5 profils (1 profil = 1 compte par plateforme), publications illimitées, 24 $ par mois ou 16 $ par mois en annuel (tarifs relus le 14/09/2026 sur docs.upload-post.com/resources/pricing-and-limits). Plafonds par compte et par 24 h : Instagram 50, TikTok 15, LinkedIn 150, YouTube 10, Facebook 25. → `UPLOAD_POST_API_KEY`, `state/channels.json` (`adapter: upload_post`, `user`, `platform`).
3. **Newsletter** : Brevo (listes par persona, expéditeur vérifié). → `BREVO_API_KEY`, réglages `sender`, `list_ids`, `send: false` pour créer en brouillon.
4. **Analytics** : exports CSV depuis Meta Business Suite, LinkedIn Pages et YouTube Studio déposés dans `outbox/_metrics/` (format `date,piece_id,channel,metric,value,source`). Les connecteurs analytics par API sont au palier 2.
5. **Veille** : flux RSS vérifiés livrés ; alertes Google en flux RSS pour les mentions de marque (gratuit) ; Reddit en lecture via une application « script » (gratuite, usage non commercial léger ; un usage commercial à volume demande un accord Reddit). → `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` (optionnel).

## Alternatives à upload-post (relues le 14/09/2026)
- Post Bridge : 29 $ par mois (5 comptes), MCP inclus, skill OpenClaw annoncée. API en supplément non affiché.
- Zernio (ex Late) : à l'usage, 2 comptes gratuits puis 6 $ par compte et par mois jusqu'à 10 comptes.
- Ayrshare : 149 $ par mois (1 profil, jusqu'à 14 comptes), orienté agences.
- APIs natives (adaptateurs livrés `meta_graph`, `linkedin`, `youtube`) : IMMO9 enregistre ses propres applications, passe les revues (Meta App Review, LinkedIn Community Management, Google OAuth), gère les jetons. Plus de contrôle, plus de travail. Instagram exige en plus une URL publique pour chaque média (réglage `public_base_url`).

## Ce que chaque adaptateur attend (résumé ; détail en tête de chaque fichier)
| Adaptateur | Variables | Réglages `state/channels.json` |
|---|---|---|
| `dryrun` | aucune | aucun (simulation) |
| `upload_post` | `UPLOAD_POST_API_KEY` | `user`, `platform` |
| `meta_graph` | `META_PAGE_ACCESS_TOKEN` | `ig_user_id`, `fb_page_id`, `public_base_url` |
| `linkedin` | `LINKEDIN_ACCESS_TOKEN` | `organization_urn` ; version d'API dans le fichier |
| `youtube` | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` | `privacy`, `category_id` |
| `brevo` | `BREVO_API_KEY` | `sender`, `list_ids` par persona, `send` |

## Points de vigilance
- X (Twitter) facture désormais à la publication ; upload-post retire les liens par défaut pour rester au tarif bas. Hors périmètre de la v1.
- TikTok : préférer la publication en brouillon (l'équipe publie depuis l'application, meilleure portée organique selon upload-post).
- Les limites Instagram, LinkedIn et YouTube évoluent : le fichier de chaque adaptateur porte la version d'API à ajuster.
- Test avant production : `python3 workspace/skills/novia-publish/scripts/publish.py <id> --dry-run`, puis une première publication réelle sur une pièce test avec « Go publie », en compte privé YouTube si besoin.
