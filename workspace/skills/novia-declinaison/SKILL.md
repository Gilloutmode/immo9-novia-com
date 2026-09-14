---
name: novia-declinaison
description: "Déclinaison automatique d'un visuel ou d'une vidéo validés dans les formats natifs des plateformes : 9:16 (1080×1920), 1:1 (1080×1080), 16:9 (1920×1080), 1.91:1 (1200×628) avec ffmpeg, en recadrage centré ou en fond flouté (scripts/declinaison.sh). Auto, après validation de la pièce source."
metadata: {"openclaw": {"emoji": "📐", "requires": {"bins": ["ffmpeg", "ffprobe"]}}}
---

# novia-declinaison — un master, quatre surfaces

## Usage
```bash
bash skills/novia-declinaison/scripts/declinaison.sh outbox/<id>/master.png outbox/<id>/declinaisons
bash skills/novia-declinaison/scripts/declinaison.sh outbox/<id>/master.mp4 outbox/<id>/declinaisons --pad
bash skills/novia-declinaison/scripts/declinaison.sh outbox/<id>/master.png outbox/<id>/declinaisons --only 9x16,1x1
```
- Sans option : recadrage centré (l'image couvre le cadre, on coupe les bords). Bon pour les visuels sans texte près des bords.
- `--pad` : l'image entière est conservée, posée sur un fond flouté de la même image. Bon pour les infographies et les vidéos horizontales à passer en 9:16.
- `--only` : limiter aux formats voulus.
Sorties : `<base>-9x16.<ext>`, `<base>-1x1.<ext>`, `<base>-16x9.<ext>`, `<base>-1.91x1.<ext>` dans le dossier cible. Les vidéos gardent leur piste audio ; H.264 + AAC, compatibles avec toutes les plateformes.

## Règles
- Décliner seulement une pièce validée (Go 1 au moins) ; ne jamais décliner un brouillon.
- Vérifier après coup que le texte reste lisible et dans les zones de sécurité (`rules/production-visuelle.md`) ; si un recadrage coupe du texte, refaire avec `--pad` ou demander un master adapté.
- Ajouter chaque déclinaison au manifest (`assets`, avec le canal cible) et signaler en une ligne dans le groupe.
