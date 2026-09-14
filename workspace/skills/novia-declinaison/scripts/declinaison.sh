#!/usr/bin/env bash
# Décline une image ou une vidéo dans les formats des plateformes.
# Usage : declinaison.sh <fichier> <dossier_sortie> [--pad] [--only 9x16,1x1,16x9,1.91x1]
set -euo pipefail
src="${1:?fichier source}"; out="${2:?dossier de sortie}"; shift 2
MODE="crop"; ONLY="9x16,1x1,16x9,1.91x1"
while [ $# -gt 0 ]; do
  case "$1" in
    --pad) MODE="pad";;
    --only) ONLY="$2"; shift;;
    *) echo "option inconnue : $1" >&2; exit 1;;
  esac; shift
done
command -v ffmpeg >/dev/null || { echo "ffmpeg manquant" >&2; exit 2; }
mkdir -p "$out"
base="$(basename "${src%.*}")"; ext="${src##*.}"; lext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
is_video=0; case "$lext" in mp4|mov|m4v|webm|mkv) is_video=1;; esac
dims() { case "$1" in 9x16) echo "1080 1920";; 1x1) echo "1080 1080";; 16x9) echo "1920 1080";; 1.91x1) echo "1200 628";; *) echo "";; esac; }
IFS=',' read -r -a formats <<< "$ONLY"
for f in "${formats[@]}"; do
  read -r W H <<< "$(dims "$f")"; [ -z "${W:-}" ] && { echo "format inconnu : $f" >&2; continue; }
  if [ "$MODE" = "crop" ]; then
    filter="scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},setsar=1"
  else
    filter="split[a][b];[a]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},boxblur=24:6[bg];[b]scale=${W}:${H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1"
  fi
  if [ "$is_video" = 1 ]; then
    dst="$out/${base}-${f}.mp4"
    ffmpeg -y -loglevel error -i "$src" -filter_complex "$filter" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 160k "$dst"
  else
    case "$lext" in jpg|jpeg) dst="$out/${base}-${f}.jpg";; *) dst="$out/${base}-${f}.png";; esac
    ffmpeg -y -loglevel error -i "$src" -filter_complex "$filter" -frames:v 1 "$dst"
  fi
  echo "→ $dst"
done
