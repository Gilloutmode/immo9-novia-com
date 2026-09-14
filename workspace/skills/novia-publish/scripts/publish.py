#!/usr/bin/env python3
"""Publie une pièce approuvée via l'adaptateur configuré. Refuse sans approbation go2."""
import argparse
import importlib.util
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "novia-outbox" / "scripts"))
from novia_common import find_workspace, load_manifest, write_json, now_iso, add_history, read_json, append_line, load_contract  # noqa: E402


def load_adapter(name):
    path = HERE.parent / "adapters" / ("%s.py" % name)
    if not path.exists():
        sys.exit("adaptateur inconnu : %s (fichier %s absent)" % (name, path))
    spec = importlib.util.spec_from_file_location("adapter_%s" % name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "publish"):
        sys.exit("adaptateur %s sans fonction publish()" % name)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piece_id")
    ap.add_argument("--channel", action="append", default=[], help="canal à publier (défaut : canal primaire)")
    ap.add_argument("--dry-run", action="store_true", help="simulation, aucun appel externe")
    args = ap.parse_args()

    ws = find_workspace()
    contract = load_contract(ws)
    path, m = load_manifest(ws, args.piece_id)

    if m["status"] != "approved" or not m["approvals"].get("go2"):
        sys.exit("REFUS : pièce %s sans « Go publie » enregistré (statut %s)." % (m["id"], m["status"]))
    go2 = m["approvals"]["go2"]
    approvers = read_json(ws / "state" / "approvers.json", {"approvers": []}).get("approvers", [])
    if not any(str(a.get("telegram_id")) == str(go2.get("by")) for a in approvers):
        sys.exit("REFUS : l'auteur du Go publie n'est plus dans state/approvers.json.")
    ttl = timedelta(hours=float(contract.get("validation", {}).get("approval_ttl_hours", 24)))
    at = datetime.fromisoformat(go2["at"])
    if datetime.now(at.tzinfo) - at > ttl:
        sys.exit("REFUS : « Go publie » trop ancien (> %s h) ; re-présenter la pièce." % contract.get("validation", {}).get("approval_ttl_hours", 24))

    channels_cfg = read_json(ws / "state" / "channels.json", {"channels": {}}).get("channels", {})
    targets = args.channel or [m["channel_primary"]]
    results = []
    for ch in targets:
        cfg = dict(channels_cfg.get(ch, {}))
        adapter_name = "dryrun" if args.dry_run else cfg.get("adapter")
        if not adapter_name:
            sys.exit("REFUS : aucun adaptateur configuré pour le canal « %s » dans state/channels.json." % ch)
        caption = m["captions"].get(ch) or m["captions"].get("default") or ""
        assets = [ws / "outbox" / m["id"] / a["file"] for a in m.get("assets", []) if not a.get("channels") or ch in a["channels"]]
        missing = [str(a) for a in assets if not a.exists()]
        if missing:
            sys.exit("REFUS : fichiers manquants : %s" % ", ".join(missing))
        mod = load_adapter(adapter_name)
        try:
            res = mod.publish(channel=ch, settings=cfg, caption=caption, assets=[str(a) for a in assets], manifest=m)
        except Exception as e:  # l'erreur est rapportée telle quelle, sans repli silencieux
            add_history(m, "publish_failed", by="agent", note="%s: %s" % (ch, e))
            write_json(path, m)
            sys.exit("ÉCHEC publication %s via %s : %s" % (ch, adapter_name, e))
        res = dict(res or {})
        res.update({"channel": ch, "adapter": adapter_name, "at": now_iso()})
        results.append(res)
        m["publication"]["results"].append(res)

    if not args.dry_run:
        m["status"] = "published"
        add_history(m, "published", by=str(go2.get("by")))
        write_json(path, m)
        for r in results:
            append_line(ws / "learning" / "CONTENT_LEDGER.md",
                        "- %s · %s · %s · %s · %s · publiée · %s" % (now_iso()[:10], m["id"], m["format"], m["persona"], r["channel"], r.get("url") or r.get("id") or ""))
            append_line(ws / "learning" / "FEED_STATE.md",
                        "- %s · %s · %s · %s · %s" % (now_iso()[:10], r["channel"], m["format"], m["title"], r.get("url") or ""))
    else:
        add_history(m, "publish_dry_run", by="agent")
        write_json(path, m)
    for r in results:
        print("%s via %s : %s" % (r["channel"], r["adapter"], r.get("url") or r.get("id") or r.get("message", "ok")))


if __name__ == "__main__":
    main()
