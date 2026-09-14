#!/usr/bin/env python3
"""Construit l'infographie mensuelle HTML depuis knowledge/donnees-marche.json (sources obligatoires)."""
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, read_json  # noqa: E402

DEFAULT_TOKENS = {"color_primary": "#1F3A5F", "color_secondary": "#F4F1EA", "color_accent": "#B88B2C", "color_text": "#1A1A1A",
                  "color_muted": "#5B6470", "font_title": "Georgia, 'Times New Roman', serif", "font_body": "Arial, Helvetica, sans-serif", "brand_name": "IMMO9", "logo_path": ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--square", action="store_true")
    args = ap.parse_args()
    ws = find_workspace()
    data = read_json(ws / "knowledge" / "donnees-marche.json", {})
    tokens = dict(DEFAULT_TOKENS)
    tokens.update({k: v for k, v in (read_json(ws / "templates" / "_tokens.json", {}) or {}).items() if v})
    w, h = (1080, 1080) if args.square else (1080, 1350)
    rates = [r for r in data.get("rates", []) if str(r.get("value", "")).strip()]
    prices = [p for p in data.get("prices", []) if str(p.get("value", "")).strip()]
    if not rates and not prices:
        sys.exit("aucune donnée renseignée dans knowledge/donnees-marche.json")
    problems = [("%s" % (r.get("label") or r.get("city"))) for r in rates + prices if not (r.get("source") and r.get("date"))]
    if problems:
        sys.exit("REFUS : chiffres sans source ou sans date : %s" % ", ".join(problems))
    if not data.get("month"):
        sys.exit("REFUS : champ month vide (ex. « septembre 2026 »)")
    pad = int(w * 0.08)
    css = """
    @page { size: %dpx %dpx; margin: 0; } html,body{margin:0;padding:0}
    .s{width:%dpx;height:%dpx;box-sizing:border-box;padding:%dpx;background:%s;color:%s;font-family:%s;position:relative;overflow:hidden}
    .k{font-size:32px;letter-spacing:2px;text-transform:uppercase;color:%s;font-weight:bold;margin-bottom:24px}
    h1{font-family:%s;font-size:66px;line-height:1.1;margin:0 0 36px 0}
    .row{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid rgba(0,0,0,.08);padding:18px 0}
    .lab{font-size:38px} .val{font-family:%s;font-size:60px;font-weight:700;color:%s} .unit{font-size:30px;color:%s;margin-left:8px}
    .src{font-size:24px;color:%s;margin-top:6px} .sec{font-size:30px;color:%s;text-transform:uppercase;letter-spacing:1px;margin:40px 0 8px 0}
    .foot{position:absolute;left:%dpx;right:%dpx;bottom:%dpx;font-size:28px;color:%s;line-height:1.35} .foot .b{font-weight:700;letter-spacing:2px;display:block;margin-bottom:6px}
    .note{font-size:26px;color:%s;margin-top:24px}
    """ % (w, h, w, h, pad, tokens["color_secondary"], tokens["color_text"], tokens["font_body"], tokens["color_accent"], tokens["font_title"],
           tokens["font_title"], tokens["color_primary"], tokens["color_muted"], tokens["color_muted"], tokens["color_muted"], pad, pad, pad, tokens["color_muted"], tokens["color_muted"])
    out = ["<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\"><style>%s</style></head><body><section class=\"s\">" % css]
    out.append("<div class=\"k\">Repères du mois · %s</div><h1>Taux de crédit et prix du neuf</h1>" % html.escape(data["month"]))
    if rates:
        out.append("<div class=\"sec\">Taux moyens</div>")
        for r in rates:
            out.append("<div class=\"row\"><span class=\"lab\">%s</span><span><span class=\"val\">%s</span><span class=\"unit\">%s</span></span></div><div class=\"src\">%s, %s</div>"
                       % (html.escape(r["label"]), html.escape(str(r["value"])), html.escape(r.get("unit", "")), html.escape(r["source"]), html.escape(r["date"])))
    if prices:
        out.append("<div class=\"sec\">Prix du neuf</div>")
        for p in prices:
            out.append("<div class=\"row\"><span class=\"lab\">%s</span><span><span class=\"val\">%s</span><span class=\"unit\">%s</span></span></div><div class=\"src\">%s, %s</div>"
                       % (html.escape(p["city"]), html.escape(str(p["value"])), html.escape(p.get("unit", "")), html.escape(p["source"]), html.escape(p["date"])))
    if data.get("note"):
        out.append("<div class=\"note\">%s</div>" % html.escape(data["note"]))
    out.append("<div class=\"foot\"><span class=\"b\">%s</span>Relevé %s. L'investissement immobilier comporte des risques ; vérifiez votre situation avec un professionnel.</div>" % (html.escape(tokens["brand_name"]), html.escape(data["month"])))
    out.append("</section></body></html>")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(out), encoding="utf-8")
    print("→ %s (%dx%d, %d taux, %d prix)" % (args.out, w, h, len(rates), len(prices)))


if __name__ == "__main__":
    main()
