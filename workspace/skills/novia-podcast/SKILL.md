---
name: novia-podcast
description: "Podcast IMMO9 bimensuel : script à valider, voix (humaine enregistrée ou synthèse autorisée par la doctrine), montage et mixage, transcription et show notes (auto), audiograms 1:1 et 9:16 avec forme d'onde par ffmpeg (scripts/audiogram.sh, auto à chaque épisode). Hébergement et flux RSS via l'outil de podcast d'IMMO9."
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"bins": ["ffmpeg", "ffprobe"]}}}
---

# novia-podcast : un sujet, dix minutes, des extraits qui circulent

## Épisode (cron `podcast-prep` un vendredi sur deux, semi-auto)
1. Sujet ancré (veille du mois, question récurrente des clients, échéance) et persona. Vérifier `THEMES_COVERED.md`.
2. Script parlé dans `outbox/<id>/script.md` : accroche (20 s), trois parties, repère final. Phrases courtes, chiffres sourcés (les sources vont dans les show notes). 10 à 20 minutes à l'oral (1 300 à 2 600 mots).
3. Présentation du script (Go 1). Après Go : enregistrement par une personne de l'équipe (recommandé) ou voix de synthèse si `doctrine/LINES.md` l'autorise (outil `tts` d'OpenClaw ou service configuré, coût annoncé).
4. Montage : nettoyage, jingle et musique libres de droits documentés dans le manifest (`music_license`), niveaux ; `ffmpeg` avec les commandes de `skills-shared/sound-integration` si installé.
5. Package final : fichier audio, transcription, show notes, audiograms, visuel de couverture. « Go publie » puis dépôt sur l'hébergeur (manuel ou connecteur, voir `connectors/README.md`).

## Transcription et show notes (auto)
- Transcription : outil `media.audio` d'OpenClaw (activé dans la configuration) ou service de transcription configuré. Relire les noms propres et les chiffres.
- Show notes : résumé en 5 lignes, chapitres horodatés, sources citées, mention des risques si contenu investisseur.

## Audiograms (auto)
```bash
bash skills/novia-podcast/scripts/audiogram.sh outbox/<id>/episode.mp3 outbox/<id>/cover.png "Titre court" outbox/<id>/audiograms --start 00:03:10 --duration 45
```
Produit `audiogram-1x1.mp4` et `audiogram-9x16.mp4` (forme d'onde, titre, couverture). Choisir 2 ou 3 extraits de 30 à 60 secondes qui se comprennent seuls. Sous-titres : ajouter avec `supermonteur` si installé.
