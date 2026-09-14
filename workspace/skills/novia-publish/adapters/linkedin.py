"""Adaptateur LinkedIn (Page entreprise) : post texte ou texte + image via l'API Posts.

Prérequis (voir connectors/README.md) :
- application LinkedIn avec le produit Community Management API approuvé, jeton d'accès avec w_organization_social ;
- variable LINKEDIN_ACCESS_TOKEN ;
- réglages state/channels.json : {"adapter": "linkedin", "organization_urn": "urn:li:organization:123456"}.
La version d'API (en-tête LinkedIn-Version) évolue chaque mois : ajuster LINKEDIN_VERSION à l'installation.
"""
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _http import require_env, request_json, PreflightError, RemoteRejected  # noqa: E402

LINKEDIN_VERSION = "202509"


def _headers(token):
    return {"Authorization": "Bearer %s" % token, "LinkedIn-Version": LINKEDIN_VERSION, "X-Restli-Protocol-Version": "2.0.0"}


def _upload_image(token, owner, path):
    init = request_json("POST", "https://api.linkedin.com/rest/images?action=initializeUpload",
                        headers=_headers(token), data={"initializeUploadRequest": {"owner": owner}})
    value = init["value"]
    with open(path, "rb") as f:
        req = urllib.request.Request(value["uploadUrl"], data=f.read(), method="PUT", headers={"Authorization": "Bearer %s" % token})
        urllib.request.urlopen(req, timeout=300).read()
    return value["image"]


def publish(channel, settings, caption, assets, manifest):
    token = require_env("LINKEDIN_ACCESS_TOKEN")
    owner = settings.get("organization_urn")
    if not owner:
        raise PreflightError("réglage manquant : organization_urn")
    body = {"author": owner, "commentary": caption, "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False}
    if any(a.lower().endswith(".pdf") for a in assets):
        raise PreflightError("l'adaptateur linkedin natif ne gère pas les documents PDF ; utiliser upload_post (upload_document) ou publier le PDF manuellement")
    images = [a for a in assets if a.lower().endswith((".png", ".jpg", ".jpeg"))]
    if images:
        image_urn = _upload_image(token, owner, images[0])
        body["content"] = {"media": {"id": image_urn, "title": manifest.get("title", "")}}
    req = urllib.request.Request("https://api.linkedin.com/rest/posts", data=__import__("json").dumps(body).encode("utf-8"), method="POST",
                                 headers=dict(_headers(token), **{"Content-Type": "application/json"}))
    with urllib.request.urlopen(req, timeout=60) as resp:
        post_id = resp.headers.get("x-restli-id") or resp.headers.get("X-RestLi-Id")
    return {"state": "published" if post_id else "submitted", "id": post_id, "url": ("https://www.linkedin.com/feed/update/%s" % post_id) if post_id else None}
