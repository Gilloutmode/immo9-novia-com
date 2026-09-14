#!/usr/bin/env bash
# Rend des fichiers HTML en PNG (et un PDF global) avec un navigateur Chromium headless.
# Usage : render_html.sh <dossier_ou_fichier.html> [largeur] [hauteur]
set -euo pipefail
target="${1:?dossier ou fichier HTML}"; W="${2:-1080}"; H="${3:-1350}"
find_browser() {
  for b in chromium chromium-browser google-chrome google-chrome-stable chrome; do
    command -v "$b" >/dev/null 2>&1 && { echo "$b"; return; }
  done
  for p in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
    [ -x "$p" ] && { echo "$p"; return; }
  done
  return 1
}
BROWSER="$(find_browser || true)"
if [ -z "$BROWSER" ]; then
  echo "Aucun navigateur Chromium trouvé. Options : installer chromium (apt install chromium) ou utiliser l'outil browser d'OpenClaw pour capturer chaque slide en ${W}x${H}." >&2
  exit 2
fi
if [ -d "$target" ]; then files=("$target"/*.html); outdir="$target"; else files=("$target"); outdir="$(dirname "$target")"; fi
for f in "${files[@]}"; do
  abs_dir="$(cd "$(dirname "$f")" && pwd)"; out="$abs_dir/$(basename "${f%.html}").png"
  "$BROWSER" --headless=new --disable-gpu --hide-scrollbars --no-sandbox --force-device-scale-factor=1 \
    --window-size="${W},${H}" --screenshot="$out" "file://$abs_dir/$(basename "$f")" >/dev/null 2>&1
  echo "→ $out"
done
if [ -d "$target" ] && [ -f "$outdir/../carousel.html" ]; then
  parent="$(cd "$outdir/.." && pwd)"; pdf="$parent/carousel.pdf"
  "$BROWSER" --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf="$pdf" \
    "file://$parent/carousel.html" >/dev/null 2>&1 && echo "→ $pdf"
fi
