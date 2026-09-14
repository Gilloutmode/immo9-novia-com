#!/usr/bin/env python3
"""Publie une pièce approuvée via l'adaptateur configuré.

Préconditions vérifiées ici (et non seulement dans la charte) : onboarding complete, statut approved avec
enregistrement go2, auteur toujours autorisé, approbation récente, package inchangé depuis la présentation,
canaux demandés inclus dans ceux approuvés, aucune publication concurrente (verrou), cibles déjà publiées
non rejouées. Le statut « published » n'est écrit que si chaque cible a un succès terminal.
"""
import argparse
import importlib.util
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "novia-outbox" / "scripts"))
from novia_common import find_workspace, load_manifest, write_json, now_iso, add_history, read_json, append_line, load_contract, package_fingerprint, onboarding_status  # noqa: E402

TERMINAL_OK = {"published"}
PENDING = {"submitted", "processing", "draft_remote"}


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


def export_media(ws, m, assets):
    """Copie les seuls médias à publier dans export/<id>/ (le dossier servi publiquement, jamais outbox/)."""
    dst_dir = ws / "export" / m["id"]
    dst_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for a in assets:
        rel = Path(a).relative_to(ws / "outbox" / m["id"])
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(a, dst)
        out.append(str(rel))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piece_id")
    ap.add_argument("--channel", action="append", default=[], help="canal à publier (défaut : canaux approuvés)")
    ap.add_argument("--dry-run", action="store_true", help="simulation complète (adaptateur dryrun), aucun appel externe")
    ap.add_argument("--preview", action="store_true", help="montre ce qui serait envoyé, sans approbation requise, sans appel externe")
    args = ap.parse_args()

    ws = find_workspace()
    contract = load_contract(ws)
    lock = ws / "outbox" / args.piece_id / ".publish.lock"
    if not args.preview:
        if not lock.parent.is_dir():
            sys.exit("pièce inconnue : %s" % args.piece_id)
        try:  # verrou AVANT toute lecture : deux exécutions ne peuvent pas partir de la même copie
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, now_iso().encode("utf-8"))
            os.close(fd)
        except FileExistsError:
            sys.exit("REFUS : publication déjà en cours pour %s (verrou %s)." % (args.piece_id, lock.name))
    try:
        _run(ws, contract, args, lock)
    finally:
        if not args.preview:
            try:
                lock.unlink()
            except FileNotFoundError:
                pass


def _run(ws, contract, args, lock):
    path, m = load_manifest(ws, args.piece_id)
    channels_cfg = read_json(ws / "state" / "channels.json", {"channels": {}}).get("channels", {})
    approved_channels = list((m["approvals"].get("go2") or {}).get("channels") or m.get("channels") or [m["channel_primary"]])
    targets = args.channel or approved_channels

    if args.preview:
        for ch in targets:
            cfg = channels_cfg.get(ch, {})
            caption = m["captions"].get(ch) or m["captions"].get("default") or ""
            assets = [a["file"] for a in m.get("assets", []) if not a.get("channels") or ch in a["channels"]]
            print("[aperçu] %s via %s : %d fichier(s) %s ; légende %d caractères :\n%s\n" % (ch, cfg.get("adapter") or "(non configuré)", len(assets), assets, len(caption), caption))
        return

    if onboarding_status(ws) != "complete":
        sys.exit("REFUS : onboarding en %s ; aucune publication avant complete." % onboarding_status(ws))
    if m.get("is_test"):
        sys.exit("REFUS : pièce test de calibration, jamais publiable.")
    if m["status"] not in ("approved", "submitted") or not m["approvals"].get("go2"):
        sys.exit("REFUS : pièce %s sans « Go publie » enregistré (statut %s)." % (m["id"], m["status"]))
    go2 = m["approvals"]["go2"]
    approvers = read_json(ws / "state" / "approvers.json", {"approvers": []}).get("approvers", [])
    if not any(str(a.get("telegram_id")) == str(go2.get("by")) for a in approvers):
        sys.exit("REFUS : l'auteur du Go publie n'est plus dans state/approvers.json.")
    ttl = timedelta(hours=float(contract.get("validation", {}).get("approval_ttl_hours", 24)))
    at = datetime.fromisoformat(go2["at"])
    if datetime.now(at.tzinfo) - at > ttl:
        sys.exit("REFUS : « Go publie » trop ancien (> %s h) ; re-présenter la pièce." % contract.get("validation", {}).get("approval_ttl_hours", 24))
    if package_fingerprint(ws, m) != go2.get("package_fingerprint"):
        sys.exit("REFUS : le package a changé depuis l'approbation ; re-présenter et refaire approuver.")
    extra = [ch for ch in targets if ch not in approved_channels]
    if extra:
        sys.exit("REFUS : canal non approuvé : %s (approuvés : %s)." % (", ".join(extra), ", ".join(approved_channels)))

    results_prev = m["publication"].get("results", [])
    done = {r["channel"] for r in results_prev if r.get("state") in TERMINAL_OK}
    pending = {r["channel"]: r for r in results_prev if r.get("state") in PENDING}
    results = []
    for ch in targets:
        if not args.dry_run and ch in done:
            print("%s : déjà publié, ignoré" % ch)
            continue
        if not args.dry_run and ch in pending:
            r = pending[ch]
            print("%s : déjà soumis le %s (%s), en attente de confirmation chez le prestataire ; rien n'est renvoyé. Vérifier avec l'identifiant %s." % (ch, r.get("at"), r.get("state"), r.get("id")))
            continue
        cfg = dict(channels_cfg.get(ch, {}))
        adapter_name = "dryrun" if args.dry_run else cfg.get("adapter")
        if not adapter_name:
            sys.exit("REFUS : aucun adaptateur configuré pour le canal « %s » dans state/channels.json." % ch)
        caption = m["captions"].get(ch) or m["captions"].get("default") or ""
        assets = [ws / "outbox" / m["id"] / a["file"] for a in m.get("assets", []) if not a.get("channels") or ch in a["channels"]]
        missing = [str(a) for a in assets if not a.exists()]
        if missing:
            sys.exit("REFUS : fichiers manquants : %s" % ", ".join(missing))
        if adapter_name == "meta_graph":
            cfg["exported_files"] = export_media(ws, m, [str(a) for a in assets])
        cfg["idempotency_key"] = "%s:%s:%s" % (m["id"], ch, (go2.get("package_fingerprint") or "")[:16])
        mod = load_adapter(adapter_name)
        if not args.dry_run:  # tentative persistée avant l'envoi : une reprise sait qu'un appel a pu partir
            m["publication"]["results"].append({"channel": ch, "adapter": adapter_name, "at": now_iso(), "state": "attempt", "idempotency_key": cfg["idempotency_key"]})
            write_json(path, m)
        try:
            res = mod.publish(channel=ch, settings=cfg, caption=caption, assets=[str(a) for a in assets], manifest=m)
        except Exception as e:  # rapporté tel quel, sans repli silencieux
            if not args.dry_run:
                m["publication"]["results"] = [r for r in m["publication"]["results"] if not (r.get("channel") == ch and r.get("state") == "attempt")]
            add_history(m, "publish_failed", by="agent", note="%s: %s" % (ch, e))
            write_json(path, m)
            sys.exit("ÉCHEC publication %s via %s : %s" % (ch, adapter_name, e))
        res = dict(res or {})
        state = "simulated" if adapter_name == "dryrun" else (res.get("state") or "submitted")
        res.update({"channel": ch, "adapter": adapter_name, "at": now_iso(), "state": state, "idempotency_key": cfg["idempotency_key"]})
        results.append(res)
        if state != "simulated":
            m["publication"]["results"] = [r for r in m["publication"]["results"] if not (r.get("channel") == ch and r.get("state") == "attempt")]
            m["publication"]["results"].append(res)
            write_json(path, m)  # chaque résultat est sauvegardé immédiatement
            label = {"published": "publiée", "submitted": "soumise (en attente de confirmation)", "processing": "en traitement", "draft_remote": "brouillon créé chez le prestataire"}.get(state, state)
            append_line(ws / "learning" / "CONTENT_LEDGER.md",
                        "- %s · %s · %s · %s · %s · %s · %s" % (now_iso()[:10], m["id"], m["format"], m["persona"], ch, label, res.get("url") or res.get("id") or ""))
            if state in TERMINAL_OK:
                append_line(ws / "learning" / "FEED_STATE.md", "- %s · %s · %s · %s · %s" % (now_iso()[:10], ch, m["format"], m["title"], res.get("url") or ""))
    if not args.dry_run:
        states = {}
        for r in m["publication"]["results"]:
            states[r["channel"]] = r.get("state")
        if all(states.get(ch) in TERMINAL_OK for ch in approved_channels):
            if m["status"] != "published":
                m["status"] = "published"
                add_history(m, "published", by=str(go2.get("by")))
        else:
            m["status"] = "submitted"
            add_history(m, "submitted", by=str(go2.get("by")), note=str(states))
        write_json(path, m)
    else:
        add_history(m, "publish_dry_run", by="agent")
        write_json(path, m)
    for r in results:
        print("%s via %s [%s] : %s" % (r["channel"], r["adapter"], r["state"], r.get("url") or r.get("id") or r.get("message", "ok")))


if __name__ == "__main__":
    main()
