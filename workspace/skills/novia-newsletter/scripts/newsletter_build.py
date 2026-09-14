#!/usr/bin/env python3
"""Construit une newsletter HTML email-safe (tables, CSS inline, 640 px) et sa version texte."""
import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "novia-outbox" / "scripts"))
from novia_common import find_workspace, read_json  # noqa: E402

DEFAULT_TOKENS = {"color_primary": "#1F3A5F", "color_secondary": "#F4F1EA", "color_accent": "#B88B2C", "color_text": "#1A1A1A",
                  "color_muted": "#5B6470", "font_title": "Georgia, 'Times New Roman', serif", "font_body": "Arial, Helvetica, sans-serif", "brand_name": "IMMO9"}
RISK = "L'investissement immobilier comporte des risques (vacance locative, évolution des prix, fiscalité susceptible de changer). Vérifiez votre situation personnelle avec un professionnel."


def esc(s):
    return html.escape(str(s or ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    args = ap.parse_args()
    ws = find_workspace()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    t = dict(DEFAULT_TOKENS)
    t.update({k: v for k, v in (read_json(ws / "templates" / "_tokens.json", {}) or {}).items() if v})
    subject = spec.get("subject", "")
    if not 10 <= len(subject) <= 60:
        sys.exit("REFUS : objet de %d caractères (viser 35 à 50)" % len(subject))
    if subject.isupper() or "urgent" in subject.lower():
        sys.exit("REFUS : objet en majuscules ou avec « urgent »")
    footer = spec.get("footer", {})
    if not footer.get("unsubscribe_url") or not footer.get("address"):
        sys.exit("REFUS : footer.unsubscribe_url et footer.address sont obligatoires")
    sections = spec.get("sections", [])
    if not 1 <= len(sections) <= 4:
        sys.exit("REFUS : 1 à 4 sections")
    body_text = " ".join([spec.get("intro", "")] + [s.get("body", "") for s in sections]).lower()
    if spec.get("persona") == "P2" and "risque" not in body_text:
        spec["risk_note"] = RISK
    p = "font-family:%s;font-size:16px;line-height:1.55;color:%s;margin:0 0 14px 0;" % (t["font_body"], t["color_text"])
    h2 = "font-family:%s;font-size:22px;line-height:1.3;color:%s;margin:24px 0 10px 0;" % (t["font_title"], t["color_primary"])
    parts = ["<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\"><title>%s</title></head>" % esc(subject),
             "<body style=\"margin:0;padding:0;background:%s;\">" % t["color_secondary"],
             "<div style=\"display:none;max-height:0;overflow:hidden;\">%s</div>" % esc(spec.get("preheader", "")),
             "<table role=\"presentation\" width=\"100%%\" cellpadding=\"0\" cellspacing=\"0\" style=\"background:%s;\"><tr><td align=\"center\" style=\"padding:24px 12px;\">" % t["color_secondary"],
             "<table role=\"presentation\" width=\"640\" cellpadding=\"0\" cellspacing=\"0\" style=\"max-width:640px;width:100%%;background:#ffffff;\">",
             "<tr><td style=\"background:%s;padding:22px 32px;font-family:%s;font-size:24px;font-weight:bold;color:#ffffff;\">%s</td></tr>" % (t["color_primary"], t["font_title"], esc(spec.get("header") or t["brand_name"])),
             "<tr><td style=\"padding:28px 32px 8px 32px;\">"]
    parts.append("<h1 style=\"font-family:%s;font-size:28px;line-height:1.25;color:%s;margin:0 0 18px 0;\">%s</h1>" % (t["font_title"], t["color_primary"], esc(spec.get("title") or subject)))
    for para in str(spec.get("intro", "")).split("\n\n"):
        if para.strip():
            parts.append("<p style=\"%s\">%s</p>" % (p, esc(para.strip())))
    for s in sections:
        parts.append("<h2 style=\"%s\">%s</h2>" % (h2, esc(s.get("title", ""))))
        for para in str(s.get("body", "")).split("\n\n"):
            if para.strip():
                parts.append("<p style=\"%s\">%s</p>" % (p, esc(para.strip())))
        if s.get("link"):
            parts.append("<p style=\"%s\"><a href=\"%s\" style=\"color:%s;font-weight:bold;\">%s</a></p>" % (p, esc(s["link"]), t["color_accent"], esc(s.get("link_label") or s["link"])))
    if spec.get("risk_note"):
        parts.append("<p style=\"%sfont-size:13px;color:%s;\">%s</p>" % (p, t["color_muted"], esc(spec["risk_note"])))
    sig = spec.get("signature", {})
    if sig:
        parts.append("<p style=\"%s\">%s<br><span style=\"color:%s;\">%s</span></p>" % (p, esc(sig.get("name", "")), t["color_muted"], esc(sig.get("role", ""))))
    parts.append("</td></tr><tr><td style=\"padding:18px 32px 28px 32px;font-family:%s;font-size:12px;line-height:1.5;color:%s;border-top:1px solid #e6e6e6;\">%s · %s<br>Vous recevez cet email parce que vous avez accepté de recevoir les informations d'IMMO9. <a href=\"%s\" style=\"color:%s;\">Se désinscrire</a></td></tr>"
                 % (t["font_body"], t["color_muted"], esc(t["brand_name"]), esc(footer["address"]), esc(footer["unsubscribe_url"]), t["color_muted"]))
    parts.append("</table></td></tr></table></body></html>")
    out_dir = Path(args.spec).resolve().parent
    (out_dir / "newsletter.html").write_text("\n".join(parts), encoding="utf-8")
    txt = [subject, "", spec.get("intro", "")]
    for s in sections:
        txt += ["", s.get("title", "").upper(), s.get("body", "")] + ([s["link"]] if s.get("link") else [])
    if spec.get("risk_note"):
        txt += ["", spec["risk_note"]]
    txt += ["", "%s · %s" % (t["brand_name"], footer["address"]), "Se désinscrire : %s" % footer["unsubscribe_url"]]
    (out_dir / "newsletter.txt").write_text("\n".join(txt), encoding="utf-8")
    print("→ %s et newsletter.txt (%d sections, persona %s)" % (out_dir / "newsletter.html", len(sections), spec.get("persona")))


if __name__ == "__main__":
    main()
