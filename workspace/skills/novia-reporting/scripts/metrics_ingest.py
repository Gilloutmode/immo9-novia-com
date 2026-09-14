#!/usr/bin/env python3
"""Ingère un CSV de métriques (date,piece_id,channel,metric,value,source) dans learning/METRICS.md sans doublon."""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, append_line  # noqa: E402

REQUIRED = ["date", "piece_id", "channel", "metric", "value", "source"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_file")
    args = ap.parse_args()
    ws = find_workspace()
    path = Path(args.csv_file)
    metrics_md = ws / "learning" / "METRICS.md"
    existing = set()
    if metrics_md.exists():
        for line in metrics_md.read_text(encoding="utf-8").splitlines():
            if line.startswith("- "):
                cells = [c.strip() for c in line[2:].split(" · ")]
                if len(cells) >= 4:
                    existing.add(tuple(cells[:4]))
    added, skipped = 0, 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit("colonnes manquantes : %s" % ", ".join(missing))
        for row in reader:
            key = (row["date"].strip(), row["piece_id"].strip(), row["channel"].strip(), row["metric"].strip())
            if key in existing or not row["value"].strip():
                skipped += 1
                continue
            append_line(metrics_md, "- %s · %s · %s · %s · %s · %s" % (key + (row["value"].strip(), row["source"].strip())))
            existing.add(key)
            added += 1
    done = path.with_suffix(path.suffix + ".ingested")
    path.rename(done)
    print("%d lignes ajoutées, %d ignorées (doublons ou vides) → %s" % (added, skipped, done.name))


if __name__ == "__main__":
    main()
