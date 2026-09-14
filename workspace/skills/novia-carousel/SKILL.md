---
name: novia-carousel
description: "Carrousel pédagogique IMMO9 pour LinkedIn (PDF) et Instagram (images 1080×1350) : plan slide par slide, construction HTML à la charte depuis un JSON (scripts/carousel_build.py), rendu PNG et PDF par navigateur headless (scripts/render_html.sh) ou par l'outil browser d'OpenClaw. Semi-auto, hebdomadaire."
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"bins": ["python3"]}}}
---

# novia-carousel : cinq à huit slides qui font garder un repère

## Procédure
1. Sujet ancré (veille, question client, calendrier) et persona unique. Vérifier `learning/THEMES_COVERED.md`.
2. Plan : slide 1 = promesse autonome (titre + sous-titre, se comprend seule dans le feed) ; slides 2 à 7 = une idée chacune (titre court, 2 à 4 lignes, chiffre sourcé si utile) ; dernière slide = repère à garder ou question sincère, logo, source principale. Jamais d'appel à l'action creux.
3. Écrire le JSON `outbox/<id>/carousel.json` (structure ci-dessous).
4. `python3 skills/novia-carousel/scripts/carousel_build.py outbox/<id>/carousel.json` → `outbox/<id>/carousel.html` et `outbox/<id>/slides/slide-01.html` … (tokens de `templates/_tokens.json`).
5. Rendu : `bash skills/novia-carousel/scripts/render_html.sh outbox/<id>/slides 1080 1350` → PNG par slide + `carousel.pdf`. Sans navigateur sur le serveur : ouvrir chaque slide avec l'outil `browser` d'OpenClaw et prendre une capture 1080 × 1350, ou demander à Julien d'installer Chromium (voir `docs/INSTALLATION.md`).
6. Contrôle visuel (`rules/production-visuelle.md`) : lisibilité téléphone, sources sur les slides chiffrées, logo, orthographe.
7. Légende du canal primaire avec `novia-editorial` puis `caption_check.py`. Manifest : assets = PNG (Instagram) et PDF (LinkedIn), `channels` par asset.
8. Présentation en une carte ; « Go publie » ; `novia-publish`.

## Structure du JSON
```json
{
  "id": "nc-20260914-02",
  "persona": "P1",
  "kicker": "Primo-accédants",
  "slides": [
    {"title": "Le prêt à taux zéro en 2026, en 5 questions", "body": "Ce qui change, pour qui, et combien.", "cover": true},
    {"title": "1. Qui peut en bénéficier ?", "body": "…", "source": "service-public.fr, 12/09/2026"},
    {"title": "À garder", "body": "…", "last": true}
  ],
  "footer": {"source": "Sources : service-public.fr, ANIL (septembre 2026)", "brand": "IMMO9"}
}
```

## Règles
- 5 à 8 slides, 1080 × 1350, marges 8 %, texte de corps ≥ 40 px, titres ≥ 64 px.
- Un chiffre par slide au maximum, toujours avec sa source sur la slide.
- Pas de tableau, pas de liste de plus de trois points par slide.
- Le PDF LinkedIn et les images Instagram viennent du même HTML : une seule vérité.
