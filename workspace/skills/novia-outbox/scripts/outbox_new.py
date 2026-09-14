#!/usr/bin/env python3
"""Crée une pièce dans outbox/ avec son manifest."""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from novia_common import find_workspace, now_iso, write_json, load_contract  # noqa: E402

FORMATS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]
PERSONAS = ["P1", "P2", "P3", "P4"]
CHANNELS = ["linkedin", "instagram", "facebook", "youtube", "tiktok", "newsletter", "site", "autre"]


def next_id(ws):
    today = date.today().strftime("%Y%m%d")
    prefix = "nc-%s-" % today
    n = 0
    for d in (ws / "outbox").glob(prefix + "*"):
        m = re.match(r"nc-\d{8}-(\d{2,})$", d.name)
        if m:
            n = max(n, int(m.group(1)))
    return "%s%02d" % (prefix, n + 1)


def main():
    ap = argparse.ArgumentParser(description="Crée une pièce Novia Com")
    ap.add_argument("--format", required=True, choices=FORMATS)
    ap.add_argument("--persona", required=True, choices=PERSONAS)
    ap.add_argument("--channel", required=True, choices=CHANNELS, help="canal primaire")
    ap.add_argument("--title", required=True)
    ap.add_argument("--source", action="append", default=[], help="URL ou document source (répétable)")
    ap.add_argument("--ancrage", default="", help="veille du <date> | question client | calendrier | programme")
    ap.add_argument("--cost", type=float, default=0.0, help="coût probable en euros")
    ap.add_argument("--ceiling", type=float, default=None, help="plafond en euros (défaut : contrat)")
    args = ap.parse_args()

    ws = find_workspace()
    contract = load_contract(ws)
    ceiling = args.ceiling if args.ceiling is not None else contract.get("budget", {}).get("default_ceiling_per_piece", 2.0)
    if args.cost > ceiling:
        sys.exit("coût probable (%.2f) supérieur au plafond (%.2f) : présenter un devis dédié" % (args.cost, ceiling))
    pid = next_id(ws)
    piece_dir = ws / "outbox" / pid
    piece_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "id": pid,
        "created_at": now_iso(),
        "format": args.format,
        "persona": args.persona,
        "channel_primary": args.channel,
        "channels": [args.channel],
        "title": args.title,
        "ancrage": args.ancrage,
        "sources": args.source,
        "status": "draft",
        "presented_at": None,
        "cost": {"currency": "EUR", "estimated": args.cost, "ceiling": ceiling, "actual": None},
        "assets": [],
        "captions": {},
        "quality": {"narrative_score": None, "compliance_checked": False},
        "approvals": {"go1": None, "go2": None},
        "publication": {"targets": [], "results": []},
        "history": [{"at": now_iso(), "event": "created", "by": "agent", "note": None}],
    }
    write_json(piece_dir / "manifest.json", manifest)
    print(pid)


if __name__ == "__main__":
    main()
