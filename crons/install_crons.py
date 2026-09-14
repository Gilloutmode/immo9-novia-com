#!/usr/bin/env python3
"""Déclare, active ou désactive les crons de Novia Com via la CLI OpenClaw (subprocess, sans shell ni eval)."""
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
WS = REPO / "workspace"
OPENCLAW = shlex.split(os.environ.get("OPENCLAW", "openclaw"))


def oc(*args, capture=False):
    cmd = OPENCLAW + list(args)
    if capture:
        return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    subprocess.run(cmd, check=True)


def existing_jobs():
    try:
        out = oc("cron", "list", "--json", capture=True)
    except subprocess.CalledProcessError as e:
        sys.exit("gateway non joignable (openclaw cron list) : %s" % e)
    data = json.loads(out or "[]")
    jobs = data.get("jobs", data) if isinstance(data, dict) else data
    return {j.get("name"): j for j in jobs if isinstance(j, dict)}


def main():
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))
    unknown = [a for a in sys.argv[1:] if a not in ("--dry-run", "--enable-p1", "--disable-all")]
    if unknown:
        sys.exit("option inconnue : %s" % " ".join(unknown))
    dry = "--dry-run" in flags
    spec = json.loads((HERE / "crons.json").read_text(encoding="utf-8"))
    channels = json.loads((WS / "state" / "channels.json").read_text(encoding="utf-8")) if (WS / "state" / "channels.json").exists() else {}
    group = str(channels.get("telegram_group_id") or "")
    if not group:
        sys.exit("state/channels.json : telegram_group_id manquant (les crons livrent leur sortie dans ce groupe)")
    current = {} if dry else existing_jobs()
    created, kept = 0, 0
    for j in spec["jobs"]:
        argv = ["cron", "add", "--name", j["name"], "--cron", j["cron"], "--tz", spec["timezone"], "--agent", spec["agent"],
                "--message", spec["preamble"] + "\n\n" + j["message"], "--declaration-key", "novia-com:" + j["key"],
                "--description", j["description"], "--session", "isolated", "--announce", "--channel", "telegram",
                "--account", spec["agent"], "--to", group, "--timeout-seconds", str(j.get("timeout_seconds", 900)), "--disabled"]
        if dry:
            print(" ".join(shlex.quote(a) for a in OPENCLAW + argv)[:220] + " …")
            continue
        if j["name"] in current:
            kept += 1
            continue
        oc(*argv)
        created += 1
        print("✓ déclaré : %s" % j["name"])
    if dry:
        print("(simulation : %d jobs)" % len(spec["jobs"]))
        return
    current = existing_jobs()
    if "--enable-p1" in flags or "--disable-all" in flags:
        for j in spec["jobs"]:
            job = current.get(j["name"])
            if not job:
                print("! job absent : %s" % j["name"])
                continue
            want = ("--enable-p1" in flags and j["palier"] == 1)
            if want and not job.get("enabled"):
                oc("cron", "enable", job["id"])
                print("✓ activé : %s" % j["name"])
            elif not want and job.get("enabled"):
                oc("cron", "disable", job["id"])
                print("✓ désactivé : %s" % j["name"])
    print("Crons : %d créés, %d déjà présents. Vérifier : %s cron list" % (created, kept, " ".join(OPENCLAW)))


if __name__ == "__main__":
    main()
