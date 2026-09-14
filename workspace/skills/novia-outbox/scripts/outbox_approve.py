#!/usr/bin/env python3
"""Enregistre une approbation Go 1 ou Go 2 après vérification de l'auteur, du texte et du délai."""
import argparse
import sys
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from novia_common import find_workspace, load_manifest, write_json, now_iso, add_history, read_json, load_contract  # noqa: E402


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(s.lower().split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piece_id")
    ap.add_argument("--stage", required=True, choices=["go1", "go2"])
    ap.add_argument("--by", required=True, help="identifiant Telegram de l'auteur du message")
    ap.add_argument("--text", required=True, help="texte exact du message")
    ap.add_argument("--reply-to-card", action="store_true", default=True,
                    help="le message répond à la carte de la pièce (obligatoire)")
    args = ap.parse_args()

    ws = find_workspace()
    contract = load_contract(ws)
    val = contract.get("validation", {})
    approvers = read_json(ws / "state" / "approvers.json", {"approvers": []}).get("approvers", [])
    who = next((a for a in approvers if str(a.get("telegram_id")) == str(args.by)), None)
    if who is None:
        sys.exit("REFUS : %s n'est pas dans state/approvers.json. Remercier, ne rien enregistrer." % args.by)

    path, m = load_manifest(ws, args.piece_id)
    text = norm(args.text)
    if len(text) > 300:
        sys.exit("REFUS : message trop long pour valoir approbation (>300 caractères).")
    if "?" in args.text:
        sys.exit("REFUS : le message est une question, pas une approbation.")
    negations = ("ne ", "n'", "pas", "non", "rien", "jamais", "sauf", "stop", "attend", "plus tard", "pas encore", "annule", "surtout pas")
    if any((" " + n) in (" " + text + " ") or text.startswith(n) for n in negations):
        sys.exit("REFUS : le message contient une négation ou une réserve ; demander une réponse claire.")
    words = [norm(w) for w in val.get("go2_words" if args.stage == "go2" else "go1_words", [])]
    if args.stage == "go1":
        words += [norm(w) for w in val.get("go2_words", [])]  # un « Go publie » vaut aussi Go 1
    never = [norm(w) for w in val.get("never_approval", [])]
    if text in never:
        sys.exit("REFUS : « %s » ne vaut jamais approbation." % args.text)
    lead = text.lstrip("!.:,;- ")
    if not any(lead == w or lead.startswith(w + " ") or lead.startswith(w + ",") or lead.startswith(w + ".") or lead.startswith(w + "!") for w in sorted(words, key=len, reverse=True)):
        sys.exit("REFUS : le message doit commencer par une formule d'approbation (%s) ; ici : « %s »." % (", ".join(words), args.text))
    if not m.get("presented_at"):
        sys.exit("REFUS : la pièce n'a pas été présentée (outbox_present.py).")
    ttl = timedelta(hours=float(val.get("approval_ttl_hours", 24)))
    presented = datetime.fromisoformat(m["presented_at"])
    if datetime.now(presented.tzinfo) - presented > ttl:
        sys.exit("REFUS : présentation trop ancienne (> %s h) ; re-présenter la pièce." % val.get("approval_ttl_hours", 24))
    if args.stage == "go2" and m["status"] not in ("presented", "go1", "final_presented"):
        sys.exit("REFUS : statut %s incompatible avec Go 2." % m["status"])
    if args.stage == "go1" and m["status"] not in ("presented", "final_presented"):
        sys.exit("REFUS : statut %s incompatible avec Go 1." % m["status"])

    record = {"by": str(args.by), "name": who.get("name"), "at": now_iso(), "text": args.text}
    m["approvals"][args.stage] = record
    m["status"] = "go1" if args.stage == "go1" else "approved"
    add_history(m, "approved_%s" % args.stage, by=str(args.by), note=args.text)
    write_json(path, m)
    print("OK : %s → %s par %s (%s)" % (m["id"], m["status"], who.get("name"), record["at"]))


if __name__ == "__main__":
    main()
