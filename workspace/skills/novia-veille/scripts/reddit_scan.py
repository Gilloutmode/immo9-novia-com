#!/usr/bin/env python3
"""Repère les questions récentes sur Reddit (endpoints JSON publics, lecture seule, sans clé)."""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, read_json, write_json  # noqa: E402

UA = "NoviaCom/1.0 (veille lecture seule; contact: web@toulouseimmo9.com)"
TOKEN = None


def get_token():
    """Jeton OAuth (grant client_credentials) si REDDIT_CLIENT_ID et REDDIT_CLIENT_SECRET sont définis."""
    global TOKEN
    cid, secret = os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")
    if not cid or not secret or TOKEN:
        return TOKEN
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    auth = base64.b64encode(("%s:%s" % (cid, secret)).encode("utf-8")).decode("ascii")
    req = urllib.request.Request("https://www.reddit.com/api/v1/access_token", data=data, method="POST",
                                 headers={"User-Agent": UA, "Authorization": "Basic " + auth})
    with urllib.request.urlopen(req, timeout=20) as resp:
        TOKEN = json.loads(resp.read().decode("utf-8")).get("access_token")
    return TOKEN


def get_json(url):
    token = get_token()
    if token:
        url = url.replace("https://www.reddit.com/", "https://oauth.reddit.com/")
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ws = find_workspace()
    kw = read_json(ws / "knowledge" / "veille-keywords.json", {})
    reddit = kw.get("reddit", {})
    subs, terms = reddit.get("subreddits", []), [t.lower() for t in reddit.get("terms", kw.get("include", []))]
    seen_path = ws / "state" / "reddit-seen.json"
    seen = read_json(seen_path, {}) or {}
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    out, errors = [], []
    for sub in subs:
        url = "https://www.reddit.com/r/%s/new.json?limit=%d" % (sub, args.limit)
        try:
            data = get_json(url)
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            errors.append("r/%s : %s" % (sub, str(e)[:60]))
            time.sleep(2)
            continue
        for child in data.get("data", {}).get("children", []):
            p = child.get("data", {})
            created = datetime.fromtimestamp(p.get("created_utc", 0), tz=timezone.utc)
            if created < since:
                continue
            link = "https://www.reddit.com" + p.get("permalink", "")
            if link in seen:
                continue
            text = ("%s %s" % (p.get("title", ""), p.get("selftext", ""))).lower()
            if terms and not any(t in text for t in terms):
                continue
            out.append({"sub": sub, "title": p.get("title", ""), "url": link, "score": p.get("score", 0), "comments": p.get("num_comments", 0), "date": created.date().isoformat()})
        time.sleep(2)  # politesse
    if not out:
        hint = "" if get_token() else " (accès anonyme bloqué par Reddit : déclarer REDDIT_CLIENT_ID et REDDIT_CLIENT_SECRET, voir connectors/README.md)"
        print("NO_REPLY" if not errors else "Aucune question nouvelle. Reddit injoignable : " + " ; ".join(errors) + hint)
    else:
        print("❓ Questions Reddit (%d)" % len(out))
        for i, q in enumerate(sorted(out, key=lambda x: x["date"], reverse=True), 1):
            print("%d. r/%s · %s (%s, %d commentaires)\n   %s" % (i, q["sub"], q["title"], q["date"], q["comments"], q["url"]))
        if errors:
            print("Injoignable : " + " ; ".join(errors))
    if not args.dry_run:
        for q in out:
            seen[q["url"]] = q["date"]
        write_json(seen_path, seen)


if __name__ == "__main__":
    main()
