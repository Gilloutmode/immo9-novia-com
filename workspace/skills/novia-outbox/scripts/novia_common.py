"""Fonctions partagées des scripts Novia Com (stdlib uniquement, Python 3.8+)."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_workspace(start=None):
    """Remonte depuis le script (ou NOVIA_WORKSPACE) jusqu'au dossier contenant AGENTS.md et state/."""
    env = os.environ.get("NOVIA_WORKSPACE")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "AGENTS.md").exists():
            return p
        sys.exit("NOVIA_WORKSPACE ne pointe pas vers un workspace (AGENTS.md absent) : %s" % p)
    p = Path(start or __file__).resolve()
    for d in [p] + list(p.parents):
        if (d / "AGENTS.md").exists() and (d / "state").is_dir():
            return d
    sys.exit("workspace introuvable : lancer depuis le workspace ou définir NOVIA_WORKSPACE")


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def load_contract(ws):
    return read_json(ws / "doctrine" / "STUDIO_CONTRACT.json", {})


def load_manifest(ws, piece_id):
    path = ws / "outbox" / piece_id / "manifest.json"
    data = read_json(path)
    if data is None:
        sys.exit("pièce inconnue : %s (manifest absent)" % piece_id)
    return path, data


def append_line(path, line):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", encoding="utf-8") as f:
        if new:
            f.write("# %s\n\n" % path.stem)
        f.write(line.rstrip("\n") + "\n")


def add_history(manifest, event, by=None, note=None):
    manifest.setdefault("history", []).append({
        "at": now_iso(), "event": event, "by": by, "note": note,
    })


def send_plan(manifest):
    """Plan d'envoi canonique : pour chaque canal, ce qui aura un effet externe (légende, titre, persona, fichiers dans l'ordre)."""
    channels = list(manifest.get("channels") or [manifest.get("channel_primary")])
    plan = []
    for ch in channels:
        assets = [a.get("file", "") for a in manifest.get("assets", []) if not a.get("channels") or ch in a["channels"]]
        plan.append({"channel": ch, "caption": manifest.get("captions", {}).get(ch) or manifest.get("captions", {}).get("default") or "",
                     "title": manifest.get("title", ""), "persona": manifest.get("persona"), "assets": assets,
                     "ceiling": manifest.get("cost", {}).get("ceiling")})
    return plan


def package_fingerprint(ws, manifest):
    """Empreinte SHA-256 du plan d'envoi et du contenu des fichiers, dans l'ordre. Change = approbation caduque."""
    import hashlib
    h = hashlib.sha256()
    h.update(json.dumps(send_plan(manifest), sort_keys=True, ensure_ascii=False).encode("utf-8"))
    for a in manifest.get("assets", []):  # ordre du manifest conservé
        f = ws / "outbox" / manifest["id"] / a.get("file", "")
        h.update(("|" + a.get("file", "") + "|" + ",".join(a.get("channels") or [])).encode("utf-8"))
        if f.is_file():
            with f.open("rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
        else:
            h.update(b"<missing>")
    return h.hexdigest()


def missing_assets(ws, manifest):
    return [a.get("file", "") for a in manifest.get("assets", []) if not (ws / "outbox" / manifest["id"] / a.get("file", "")).is_file()]


def onboarding_status(ws):
    return (read_json(ws / "state" / "onboarding.json", {}) or {}).get("status", "act0_diagnostic")


def onboarding_rank(ws, status=None):
    acts = load_contract(ws).get("onboarding", {}).get("acts", [])
    st = status or onboarding_status(ws)
    return acts.index(st) if st in acts else -1
