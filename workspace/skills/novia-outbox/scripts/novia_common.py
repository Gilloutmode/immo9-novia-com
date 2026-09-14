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
