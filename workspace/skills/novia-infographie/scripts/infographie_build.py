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
    if len(rates) > 4 or len(prices) > 6:
        sys.exit("REFUS : au plus 4 taux et 6 prix par infographie (ici %d et %d) ; faire deux visuels" % (len(rates), len(prices)))
    css = """
    @page { size: %(w)dpx %(h)dpx; margin: 0; } html,body{margin:0;padding:0}
    .s{width:%(w)dpx;height:%(h)dpx;box-sizing:border-box;padding:%(pad)dpx %(pad)dpx %(foot)dpx %(pad)dpx;background:%(bg)s;color:%(text)s;font-family:%(fb)s;position:relative;overflow:hidden}
    .k{font-size:28px;letter-spacing:2px;text-transform:uppercase;color:%(accent)s;font-weight:bold;margin-bottom:14px}
    h1{font-family:%(ft)s;font-size:58px;line-height:1.08;margin:0 0 22px 0}
    .sec{font-size:24px;color:%(muted)s;text-transform:uppercase;letter-spacing:1px;margin:18px 0 4px 0}
    .row{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid rgba(0,0,0,.08);padding:10px 0 4px 0}
    .lab{font-size:32px} .val{font-family:%(ft)s;font-size:50px;font-weight:700;color:%(primary)s} .unit{font-size:24px;color:%(muted)s;margin-left:6px}
    .src{font-size:20px;color:%(muted)s;margin:2px 0 6px 0}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 28px;margin-top:6px}
    .card{border-bottom:2px solid rgba(0,0,0,.08);padding:8px 0 4px 0}
    .card .city{font-size:28px} .card .val{font-size:42px} .card .unit{font-size:20px} .card .src{font-size:18px;margin-bottom:2px}
    .note{font-size:22px;color:%(muted)s;margin-top:14px}
    .foot{position:absolute;left:%(pad)dpx;right:%(pad)dpx;bottom:%(padb)dpx;font-size:22px;color:%(muted)s;line-height:1.3}
    .foot .b{font-weight:700;letter-spacing:2px;display:block;margin-bottom:4px;color:%(primary)s}
    """ % {"w": w, "h": h, "pad": pad, "foot": int(h * 0.16), "padb": int(pad * 0.6), "bg": tokens["color_secondary"], "text": tokens["color_text"], "fb": tokens["font_body"],
           "ft": tokens["font_title"], "accent": tokens["color_accent"], "muted": tokens["color_muted"], "primary": tokens["color_primary"]}
    out = ["<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\"><style>%s</style></head><body><section class=\"s\">" % css]
    out.append("<div class=\"k\">Repères du mois · %s</div><h1>Taux de crédit et prix du neuf</h1>" % html.escape(data["month"]))
    if rates:
        out.append("<div class=\"sec\">Taux moyens</div>")
        for r in rates:
            out.append("<div class=\"row\"><span class=\"lab\">%s</span><span><span class=\"val\">%s</span><span class=\"unit\">%s</span></span></div><div class=\"src\">%s, %s</div>"
                       % (html.escape(r["label"]), html.escape(str(r["value"])), html.escape(r.get("unit", "")), html.escape(r["source"]), html.escape(r["date"])))
    if prices:
        out.append("<div class=\"sec\">Prix du neuf</div><div class=\"grid\">")
        for p in prices:
            out.append("<div class=\"card\"><div class=\"city\">%s</div><div><span class=\"val\">%s</span><span class=\"unit\">%s</span></div><div class=\"src\">%s, %s</div></div>"
                       % (html.escape(p["city"]), html.escape(str(p["value"])), html.escape(p.get("unit", "")), html.escape(p["source"]), html.escape(p["date"])))
        out.append("</div>")
    if data.get("note"):
        out.append("<div class=\"note\">%s</div>" % html.escape(data["note"]))
    out.append("<div class=\"foot\"><span class=\"b\">%s</span>Relevé %s. L'investissement immobilier comporte des risques ; vérifiez votre situation avec un professionnel.</div>" % (html.escape(tokens["brand_name"]), html.escape(data["month"])))
    out.append("</section></body></html>")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(out), encoding="utf-8")
    print("→ %s (%dx%d, %d taux, %d prix)" % (args.out, w, h, len(rates), len(prices)))


if __name__ == "__main__":
    main()
