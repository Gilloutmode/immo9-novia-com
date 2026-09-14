#!/usr/bin/env python3
"""Prépare le fragment de configuration à partir du gabarit, du workspace et des fichiers d'état (sans secret).

Usage : prepare_patch.py <gabarit.json5> <workspace> <sortie.json> [--with-telegram] [--allow-example-ids]
Sortie standard : résumé. Code 2 si des identifiants d'exemple subsistent (sauf --allow-example-ids).
"""
import json
import os
import re
import sys


def json5_to_json(text):
    text = re.sub(r"(?m)^\s*//.*$", "", text)
    text = re.sub(r"(?m)(?<=[\s,{}\[\]])//(?!/).*$", "", text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    text = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_-]*)\s*:", r'\1"\2":', text)
    return json.loads(text)


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def example_ids(ws):
    ids = set()
    for name in ("approvers.json.example", "channels.json.example"):
        d = load(os.path.join(ws, "state", name))
        for a in d.get("approvers", []):
            ids.add(str(a.get("telegram_id")))
        if d.get("telegram_group_id"):
            ids.add(str(d["telegram_group_id"]))
    return ids


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))
    src, ws, out = args[:3]
    with open(src, encoding="utf-8") as f:
        data = json5_to_json(f.read().replace("__WORKSPACE__", ws))
    approvers = [str(a.get("telegram_id")) for a in load(os.path.join(ws, "state", "approvers.json")).get("approvers", []) if a.get("telegram_id")]
    group = str(load(os.path.join(ws, "state", "channels.json")).get("telegram_group_id", "") or "")
    placeholders = [x for x in approvers + ([group] if group else []) if x in example_ids(ws)]
    if placeholders and "--allow-example-ids" not in flags:
        print("REFUS : identifiants d'exemple encore présents dans state/ (%s). Remplacer par les vrais identifiants Telegram." % ", ".join(placeholders))
        sys.exit(2)
    # variables des connecteurs : seulement celles présentes dans l'environnement
    absent_all = []
    for skill, entry in list(data.get("skills", {}).get("entries", {}).items()):
        env = entry.get("env")
        if not env:
            continue
        present = {k: v for k, v in env.items() if os.environ.get(k)}
        absent_all += [k for k in env if k not in present]
        if present:
            entry["env"] = present
        else:
            entry.pop("env", None)
    if "--with-telegram" in flags:
        acc = data["channels"]["telegram"]["accounts"]["novia-com"]
        acc["allowFrom"] = approvers
        acc["groupAllowFrom"] = approvers
        acc["groups"] = {group: {"requireMention": False, "allowFrom": approvers}} if group else {}
    else:
        data.pop("channels", None)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("fragment préparé : %d personne(s) autorisée(s), groupe %s, Telegram %s" % (len(approvers), group or "(non renseigné)", "inclus" if "--with-telegram" in flags else "omis (jeton absent)"))
    if absent_all:
        print("variables non définies pour l'instant (relancer install.sh après les avoir déclarées) : %s" % ", ".join(sorted(set(absent_all))))


if __name__ == "__main__":
    main()
