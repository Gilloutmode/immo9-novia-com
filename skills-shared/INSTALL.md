# Skills partagés : ce qui est livré ici, ce qui s'installe depuis sa source publique

Les dossiers de ce répertoire sont installés pour tous les agents par `scripts/install.sh` (`openclaw skills install <dossier> --global`). Les autres skills utiles à Novia Com se prennent à leur source publique, pour rester à jour et ne pas figer du code tiers dans ce dépôt.

## Livrés dans ce dossier (relus et nettoyés pour Linux, sans chemin personnel)
| Skill | Usage pour Novia Com | Dépendances |
|---|---|---|
| `html-email` | règles de mise en forme d'un email HTML lisible partout (utilisées par novia-newsletter) | aucune |
| `marketing-intelligence` | repères de création de contenu social (synthèse de recherches) | aucune |
| `social-media-growth-2026` | stratégie de croissance TikTok et Instagram, orientée immobilier | aucune |
| `elevenlabs-soundfx` | effets sonores pour les vidéos et audiograms | compte ElevenLabs (`ELEVENLABS_API_KEY`) |
| `sound-integration` | intégration sonore (timing, mixage) | ffmpeg |
| `reddit-search` | recherche Reddit par l'API publique | `npm ci` dans le dossier du skill (node) |
| `nano-banana-pro` | génération et retouche d'images via Gemini (alternative à l'outil image d'OpenClaw) | `uv`, `GEMINI_API_KEY` |
| `supermonteur` | rush parlé vers vidéo 9:16 sous-titrée mot à mot | ffmpeg, node (`npx hyperframes@0.6.81`), `ELEVENLABS_API_KEY` (transcription Scribe), police Montserrat |

## À installer depuis leur source publique
```bash
# HyperFrames (compositions vidéo HTML) : installe les 4 skills hyperframes* dans le workspace
cd <workspace> && npx hyperframes@0.6.81 init hyperframes
# Recherche sociale sur 30 jours (Reddit, X, YouTube, TikTok…), MIT
openclaw skills install git:https://github.com/mvanhorn/last30days-skill --global
# Diagrammes (Kroki, sans installation locale)
openclaw skills install git:https://github.com/Agents365-ai/creating-mermaid-diagrams --global
# Depuis ClawHub (vérifier l'auteur avec `openclaw skills search <slug>` puis `openclaw skills verify`)
openclaw skills search video ; openclaw skills search content-marketing ; openclaw skills search content-ideas ; openclaw skills search instagram
```
Avant d'installer un skill tiers : `openclaw skills verify @owner/slug`, lecture du `SKILL.md` et des scripts, puis test sur une pièce. Un skill non relu n'entre pas en production (docs/SECURITE.md).

## Non retenus (et pourquoi)
- `deep-search` (recherche multi-moteurs) : puissant mais lié à une machine précise et à une dizaine de clés payantes ; proposé en option au palier 2 (docs/ROADMAP.md).
- `seedance-video`, `veo` : vidéo générative payante, hors besoin immédiat ; utilisables plus tard pour des ambiances abstraites uniquement.
- `wacli`, `voice-tts`, `telegram-send`, `reel` : spécifiques à un autre environnement (macOS, autre agent).
