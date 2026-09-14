#!/usr/bin/env python3
"""Contrôle machine d'une légende ou d'un post avant présentation : limites, lexique, conformité."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, read_json  # noqa: E402

LIMITS = {
    "linkedin": {"max": 3000, "hashtags_max": 3, "fold": 210},
    "instagram": {"max": 2200, "hashtags_max": 5, "fold": 125},
    "facebook": {"max": 63206, "hashtags_max": 2, "fold": 125},
    "tiktok": {"max": 2200, "hashtags_max": 5, "fold": 100},
    "youtube": {"max": 5000, "hashtags_max": 5, "fold": 150},
    "newsletter": {"max": 6000, "hashtags_max": 0, "fold": 90},
    "site": {"max": 20000, "hashtags_max": 0, "fold": 160},
}
PROMISES = [r"rendement\s+(garanti|assur[ée]|s[ûu]r)", r"sans\s+risque", r"plus-value\s+(garantie|assur[ée])",
            r"placement\s+(s[ûu]r|en\s+or)", r"gain\s+garanti", r"rentabilit[ée]\s+(garantie|assur[ée])"]
URGENCY = [r"derni[èe]res?\s+(unit[ée]s?|lots?|chances?|opportunit[ée]s?)", r"plus\s+que\s+\d+\s+(lots?|appartements?)",
           r"offre\s+limit[ée]e", r"avant\s+qu'il\s+ne\s+soit\s+trop\s+tard", r"vite\s*!", r"d[ée]p[êe]chez"]
AI_FORMULAS = [r"dans\s+un\s+monde\s+o[ùu]", r"il\s+est\s+important\s+de\s+noter", r"en\s+conclusion",
               r"que\s+vous\s+soyez.*ou", r"n'h[ée]sitez\s+pas", r"excellente\s+question", r"plongeons", r"d[ée]couvrez\s+comment"]
TUTOIEMENT = [r"\btu\b", r"\bton\b", r"\bta\b", r"\btes\b", r"\bt'as\b", r"\bt'es\b"]


def main():
    ap = argparse.ArgumentParser(description="Contrôle d'une légende Novia Com")
    ap.add_argument("--channel", required=True, choices=sorted(LIMITS))
    ap.add_argument("--persona", default=None, choices=["P1", "P2", "P3", "P4"])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file")
    src.add_argument("--text")
    ap.add_argument("--allow-tutoiement", action="store_true", help="texte interne, pas public")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = args.text if args.text is not None else Path(args.file).read_text(encoding="utf-8")
    ws = find_workspace()
    banned = read_json(ws / "knowledge" / "lexique-banni.json", {}).get("banned", [])
    low = text.lower()
    lim = LIMITS[args.channel]
    fails, warns = [], []

    n = len(text)
    if n > lim["max"]:
        fails.append("longueur %d > limite %s %d" % (n, args.channel, lim["max"]))
    first_line = text.strip().split("\n", 1)[0]
    if len(first_line) > lim["fold"]:
        warns.append("première ligne de %d caractères, visible avant repli : ~%d" % (len(first_line), lim["fold"]))
    tags = re.findall(r"(?<!\w)#\w+", text)
    if len(tags) > lim["hashtags_max"]:
        fails.append("%d hashtags > %d autorisés sur %s" % (len(tags), lim["hashtags_max"], args.channel))
    for w in banned:
        if w.lower() in low:
            fails.append("mot banni : « %s »" % w)
    for pat in PROMISES:
        if re.search(pat, low):
            fails.append("promesse de rendement ou de sécurité : /%s/" % pat)
    for pat in URGENCY:
        if re.search(pat, low):
            fails.append("urgence fabriquée : /%s/" % pat)
    for pat in AI_FORMULAS:
        if re.search(pat, low):
            fails.append("formule creuse ou IA : /%s/" % pat)
    if "\u2014" in text or "\u2013" in text:  # tiret long, demi-cadratin
        fails.append("tiret long ou demi-cadratin présent (à remplacer par une virgule, un point ou deux points)")
    if not args.allow_tutoiement:
        for pat in TUTOIEMENT:
            if re.search(pat, low):
                fails.append("tutoiement dans un texte public : /%s/" % pat)
                break
    has_number = re.search(r"\d[\d\s]*(%|€|euros?|m²|ans?\b|mois\b)", low) is not None
    has_source = ("http" in low) or ("selon " in low) or ("source" in low) or ("d'après " in low)
    if has_number and not has_source:
        fails.append("chiffre présent sans source (« selon … », URL ou « source : »)")
    if args.persona == "P2" and not re.search(r"risque", low):
        fails.append("contenu investisseur (P2) sans mention des risques")
    emojis = re.findall(r"[\U0001F300-\U0001FAFF☀-➿]", text)
    if len(emojis) > 2:
        warns.append("%d émojis (2 au maximum conseillés)" % len(emojis))

    result = {"channel": args.channel, "length": n, "hashtags": len(tags), "fails": fails, "warnings": warns, "ok": not fails}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("OK" if not fails else "FAIL")
        for f in fails:
            print("  ✗ " + f)
        for w in warns:
            print("  ! " + w)
        print("  longueur %d · hashtags %d" % (n, len(tags)))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
