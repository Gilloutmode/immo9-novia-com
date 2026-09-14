#!/usr/bin/env python3
"""Marque une pièce comme présentée à l'équipe (ouvre la fenêtre d'approbation)."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from novia_common import find_workspace, load_manifest, write_json, now_iso, add_history, append_line  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piece_id")
    ap.add_argument("--stage", choices=["go1", "final"], default="final",
                    help="go1 = présentation du concept ; final = package final (défaut)")
    ap.add_argument("--score", type=int, default=None, help="score qualité narrative (0-100)")
    args = ap.parse_args()
    ws = find_workspace()
    path, m = load_manifest(ws, args.piece_id)
    if m["status"] in ("published", "rejected", "expired"):
        sys.exit("pièce %s en statut %s : ne peut plus être présentée" % (m["id"], m["status"]))
    if args.score is not None:
        m["quality"]["narrative_score"] = args.score
    m["status"] = "presented" if args.stage == "go1" else "final_presented"
    m["presented_at"] = now_iso()
    add_history(m, "presented_%s" % args.stage, by="agent")
    write_json(path, m)
    append_line(ws / "learning" / "CONTENT_LEDGER.md",
                "- %s · %s · %s · %s · %s · présentée (%s)" % (now_iso()[:10], m["id"], m["format"], m["persona"], m["channel_primary"], args.stage))
    print("%s présentée (%s) à %s" % (m["id"], args.stage, m["presented_at"]))


if __name__ == "__main__":
    main()
