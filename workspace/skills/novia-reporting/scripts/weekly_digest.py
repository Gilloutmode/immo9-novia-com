#!/usr/bin/env python3
"""Rapport des publications et métriques sur N jours, à partir du ledger et de METRICS.md."""
import argparse
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace  # noqa: E402


def read_lines(path):
    if not path.exists():
        return []
    return [l[2:] for l in path.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()
    ws = find_workspace()
    since = (date.today() - timedelta(days=args.days)).isoformat()
    published = [l for l in read_lines(ws / "learning" / "CONTENT_LEDGER.md") if "publiée" in l and l[:10] >= since]
    metrics = [l.split(" · ") for l in read_lines(ws / "learning" / "METRICS.md")]
    recent = [m for m in metrics if len(m) >= 5 and m[0] >= since]
    if not published and not recent:
        print("NO_REPLY")
        return
    per_piece = defaultdict(dict)  # clé : (pièce, canal) → {métrique: valeur}
    for m in recent:
        try:
            per_piece[(m[1], m[2])][m[3]] = float(str(m[4]).replace(",", "."))
        except ValueError:
            continue
    print("📈 Bilan des %d derniers jours" % args.days)
    print("Publications : %d" % len(published))
    for l in published[:10]:
        print("  - " + l)
    if per_piece:
        for metric in ("reach", "impressions", "vues", "views", "engagement", "clics", "clicks"):
            rows = [(k, v[metric]) for k, v in per_piece.items() if metric in v]
            if len(rows) >= 2:
                rows.sort(key=lambda kv: kv[1], reverse=True)
                print("%s : meilleure %s/%s (%g), plus faible %s/%s (%g), sur %d observations" % (metric, rows[0][0][0], rows[0][0][1], rows[0][1], rows[-1][0][0], rows[-1][0][1], rows[-1][1], len(rows)))
    published_pairs = []
    for l in published:
        cells = [c.strip() for c in l.split(" · ")]
        if len(cells) >= 5:
            published_pairs.append((cells[1], cells[4]))
    missing = ["%s/%s" % pc for pc in published_pairs if pc not in per_piece]
    if missing:
        print("Sans métriques encore : " + ", ".join(sorted(set(missing))))
    n = len(published)
    if n < 6:
        print("Pas assez d'observations (%d < 6) pour conclure sur un format." % n)


if __name__ == "__main__":
    main()
