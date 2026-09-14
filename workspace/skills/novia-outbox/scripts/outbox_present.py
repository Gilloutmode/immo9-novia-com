#!/usr/bin/env python3
"""Marque une pièce comme présentée à l'équipe (ouvre la fenêtre d'approbation)."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from novia_common import find_workspace, load_manifest, write_json, now_iso, add_history, append_line, package_fingerprint, onboarding_status, onboarding_rank, load_contract, missing_assets  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piece_id")
    ap.add_argument("--stage", choices=["go1", "final"], default="final",
                    help="go1 = présentation du concept ; final = package final (défaut)")
    ap.add_argument("--score", type=int, default=None, help="score qualité narrative (0-100)")
    ap.add_argument("--card-id", default=None, help="identifiant du message Telegram de la carte (à renseigner après envoi, avec --card-chat-id)")
    ap.add_argument("--card-chat-id", default=None, help="identifiant du chat Telegram où la carte a été envoyée")
    ap.add_argument("--card-only", action="store_true", help="n'enregistre que la carte d'une présentation déjà faite (pas de nouvelle présentation)")
    ap.add_argument("--test", action="store_true", help="pièce test de calibration (acte 4) : présentable, jamais publiable")
    args = ap.parse_args()
    ws = find_workspace()
    path, m = load_manifest(ws, args.piece_id)
    contract = load_contract(ws)
    allowed_from = contract.get("onboarding", {}).get("production_allowed_from", "act4_calibration")
    if onboarding_rank(ws) < onboarding_rank(ws, allowed_from):
        sys.exit("REFUS : onboarding en %s ; aucune pièce n'est présentable avant %s." % (onboarding_status(ws), allowed_from))
    if args.stage == "final":
        if m["quality"].get("narrative_score") is None and args.score is None:
            sys.exit("REFUS : score qualité narrative absent (--score) ; voir doctrine/NARRATIVE_QUALITY.md.")
        score = args.score if args.score is not None else m["quality"]["narrative_score"]
        if score < contract.get("quality", {}).get("narrative_minimum_score", 85):
            sys.exit("REFUS : score %d < minimum %d." % (score, contract.get("quality", {}).get("narrative_minimum_score", 85)))
        if not m["quality"].get("compliance_checked"):
            sys.exit("REFUS : contrôle de conformité non consigné (quality.compliance_checked) ; voir rules/conformite-immobilier.md.")
        if not m.get("captions"):
            sys.exit("REFUS : aucune légende dans le manifest ; le package final doit être complet.")
        miss = missing_assets(ws, m)
        if miss:
            sys.exit("REFUS : fichiers déclarés mais absents : %s" % ", ".join(miss))
    if m["status"] in ("published", "rejected", "expired"):
        sys.exit("pièce %s en statut %s : ne peut plus être présentée" % (m["id"], m["status"]))
    if args.card_only:
        if not (args.card_id and args.card_chat_id):
            sys.exit("REFUS : --card-only exige --card-id et --card-chat-id.")
        if m["status"] not in ("presented", "final_presented"):
            sys.exit("REFUS : aucune présentation en cours (statut %s)." % m["status"])
        m["card_message_id"] = str(args.card_id)
        m["card_chat_id"] = str(args.card_chat_id)
        add_history(m, "card_recorded", by="agent", note="%s/%s" % (args.card_chat_id, args.card_id))
        write_json(path, m)
        print("%s : carte %s enregistrée dans le chat %s" % (m["id"], args.card_id, args.card_chat_id))
        return
    if args.score is not None:
        m["quality"]["narrative_score"] = args.score
    m["status"] = "presented" if args.stage == "go1" else "final_presented"
    m["presented_at"] = now_iso()
    m["is_test"] = bool(args.test) or bool(m.get("is_test"))
    # nouvelle présentation : l'ancienne carte et les approbations antérieures ne valent plus
    m["card_message_id"] = str(args.card_id) if args.card_id else None
    m["card_chat_id"] = str(args.card_chat_id) if args.card_chat_id else None
    if args.card_id and not args.card_chat_id:
        sys.exit("REFUS : --card-id exige --card-chat-id (les identifiants de message Telegram sont propres à un chat).")
    m["approvals"] = {"go1": None, "go2": None}
    if args.stage == "final":
        m["package_fingerprint"] = package_fingerprint(ws, m)
    add_history(m, "presented_%s" % args.stage, by="agent")
    write_json(path, m)
    append_line(ws / "learning" / "CONTENT_LEDGER.md",
                "- %s · %s · %s · %s · %s · présentée (%s)" % (now_iso()[:10], m["id"], m["format"], m["persona"], m["channel_primary"], args.stage))
    print("%s présentée (%s) à %s" % (m["id"], args.stage, m["presented_at"]))


if __name__ == "__main__":
    main()
