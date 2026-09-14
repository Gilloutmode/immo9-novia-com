#!/usr/bin/env python3
"""Lit, avance et vérifie l'état d'onboarding (verrou de production)."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, read_json, write_json, now_iso, load_contract  # noqa: E402


def checks(ws):
    out = []
    approvers = read_json(ws / "state" / "approvers.json", {}).get("approvers", [])
    out.append((bool(approvers), "state/approvers.json : au moins une personne autorisée (%d)" % len(approvers)))
    ch = read_json(ws / "state" / "channels.json", {})
    out.append((bool(ch.get("telegram_group_id")), "state/channels.json : telegram_group_id renseigné"))
    tokens = read_json(ws / "templates" / "_tokens.json", {}) or {}
    out.append((bool(tokens.get("color_primary")) and bool(tokens.get("font_title")), "templates/_tokens.json : couleur primaire et police de titre"))
    voice = (ws / "doctrine" / "VOICE.md").read_text(encoding="utf-8")
    out.append(("[À REMPLIR — acte 2]" not in voice.split("## Lexique")[0], "doctrine/VOICE.md : corpus, rythme, ouvertures, finitions remplis"))
    lines = (ws / "doctrine" / "LINES.md").read_text(encoding="utf-8")
    out.append(("[À REMPLIR — acte 3, avec David" not in lines, "doctrine/LINES.md : section « Jamais public (propre à IMMO9) » remplie"))
    team = (ws / "TEAM.md").read_text(encoding="utf-8")
    out.append((len(re.findall(r"\[À REMPLIR\]", team)) <= 1, "TEAM.md : identifiants Telegram renseignés"))
    taste = ws / "learning" / "TASTE.md"
    out.append((taste.exists() and len([l for l in taste.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]) >= 3, "learning/TASTE.md : au moins trois retours consignés (acte 2 et 4)"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="set_status", default=None)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    ws = find_workspace()
    contract = load_contract(ws)
    acts = contract.get("onboarding", {}).get("acts", [])
    path = ws / "state" / "onboarding.json"
    state = read_json(path, {"status": acts[0] if acts else "act0_diagnostic", "history": []})
    if args.check or args.set_status == "complete":
        results = checks(ws)
        for ok, label in results:
            print(("✓ " if ok else "✗ ") + label)
        if args.set_status == "complete" and not all(ok for ok, _ in results):
            sys.exit("REFUS : conditions manquantes, l'onboarding reste en %s" % state["status"])
        if args.check and not args.set_status:
            print("statut actuel : %s" % state["status"])
            return
    if args.set_status:
        if args.set_status not in acts:
            sys.exit("statut inconnu : %s (attendus : %s)" % (args.set_status, ", ".join(acts)))
        cur, new = acts.index(state["status"]), acts.index(args.set_status)
        if new not in (cur, cur + 1) and args.set_status != "complete":
            sys.exit("REFUS : passage de %s à %s non séquentiel" % (state["status"], args.set_status))
        state.setdefault("history", []).append({"at": now_iso(), "from": state["status"], "to": args.set_status})
        state["status"] = args.set_status
        state["updated_at"] = now_iso()
        write_json(path, state)
        print("onboarding : %s" % state["status"])
        return
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
