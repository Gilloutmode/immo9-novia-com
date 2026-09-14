#!/usr/bin/env python3
"""Enregistre une approbation Go 1 ou Go 2 après vérification de l'auteur, du texte et du délai."""
import argparse
import re
import sys
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from novia_common import find_workspace, load_manifest, write_json, now_iso, add_history, read_json, load_contract, package_fingerprint  # noqa: E402


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(s.lower().split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piece_id")
    ap.add_argument("--stage", required=True, choices=["go1", "go2"])
    ap.add_argument("--by", required=True, help="identifiant Telegram de l'auteur du message")
    ap.add_argument("--text", required=True, help="texte exact du message")
    ap.add_argument("--reply-to", default=None, help="identifiant du message Telegram auquel l'approbation répond (doit être la carte)")
    ap.add_argument("--message-id", default=None, help="identifiant du message d'approbation")
    ap.add_argument("--chat-id", default=None, help="identifiant du chat Telegram où l'approbation a été donnée")
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
    conditions = (" si ", " quand ", " lorsque ", " apres ", " des que ", " une fois ", " sous reserve", " a condition", " mais ", " sauf ",
                  " a moins ", " moins que", " excepte", " hormis", " tant que", " seulement", " uniquement", " d'abord", " avant ", " puis ", " ensuite", " sinon")
    if any(c in (" " + text + " ") for c in conditions):
        sys.exit("REFUS : le message contient une condition ou une réserve ; demander une approbation sans condition.")
    negations = ("ne ", "n'", "pas", "non", "rien", "jamais", "sauf", "stop", "attend", "plus tard", "pas encore", "annule", "surtout pas")
    if any((" " + n) in (" " + text + " ") or text.startswith(n) for n in negations):
        sys.exit("REFUS : le message contient une négation ou une réserve ; demander une réponse claire.")
    words = [norm(w) for w in val.get("go2_words" if args.stage == "go2" else "go1_words", [])]
    if args.stage == "go1":
        words += [norm(w) for w in val.get("go2_words", [])]  # un « Go publie » vaut aussi Go 1
    never = [norm(w) for w in val.get("never_approval", [])]
    if text in never:
        sys.exit("REFUS : « %s » ne vaut jamais approbation." % args.text)
    core = re.sub(r"[^a-z0-9 ]", " ", text)
    core = " ".join(core.split())
    if core not in words:
        sys.exit("REFUS : l'approbation doit être une formule complète et seule (%s), sans texte ajouté ; ici : « %s ». Les précisions (canal, horaire) se donnent dans un message séparé." % (", ".join(words), args.text))
    if not m.get("presented_at"):
        sys.exit("REFUS : la pièce n'a pas été présentée (outbox_present.py).")
    ttl = timedelta(hours=float(val.get("approval_ttl_hours", 24)))
    presented = datetime.fromisoformat(m["presented_at"])
    if datetime.now(presented.tzinfo) - presented > ttl:
        sys.exit("REFUS : présentation trop ancienne (> %s h) ; re-présenter la pièce." % val.get("approval_ttl_hours", 24))
    if args.stage == "go2" and m["status"] != "final_presented":
        sys.exit("REFUS : Go 2 n'est accepté que sur un package final présenté (statut actuel : %s)." % m["status"])
    if args.stage == "go2":
        if m.get("is_test"):
            sys.exit("REFUS : pièce test de calibration, jamais publiable.")
        fp = package_fingerprint(ws, m)
        if m.get("package_fingerprint") != fp:
            sys.exit("REFUS : le package a changé depuis sa présentation (légendes, fichiers, canaux ou plafond) ; re-présenter.")
        if not m.get("card_message_id"):
            sys.exit("REFUS : identifiant de la carte non enregistré ; relancer outbox_present.py --stage final --card-id <id du message> avant toute approbation.")
        if not args.reply_to or not args.message_id or not args.chat_id:
            sys.exit("REFUS : --reply-to, --message-id et --chat-id sont obligatoires pour Go 2 (identifiants Telegram du message d'approbation).")
        if str(args.reply_to) != str(m["card_message_id"]):
            sys.exit("REFUS : le message ne répond pas à la carte de cette pièce (%s attendu, %s reçu)." % (m["card_message_id"], args.reply_to))
        channels_state = read_json(ws / "state" / "channels.json", {})
        allowed_chats = {str(channels_state.get("telegram_group_id", ""))} | {str(a.get("telegram_id")) for a in approvers}
        if str(args.chat_id) not in allowed_chats:
            sys.exit("REFUS : chat %s inconnu (ni le groupe Novia Com, ni un DM d'une personne autorisée)." % args.chat_id)
    if args.stage == "go1" and m["status"] not in ("presented", "final_presented"):
        sys.exit("REFUS : statut %s incompatible avec Go 1." % m["status"])

    record = {"by": str(args.by), "name": who.get("name"), "at": now_iso(), "text": args.text, "reply_to": args.reply_to,
              "message_id": args.message_id, "chat_id": args.chat_id, "package_fingerprint": m.get("package_fingerprint"),
              "channels": list(m.get("channels", [])), "ceiling": m.get("cost", {}).get("ceiling")}
    m["approvals"][args.stage] = record
    m["status"] = "go1" if args.stage == "go1" else "approved"
    add_history(m, "approved_%s" % args.stage, by=str(args.by), note=args.text)
    write_json(path, m)
    print("OK : %s → %s par %s (%s)" % (m["id"], m["status"], who.get("name"), record["at"]))


if __name__ == "__main__":
    main()
