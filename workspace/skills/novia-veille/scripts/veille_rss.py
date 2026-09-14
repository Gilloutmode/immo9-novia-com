#!/usr/bin/env python3
"""Lit les flux RSS/Atom des sources autorisées, filtre par mots-clés, dédoublonne, imprime un digest."""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, read_json, write_json, append_line  # noqa: E402

UA = "Mozilla/5.0 (compatible; NoviaCom/1.0; +https://toulouseimmo9.com)"
NS = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/", "content": "http://purl.org/rss/1.0/modules/content/"}


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.5"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
        if d is not None and d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except Exception:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s.replace("Z", "+0000") if fmt.endswith("%z") else s, fmt)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def strip_html(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s or "")).strip()


def parse_feed(raw):
    root = ET.fromstring(raw)
    items = []
    if root.tag.endswith("feed"):  # Atom
        for e in root.findall("atom:entry", NS):
            link = ""
            for l in e.findall("atom:link", NS):
                if l.get("rel") in (None, "alternate"):
                    link = l.get("href", "")
                    break
            items.append({"title": strip_html(e.findtext("atom:title", default="", namespaces=NS)), "link": link,
                          "date": parse_date(e.findtext("atom:published", default=None, namespaces=NS) or e.findtext("atom:updated", default=None, namespaces=NS)),
                          "summary": strip_html(e.findtext("atom:summary", default="", namespaces=NS) or e.findtext("atom:content", default="", namespaces=NS))[:400]})
    else:  # RSS 2.0 / RDF
        for it in root.iter():
            if not it.tag.endswith("item"):
                continue
            title = link = desc = date = None
            for c in it:
                t = c.tag.split("}")[-1]
                if t == "title":
                    title = c.text
                elif t == "link":
                    link = (c.text or c.get("href") or "").strip()
                elif t in ("description", "encoded", "summary") and not desc:
                    desc = c.text
                elif t in ("pubDate", "date", "updated", "published") and not date:
                    date = c.text
            items.append({"title": strip_html(title), "link": link or "", "date": parse_date(date), "summary": strip_html(desc)[:400]})
    return items


def matches(text, include, exclude):
    low = text.lower()
    if any(x.lower() in low for x in exclude):
        return False
    return (not include) or any(k.lower() in low for k in include)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=2, help="ne garder que les items plus récents que N jours")
    ap.add_argument("--max-per-source", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true", help="n'écrit ni l'état ni le cumul")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--theme", default=None, help="limiter à un thème (reglementaire, fiscal, taux, prix, local, promotion, presse)")
    args = ap.parse_args()

    ws = find_workspace()
    cfg = read_json(ws / "knowledge" / "sources-veille.json", {})
    sources = list(cfg.get("sources", []))
    for i, feed in enumerate((cfg.get("google_alerts") or {}).get("feeds", []), 1):
        if isinstance(feed, dict) and feed.get("rss"):
            sources.append({"name": feed.get("name") or "Alerte Google %d" % i, "rss": feed["rss"], "type": "presse", "scope": "alert", "confidence": "moyenne", "themes": ["mentions"]})
    kw = read_json(ws / "knowledge" / "veille-keywords.json", {})
    include, exclude = kw.get("include", []), kw.get("exclude", [])
    cities = [c.lower() for c in kw.get("cities", [])]
    seen_path = ws / "state" / "veille-seen.json"
    seen = read_json(seen_path, {}) or {}
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    found, errors = [], []
    for s in sources:
        if not s.get("rss") or (args.theme and args.theme not in s.get("themes", [])):
            continue
        try:
            items = parse_feed(fetch(s["rss"]))
        except (urllib.error.URLError, urllib.error.HTTPError, ET.ParseError, TimeoutError, OSError) as e:
            errors.append("%s : %s" % (s["name"], str(e)[:80]))
            continue
        kept = 0
        for it in items:
            try:
                if not it["link"] or it["link"] in seen:
                    continue
                if it["date"] and it["date"] < since:
                    continue
            except Exception as e:  # une entrée défectueuse ne bloque pas la source
                errors.append("%s : item ignoré (%s)" % (s["name"], str(e)[:60]))
                continue
            text = "%s %s" % (it["title"], it["summary"])
            if s.get("type") == "presse" and s.get("scope") != "alert" and not matches(text, include, exclude):
                continue
            if s.get("type") == "presse" and s.get("scope") == "national" and cities and not any(c in text.lower() for c in cities):
                pass  # presse nationale : pas de filtre ville (le sujet immo suffit)
            if any(x.lower() in text.lower() for x in exclude):
                continue
            found.append({"source": s["name"], "type": s.get("type"), "confidence": s.get("confidence"), "themes": s.get("themes", []),
                          "title": it["title"], "url": it["link"], "date": it["date"].date().isoformat() if it["date"] else None, "summary": it["summary"]})
            kept += 1
            if kept >= args.max_per_source:
                break
    order = {"officiel": 0, "professionnel": 1, "presse": 2, "social": 3}
    found.sort(key=lambda x: (order.get(x["type"], 9), x["date"] or "", x["source"]), reverse=False)
    found.sort(key=lambda x: x["date"] or "", reverse=True)
    if args.json:
        print(json.dumps({"items": found, "errors": errors}, ensure_ascii=False, indent=2))
    else:
        if not found:
            print("NO_REPLY" if not errors else "Aucune nouveauté. Sources injoignables : " + " ; ".join(errors))
        else:
            today = datetime.now().strftime("%d/%m/%Y")
            print("🔎 Veille du %s (%d nouveautés)" % (today, len(found)))
            for i, it in enumerate(found, 1):
                print("%d. [%s · %s] %s (%s)\n   %s" % (i, it["source"], it["type"], it["title"], it["date"] or "date non trouvée", it["url"]))
            if errors:
                print("Sources injoignables : " + " ; ".join(errors))
    if not args.dry_run:
        today = datetime.now().strftime("%Y-%m-%d")
        for it in found:
            seen[it["url"]] = today
            append_line(ws / "learning" / "VEILLE.md", "- %s · %s · %s · %s · %s" % (today, it["source"], it["date"] or "n.d.", it["title"], it["url"]))
        if len(seen) > 5000:  # rotation simple
            seen = dict(sorted(seen.items(), key=lambda kv: kv[1])[-4000:])
        write_json(seen_path, seen)


if __name__ == "__main__":
    main()
