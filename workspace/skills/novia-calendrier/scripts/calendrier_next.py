#!/usr/bin/env python3
"""Liste les événements et échéances à venir depuis knowledge/calendrier-marronniers.json."""
import argparse
import calendar
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, read_json  # noqa: E402

SEQUENCE = [(-21, "annonce"), (-10, "pédagogie"), (-2, "rappel"), (7, "bilan")]


def occurrences(ev, start, end):
    if ev.get("date"):
        d = date.fromisoformat(ev["date"])
        return [d] if start <= d <= end else []
    rec = ev.get("recurrence") or {}
    out = []
    if rec.get("type") == "yearly":
        for y in range(start.year, end.year + 1):
            try:
                d = date(y, int(rec["month"]), int(rec["day"]))
            except ValueError:
                continue
            if start <= d <= end:
                out.append(d)
    elif rec.get("type") == "monthly":
        y, m = start.year, start.month
        while (y, m) <= (end.year, end.month):
            day = min(int(rec.get("day", 1)), calendar.monthrange(y, m)[1])
            d = date(y, m, day)
            if start <= d <= end:
                out.append(d)
            m += 1
            if m > 12:
                m, y = 1, y + 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--month", default=None, help="AAAA-MM")
    ap.add_argument("--kind", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    ws = find_workspace()
    events = read_json(ws / "knowledge" / "calendrier-marronniers.json", {}).get("events", [])
    if args.month:
        y, m = [int(x) for x in args.month.split("-")]
        start, end = date(y, m, 1), date(y, m, calendar.monthrange(y, m)[1])
    else:
        start, end = date.today(), date.today() + timedelta(days=args.days)
    rows = []
    for ev in events:
        if args.kind and ev.get("kind") != args.kind:
            continue
        for d in occurrences(ev, start, end):
            rows.append({"date": d.isoformat(), "name": ev["name"], "kind": ev.get("kind"), "city": ev.get("city", ""),
                         "confirmed": bool(ev.get("confirmed", False)) if (ev.get("kind") == "salon" or ev.get("date")) else True,
                         "source": ev.get("source", ""), "note": ev.get("note", ""), "important": bool(ev.get("important", False)),
                         "sequence": [{"date": (d + timedelta(days=off)).isoformat(), "step": step} for off, step in SEQUENCE] if ev.get("important") else []})
    rows.sort(key=lambda r: r["date"])
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    if not rows:
        print("Rien au calendrier entre %s et %s." % (start, end))
        return
    print("📅 Du %s au %s" % (start.strftime("%d/%m"), end.strftime("%d/%m/%Y")))
    for r in rows:
        flag = "" if r["confirmed"] else " · à confirmer"
        city = (" · " + r["city"]) if r["city"] else ""
        print("- %s · %s (%s%s)%s%s" % (r["date"], r["name"], r["kind"], city, flag, (" · " + r["note"]) if r["note"] else ""))
        if r["sequence"]:
            print("    séquence : " + ", ".join("%s %s" % (s["step"], s["date"][5:]) for s in r["sequence"]))


if __name__ == "__main__":
    main()
