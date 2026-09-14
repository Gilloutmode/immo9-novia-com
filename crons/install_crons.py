#!/usr/bin/env python3
"""Déclare, active ou désactive les crons de Novia Com via la CLI OpenClaw (subprocess, sans shell ni eval).

Identification stable par clé de déclaration (novia-com:<key>) ; la liste inclut les jobs désactivés (--all).
Toute divergence après action (job absent, état inattendu) fait échouer le script (code 1).
"""
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
WS = Path(os.environ.get("NOVIA_WORKSPACE") or (REPO / "workspace"))
OPENCLAW = shlex.split(os.environ.get("OPENCLAW", "openclaw"))
AGENT = "novia-com"


def oc(*args, capture=False):
    cmd = OPENCLAW + list(args)
    if capture:
        return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def existing_jobs():
    try:
        out = oc("cron", "list", "--all", "--agent", AGENT, "--json", capture=True)
    except subprocess.CalledProcessError as e:
        sys.exit("gateway non joignable (openclaw cron list) : %s" % e)
    data = json.loads(out or "[]")
    jobs = data.get("jobs", data) if isinstance(data, dict) else data
    by_key = {}
    for j in jobs:
        if isinstance(j, dict) and j.get("declarationKey"):
            by_key[j["declarationKey"]] = j
    return by_key


def main():
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))
    unknown = [a for a in sys.argv[1:] if a not in ("--dry-run", "--enable-p1", "--disable-all")]
    if unknown:
        sys.exit("option inconnue : %s" % " ".join(unknown))
    dry = "--dry-run" in flags
    spec = json.loads((HERE / "crons.json").read_text(encoding="utf-8"))
    ch_file = WS / "state" / "channels.json"
    channels = json.loads(ch_file.read_text(encoding="utf-8")) if ch_file.exists() else {}
    group = str(channels.get("telegram_group_id") or "")
    if not group:
        sys.exit("state/channels.json : telegram_group_id manquant (les crons livrent leur sortie dans ce groupe)")
    current = {} if dry else existing_jobs()
    created, kept, problems = 0, 0, []
    for j in spec["jobs"]:
        key = "novia-com:" + j["key"]
        argv = ["cron", "add", "--name", j["name"], "--cron", j["cron"], "--tz", spec["timezone"], "--agent", spec["agent"],
                "--message", spec["preamble"] + "\n\n" + j["message"], "--declaration-key", key,
                "--description", j["description"], "--session", "isolated", "--announce", "--channel", "telegram",
                "--account", spec["agent"], "--to", group, "--timeout-seconds", str(j.get("timeout_seconds", 900)), "--disabled"]
        if dry:
            print(" ".join(shlex.quote(a) for a in OPENCLAW + argv)[:220] + " …")
            continue
        if key in current:
            kept += 1
            continue
        oc(*argv)
        created += 1
        print("✓ déclaré : %s" % j["name"])
    if dry:
        print("(simulation : %d jobs)" % len(spec["jobs"]))
        return
    current = existing_jobs()
    for j in spec["jobs"]:
        key = "novia-com:" + j["key"]
        job = current.get(key)
        if not job:
            problems.append("job absent après déclaration : %s" % key)
            continue
        if "--enable-p1" in flags or "--disable-all" in flags:
            want = ("--enable-p1" in flags and j["palier"] == 1)
            if want and not job.get("enabled"):
                oc("cron", "enable", job["id"])
                print("✓ activé : %s" % j["name"])
            elif not want and job.get("enabled"):
                oc("cron", "disable", job["id"])
                print("✓ désactivé : %s" % j["name"])
    if "--enable-p1" in flags or "--disable-all" in flags:
        current = existing_jobs()
        for j in spec["jobs"]:
            key = "novia-com:" + j["key"]
            job = current.get(key)
            want = ("--enable-p1" in flags and j["palier"] == 1)
            if not job:
                problems.append("job absent à la vérification finale : %s" % key)
            elif bool(job.get("enabled")) != want:
                problems.append("état inattendu pour %s : enabled=%s (attendu %s)" % (key, job.get("enabled"), want))
    print("Crons : %d créés, %d déjà présents. Vérifier : %s cron list --all --agent %s" % (created, kept, " ".join(OPENCLAW), AGENT))
    if problems:
        for p in problems:
            print("✗ " + p)
        sys.exit(1)


if __name__ == "__main__":
    main()
