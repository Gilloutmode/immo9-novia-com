---
name: novia-publish
description: "Publication d'une pièce IMMO9 approuvée (« Go publie » enregistré par novia-outbox) via le connecteur configuré dans state/channels.json : dryrun, upload-post, meta-graph (Instagram et Facebook), linkedin, youtube, brevo (newsletter). Refuse toute pièce sans approbation go2. Jamais appelé par un cron."
metadata: {"openclaw": {"emoji": "🚀", "requires": {"bins": ["python3"]}}}
---

# novia-publish : publier, seulement après « Go publie »

## Ce que fait `scripts/publish.py <id> [--channel linkedin] [--dry-run] [--preview]`
1. Charge `outbox/<id>/manifest.json` et vérifie : onboarding `complete`, pièce non test, statut `approved`, enregistrement `approvals.go2` présent, auteur dans `state/approvers.json`, approbation de moins de 24 heures, empreinte du package identique à celle approuvée, canaux demandés inclus dans les canaux approuvés, aucune publication déjà en cours (verrou par pièce). Les cibles déjà publiées ne sont pas rejouées en cas de reprise.
2. Charge `state/channels.json` : pour chaque canal, le nom de l'adaptateur et ses réglages (identifiants de compte, URL de base publique). Les secrets viennent des variables d'environnement déclarées dans `skills.entries.novia-publish.env` de la configuration OpenClaw, jamais d'un fichier du workspace.
3. Appelle l'adaptateur (`adapters/<nom>.py`) avec la légende du canal (`manifest.captions[canal]`) et les fichiers (`manifest.assets` filtrés par canal).
4. Écrit chaque résultat (état, identifiant, URL, horodatage) dans le manifest dès qu'il est obtenu. États possibles : `published` (succès terminal), `submitted` (accepté, confirmation à suivre), `processing`, `draft_remote` (brouillon créé chez le prestataire, envoi manuel), `simulated`. Le statut de la pièce passe à `published` seulement si toutes les cibles approuvées sont `published` ; sinon `submitted`, et l'agent le dit avec ces mots dans le groupe. Ledger et `FEED_STATE.md` mis à jour.
5. En cas d'échec : le manifest garde son statut, l'erreur est écrite dans `history`, l'agent la rapporte telle quelle. Une reprise ne republie pas les cibles déjà réussies.

`--preview` montre ce qui serait envoyé (adaptateur, fichiers, légende) sans approbation et sans appel externe. `--dry-run` passe par l'adaptateur `dryrun` après toutes les vérifications ; ses résultats sont `simulated` et ne comptent jamais comme une publication.
Pour l'adaptateur Meta, les médias à publier sont copiés dans `export/<id>/`, seul dossier à exposer publiquement (jamais `outbox/`).

## Adaptateurs livrés
- `dryrun` : simulation complète, toujours disponible.
- `upload_post` : API upload-post.com (un seul jeton, envoi de fichiers, multi-plateformes). Réglages : `user` (profil upload-post), `platforms`. Secret : `UPLOAD_POST_API_KEY`.
- `meta_graph` : Instagram (compte professionnel) et Page Facebook via l'API Graph. Contrainte : Instagram exige une URL publique pour l'image ou la vidéo ; le réglage `public_base_url` doit servir le dossier `outbox/` (voir `connectors/README.md`). Secrets : `META_PAGE_ACCESS_TOKEN`, réglages `ig_user_id`, `fb_page_id`.
- `linkedin` : publication d'un post texte ou image sur une Page (API Community Management). Secret : `LINKEDIN_ACCESS_TOKEN`, réglage `organization_urn`.
- `youtube` : dépôt d'une vidéo (API YouTube Data v3, OAuth). Secrets : `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`.
- `brevo` : création d'une campagne email en brouillon puis envoi (API Brevo). Secret : `BREVO_API_KEY`, réglages `sender`, `list_ids` par persona.

Chaque adaptateur documente ses prérequis en tête de fichier. Un adaptateur non configuré s'arrête avec un message qui nomme le réglage ou la variable manquante, sans jamais afficher une valeur secrète.

## Règles
- Ce skill n'est jamais appelé par un cron, ni sans approbation `go2`.
- Une publication programmée (« publie mardi 8h30 ») se fait par un rappel du cron `sante` ou un one-shot OpenClaw qui demande à l'agent d'appeler ce script au moment voulu, avec l'approbation déjà enregistrée et encore valide (24 heures). Au-delà, l'agent re-présente.
- Après publication, l'agent envoie dans le groupe une ligne : canal, heure, lien.
