#!/usr/bin/env python3
"""Ferme ou met en attente une pièce, avec trace dans le ledger et le fichier de goût."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from novia_common import find_workspace, load_manifest, write_json, now_iso, add_history, append_line  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piece_id")
    ap.add_argument("--status", required=True, choices=["rejected", "parked", "expired", "draft"])
    ap.add_argument("--note", default="")
    ap.add_argument("--by", default="agent")
    args = ap.parse_args()
    ws = find_workspace()
    path, m = load_manifest(ws, args.piece_id)
    if m["status"] == "published":
        sys.exit("pièce publiée : statut figé")
    m["status"] = args.status
    add_history(m, "status_%s" % args.status, by=args.by, note=args.note)
    write_json(path, m)
    append_line(ws / "learning" / "CONTENT_LEDGER.md",
                "- %s · %s · %s · %s · %s · %s%s" % (now_iso()[:10], m["id"], m["format"], m["persona"], m["channel_primary"], args.status, (" · " + args.note) if args.note else ""))
    if args.status == "rejected":
        append_line(ws / "learning" / "TASTE.md",
                    "- %s · %s (%s, %s) · refus%s" % (now_iso()[:10], m["id"], m["format"], m["title"], (" : " + args.note) if args.note else " sans motif donné"))
    print("%s → %s" % (m["id"], args.status))


if __name__ == "__main__":
    main()
