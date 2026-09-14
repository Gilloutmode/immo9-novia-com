"""Adaptateur Brevo (ex-Sendinblue) : crée une campagne email à partir du HTML de la pièce, puis l'envoie.

Prérequis (voir connectors/README.md) :
- compte Brevo avec listes de contacts par persona et expéditeur vérifié ;
- variable BREVO_API_KEY ;
- réglages state/channels.json : {"adapter": "brevo", "sender": {"name": "IMMO9", "email": "news@…"},
  "list_ids": {"P1": [12], "P2": [13], "P3": [14], "P4": [15]}, "send": false}.
Avec "send": false, la campagne est créée en brouillon dans Brevo (l'équipe envoie depuis Brevo) ; avec true,
l'envoi est déclenché immédiatement après création.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _http import require_env, request_json, PreflightError, RemoteRejected  # noqa: E402

BASE = "https://api.brevo.com/v3"


def publish(channel, settings, caption, assets, manifest):
    key = require_env("BREVO_API_KEY")
    html = [a for a in assets if a.lower().endswith(".html")]
    if not html:
        raise PreflightError("newsletter : aucun fichier .html dans les assets de la pièce")
    sender = settings.get("sender") or {}
    if not sender.get("email"):
        raise PreflightError("réglage manquant : sender.email")
    lists = (settings.get("list_ids") or {}).get(manifest.get("persona"))
    if not lists:
        raise PreflightError("réglage manquant : list_ids.%s" % manifest.get("persona"))
    with open(html[0], "r", encoding="utf-8") as f:
        content = f.read()
    subject = (manifest.get("captions", {}).get("subject") or manifest.get("title") or "IMMO9")[:120]
    payload = {"name": "%s %s" % (manifest["id"], manifest.get("title", ""))[:100], "subject": subject,
               "sender": sender, "htmlContent": content, "recipients": {"listIds": lists}}
    res = request_json("POST", BASE + "/emailCampaigns", headers={"api-key": key}, data=payload)
    cid = res.get("id")
    if settings.get("send") and cid:
        request_json("POST", "%s/emailCampaigns/%s/sendNow" % (BASE, cid), headers={"api-key": key}, data={})
    return {"state": "published" if settings.get("send") and cid else "draft_remote", "id": cid, "url": None,
            "message": "campagne Brevo %s (%s)" % (cid, "envoyée" if settings.get("send") else "brouillon à envoyer depuis Brevo")}
