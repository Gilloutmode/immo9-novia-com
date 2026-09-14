---
name: supermonteur
triggers: ["supermonteur", "sous-titrer une vidéo", "auto-captions", "reel sous-titré", "monter un reel"]
description: Transforme une rush parlée en reel 9:16 sous-titré automatiquement : transcription verbatim ElevenLabs Scribe + sous-titres animés HyperFrames calés au mot près, avec le mot courant surligné. Rapide, lisible, prêt à poster. Use when: sous-titrer une vidéo, auto-captions, monter vite un reel/short à partir d'un talking-head.
---

# REEL CAPTIONS : sous-titrage auto qui retient

Tu déposes une rush parlée, tu repars avec un **reel 9:16 sous-titré, propre et animé**, prêt à publier. Des sous-titres calés au mot, le mot courant qui s'allume, une lecture impeccable même sans le son : exactement ce qui fait scroller moins vite.

Trois étapes : **transcrire → (option) resserrer → sous-titrer → exporter.**

## Pré-vol
```bash
ls <rush>.mp4                                   # la rush 9:16 (talking-head)
grep -c ELEVENLABS_API_KEY .env                 # clé ElevenLabs (ou export ELEVENLABS_API_KEY=...)
ffprobe -v error <rush>.mp4                      # 1080x1920 idéal
npx --yes hyperframes@0.6.81 --version           # le moteur de rendu
```
Outils du skill : `{baseDir}/assets/` (`transcribe.py` + `build.mjs`). Bosser dans un dossier projet, ex. `caption-out/`.

## 1. Caler la rush en 1080×1920
```bash
ffmpeg -y -i <rush>.mp4 -vf "scale=1080:1920:flags=lanczos" -c:v libx264 -crf 18 -c:a aac clip.mp4
# (déjà en 9:16 -> cp <rush>.mp4 clip.mp4)
```

## 2. Transcription verbatim au mot près (ElevenLabs Scribe)
```bash
python3 {baseDir}/assets/transcribe.py clip.mp4 --language fr --out clip.words.json
# --model scribe_v1 par défaut ; teste --model scribe_v2 si activé sur ton compte (WER souvent meilleur)
```
Scribe sort le texte **mot à mot avec des timings précis** : les sous-titres tombent pile sur la voix, sans dérive, sans rater les répétitions. Retry réseau + validation des timings intégrés ; échoue clair si la transcription est vide.

## 3. Resserrer les blancs (option, pour un rythme plus punchy)
```bash
ffmpeg -i clip.mp4 -af "silencedetect=n=-33dB:d=0.35" -f null -    # repérer les vrais blancs
# recouper les plages de parole (trim/concat ffmpeg) en gardant ~0.1s avant chaque mot
# puis re-transcrire le clip coupé (étape 2)
```
Garde ~0.1s avant chaque mot pour ne jamais clipper les attaques.

## 4. Sous-titres animés
```bash
mkdir -p caption-out && cp clip.mp4 clip.words.json caption-out/ && cd caption-out
node "{baseDir}/assets/build.mjs" --cam clip.mp4 --words clip.words.json --out index.html --accent "#28e0a8"
```
Génère : cam plein écran + lignes de 1–4 mots en **Montserrat 800 capitales**, **le mot prononcé qui s'allume** (couleur d'accent + léger pop), contour renforcé lisible sur n'importe quel fond, ancrés dans la **zone safe** (au-dessus de l'UI réseaux). GSAP est copié en local à côté du `index.html` → rendu **offline et déterministe**. Change `--accent` pour la couleur de marque ; police/taille/position dans `build.mjs`.

## 5. Rendu
```bash
npx --yes hyperframes@0.6.81 lint                 # doit être 0 erreur / 0 warning
npx --yes hyperframes@0.6.81 render . -q high      # -> renders/<dossier>_<date>.mp4
```
La voix est déjà dans le rendu (piste audio de la cam). **Livrable = le mp4 dans `renders/`**, prêt à poster.

## À savoir (pour que ça marche du premier coup)
- La balise `<video>` de la cam est **statique** (le générateur l'émet) : un clip média créé en JS rend noir.
- Vidéo `muted` + `<audio id>` séparé pour la voix.
- Compo **déterministe** : pas de `Date.now`/`Math.random`/réseau. GSAP est **vendorisé** (`assets/vendor/`) et copié à côté du rendu : aucun CDN.
- Sous-titres ancrés par le bas dans la **zone safe** (`bottom:430`, au-dessus de l'UI TikTok/Reels ~320-340 px). Police **Montserrat** (auto-résolue par le renderer, pas de fallback).
- Robustesse : chemins échappés (pas d'injection ffprobe), texte HTML-échappé (accents/emoji préservés), timings triés/normalisés, `--accent` validé.
- Personnalisable : couleur d'accent (`--accent`), police/taille/position dans `build.mjs`.

## Gestes ffmpeg annexes (hors sous-titrage)

Aucun script externe n'est requis ; les commandes ci-dessous suffisent. Toujours vérifier le résultat avec `ffprobe`.

```bash
# Repérer les silences (seuil -35 dB, durée ≥ 0,5 s) pour couper les blancs
ffmpeg -i rush.mp4 -af "silencedetect=noise=-35dB:d=0.5" -f null - 2>&1 | grep silence_
# Couper un segment sans réencoder (début 00:00:03, durée 12 s)
ffmpeg -ss 00:00:03 -t 12 -i rush.mp4 -c copy segment.mp4
# Recadrage 9:16 centré (1080×1920)
ffmpeg -i rush.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart rush-9x16.mp4
# Normalisation de niveau sonore (voix parlée, cible -16 LUFS, plafond -1,5 dBTP)
ffmpeg -i in.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 160k out.mp4
# Export plateforme (Reels, Shorts, TikTok) : H.264 + AAC, GOP 2 s, faststart
ffmpeg -i in.mp4 -c:v libx264 -preset medium -crf 20 -g 50 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart reels.mp4
# Vérification (dimensions, durée, débit)
ffprobe -v error -show_entries stream=width,height,codec_name,bit_rate:format=duration -of default=noprint_wrappers=1 reels.mp4
```
Les sous-titres restent produits ici (HyperFrames), pas par le filtre `subtitles` de ffmpeg (absent de certaines distributions).
