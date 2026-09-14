#!/usr/bin/env python3
"""Construit les slides HTML d'un carrousel à partir d'un JSON et des tokens de charte."""
import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, read_json  # noqa: E402

DEFAULT_TOKENS = {
    "color_primary": "#1F3A5F", "color_secondary": "#F4F1EA", "color_accent": "#B88B2C",
    "color_text": "#1A1A1A", "color_muted": "#5B6470", "font_title": "Georgia, 'Times New Roman', serif",
    "font_body": "Arial, Helvetica, sans-serif", "logo_path": "", "brand_name": "IMMO9",
}

CSS = """
@page { size: %(w)spx %(h)spx; margin: 0; }
html, body { margin: 0; padding: 0; }
.slide { width: %(w)spx; height: %(h)spx; box-sizing: border-box; padding: %(pad)spx; position: relative;
  background: %(bg)s; color: %(text)s; font-family: %(font_body)s; overflow: hidden; page-break-after: always; }
.slide.cover, .slide.last { background: %(primary)s; color: #ffffff; }
.kicker { font-size: 34px; letter-spacing: 2px; text-transform: uppercase; color: %(accent)s; margin-bottom: 36px; font-weight: bold; }
.slide.cover .kicker, .slide.last .kicker { color: %(secondary)s; }
h1 { font-family: %(font_title)s; font-size: 72px; line-height: 1.12; margin: 0 0 40px 0; font-weight: 700; }
.slide.cover h1 { font-size: 88px; }
p.body { font-size: 44px; line-height: 1.38; margin: 0 0 28px 0; }
.source { position: absolute; left: %(pad)spx; right: %(pad)spx; bottom: 150px; font-size: 28px; color: %(muted)s; }
.slide.cover .source, .slide.last .source { color: %(secondary)s; }
.footer { position: absolute; left: %(pad)spx; right: %(pad)spx; bottom: %(pad)spx; display: flex; justify-content: space-between; align-items: center; font-size: 30px; color: %(muted)s; }
.slide.cover .footer, .slide.last .footer { color: %(secondary)s; }
.brand { font-family: %(font_title)s; font-weight: 700; letter-spacing: 1px; }
.brand img { height: 64px; }
.num { font-variant-numeric: tabular-nums; }
"""


def render_slide(i, total, s, tokens, w, h, footer):
    cls = "slide" + (" cover" if s.get("cover") else "") + (" last" if s.get("last") else "")
    kicker = s.get("kicker") or footer.get("kicker") or ""
    brand = footer.get("brand") or tokens["brand_name"]
    logo = tokens.get("logo_path")
    if logo and not str(logo).startswith(("http://", "https://", "file://", "data:")):
        logo = (tokens["_ws"] / logo).resolve().as_uri() if not Path(logo).is_absolute() else Path(logo).as_uri()
    brand_html = "<img src=\"%s\" alt=\"%s\">" % (html.escape(str(logo)), html.escape(brand)) if logo else html.escape(brand)
    parts = ["<section class=\"%s\">" % cls]
    if kicker:
        parts.append("<div class=\"kicker\">%s</div>" % html.escape(kicker))
    parts.append("<h1>%s</h1>" % html.escape(s.get("title", "")))
    for para in str(s.get("body", "")).split("\n\n"):
        if para.strip():
            parts.append("<p class=\"body\">%s</p>" % html.escape(para.strip()).replace("\n", "<br>"))
    src = s.get("source") or (footer.get("source") if (s.get("last") or s.get("cover")) else "")
    if src:
        parts.append("<div class=\"source\">%s</div>" % html.escape(src))
    parts.append("<div class=\"footer\"><span class=\"brand\">%s</span><span class=\"num\">%d / %d</span></div>" % (brand_html, i, total))
    parts.append("</section>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="JSON du carrousel")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1350)
    args = ap.parse_args()
    ws = find_workspace()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    tokens = dict(DEFAULT_TOKENS)
    tokens.update({k: v for k, v in (read_json(ws / "templates" / "_tokens.json", {}) or {}).items() if v})
    tokens["_ws"] = ws
    slides = spec.get("slides", [])
    if not 5 <= len(slides) <= 8:
        sys.exit("un carrousel a entre 5 et 8 slides (ici %d)" % len(slides))
    footer = spec.get("footer", {})
    if spec.get("kicker") and "kicker" not in footer:
        footer["kicker"] = spec["kicker"]
    w, h = args.width, args.height
    css = CSS % {"w": w, "h": h, "pad": int(w * 0.08), "bg": tokens["color_secondary"], "text": tokens["color_text"],
                 "primary": tokens["color_primary"], "secondary": tokens["color_secondary"], "accent": tokens["color_accent"],
                 "muted": tokens["color_muted"], "font_title": tokens["font_title"], "font_body": tokens["font_body"]}
    out_dir = Path(args.spec).resolve().parent
    slides_dir = out_dir / "slides"
    slides_dir.mkdir(exist_ok=True)
    for old in slides_dir.glob("slide-*.html"):  # anciennes slides d'une construction précédente
        old.unlink()
    for old in slides_dir.glob("slide-*.png"):
        old.unlink()
    head = "<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\"><title>%s</title><style>%s</style></head><body>" % (html.escape(spec.get("id", "carrousel")), css)
    all_html = [head]
    for i, s in enumerate(slides, 1):
        body = render_slide(i, len(slides), s, tokens, w, h, footer)
        (slides_dir / ("slide-%02d.html" % i)).write_text(head + body + "</body></html>", encoding="utf-8")
        all_html.append(body)
    all_html.append("</body></html>")
    (out_dir / "carousel.html").write_text("\n".join(all_html), encoding="utf-8")
    print("%d slides → %s et %s" % (len(slides), out_dir / "carousel.html", slides_dir))


if __name__ == "__main__":
    main()
