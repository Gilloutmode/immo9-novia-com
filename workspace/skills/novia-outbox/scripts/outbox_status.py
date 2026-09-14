#!/usr/bin/env python3
"""Liste les pièces de l'outbox, avec passage automatique en expired des présentations trop anciennes (--expire)."""
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from novia_common import find_workspace, read_json, write_json, now_iso, add_history, append_line, load_contract  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default=None, help="filtrer sur un statut")
    ap.add_argument("--expire", action="store_true", help="passer en expired les pièces présentées depuis trop longtemps")
    args = ap.parse_args()
    ws = find_workspace()
    days = load_contract(ws).get("validation", {}).get("presented_expiry_days", 7)
    rows = []
    for d in sorted((ws / "outbox").glob("nc-*")):
        m = read_json(d / "manifest.json")
        if not m:
            continue
        if args.expire and m["status"] in ("presented", "go1", "final_presented") and m.get("presented_at"):
            presented = datetime.fromisoformat(m["presented_at"])
            if datetime.now(presented.tzinfo) - presented > timedelta(days=days):
                m["status"] = "expired"
                add_history(m, "status_expired", by="cron-sante", note="présentée depuis plus de %d jours" % days)
                write_json(d / "manifest.json", m)
                append_line(ws / "learning" / "CONTENT_LEDGER.md", "- %s · %s · expirée sans réponse" % (now_iso()[:10], m["id"]))
        if args.status and m["status"] != args.status:
            continue
        rows.append("%s  %-16s %s %s %-10s %s" % (m["id"], m["status"], m["format"], m["persona"], m["channel_primary"], m["title"]))
    print("\n".join(rows) if rows else "outbox vide")


if __name__ == "__main__":
    main()
