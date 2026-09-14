#!/usr/bin/env bash
# Audiogram : extrait audio + couverture + forme d'onde + titre, en 1:1 et 9:16.
# Usage : audiogram.sh <audio> <cover.png> "<titre>" <dossier_sortie> [--start HH:MM:SS] [--duration S] [--font /chemin/police.ttf]
set -euo pipefail
audio="${1:?audio}"; cover="${2:?couverture}"; title="${3:?titre}"; out="${4:?dossier de sortie}"; shift 4
START="0"; DUR="45"; FONT="${AUDIOGRAM_FONT:-}"
while [ $# -gt 0 ]; do case "$1" in --start) START="$2"; shift;; --duration) DUR="$2"; shift;; --font) FONT="$2"; shift;; *) echo "option inconnue $1" >&2; exit 1;; esac; shift; done
command -v ffmpeg >/dev/null || { echo "ffmpeg manquant" >&2; exit 2; }
mkdir -p "$out"
if [ -z "$FONT" ]; then
  for f in "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" "/System/Library/Fonts/Supplemental/Arial Bold.ttf" "/Library/Fonts/Arial Bold.ttf"; do [ -f "$f" ] && { FONT="$f"; break; }; done
fi
safe_title="$(printf '%s' "$title" | sed "s/'/’/g; s/:/\\\\:/g")"
HAS_DRAWTEXT=0; ffmpeg -hide_banner -filters 2>/dev/null | grep -q "drawtext" && HAS_DRAWTEXT=1
if [ "$HAS_DRAWTEXT" != 1 ]; then echo "note : ce ffmpeg n'a pas le filtre drawtext (libfreetype) ; audiograms rendus sans titre incrusté" >&2; FONT=""; fi
render() { # W H name
  local W="$1" H="$2" name="$3"
  local wave_h=$(( H / 6 )) img_h=$(( H * 55 / 100 ))
  local text_filter=""
  if [ -n "$FONT" ]; then text_filter=",drawtext=fontfile='${FONT}':text='${safe_title}':fontcolor=white:fontsize=$(( W / 18 )):x=(w-text_w)/2:y=h-${wave_h}-$(( H / 10 )):shadowcolor=black@0.6:shadowx=2:shadowy=2"; fi
  ffmpeg -y -loglevel error -ss "$START" -t "$DUR" -i "$audio" -loop 1 -i "$cover" -filter_complex \
    "[1:v]scale=${W}:${img_h}:force_original_aspect_ratio=increase,crop=${W}:${img_h},pad=${W}:${H}:0:0:color=#1F3A5F[bg];\
     [0:a]showwaves=s=${W}x${wave_h}:mode=cline:colors=white@0.9:rate=25[w];\
     [bg][w]overlay=0:${H}-${wave_h}-$(( H / 25 ))${text_filter},format=yuv420p[v]" \
    -map "[v]" -map 0:a -t "$DUR" -r 25 -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k -movflags +faststart -shortest "$out/audiogram-${name}.mp4"
  echo "→ $out/audiogram-${name}.mp4"
}
render 1080 1080 1x1
render 1080 1920 9x16
[ -z "$FONT" ] && echo "note : aucune police trouvée, audiograms rendus sans titre (option --font)" >&2 || true
