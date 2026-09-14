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
    per_piece = defaultdict(dict)
    for m in recent:
        try:
            per_piece[m[1]][m[3]] = float(str(m[4]).replace(",", "."))
        except ValueError:
            continue
    print("📈 Bilan des %d derniers jours" % args.days)
    print("Publications : %d" % len(published))
    for l in published[:10]:
        print("  - " + l)
    if per_piece:
        score = {pid: sum(v for k, v in vals.items() if k in ("reach", "impressions", "vues", "views", "engagement", "clics", "clicks")) for pid, vals in per_piece.items()}
        best = max(score, key=score.get)
        worst = min(score, key=score.get)
        print("Meilleure pièce (somme des métriques disponibles) : %s (%s)" % (best, ", ".join("%s=%g" % kv for kv in per_piece[best].items())))
        if worst != best:
            print("Plus faible : %s (%s)" % (worst, ", ".join("%s=%g" % kv for kv in per_piece[worst].items())))
    missing = [l.split(" · ")[1] for l in published if l.split(" · ")[1] not in per_piece]
    if missing:
        print("Sans métriques encore : " + ", ".join(sorted(set(missing))))
    n = len(published)
    if n < 6:
        print("Pas assez d'observations (%d < 6) pour conclure sur un format." % n)


if __name__ == "__main__":
    main()
