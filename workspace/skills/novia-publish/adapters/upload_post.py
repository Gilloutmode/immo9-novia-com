"""Adaptateur upload-post.com : une clé, envoi de fichiers, publication multi-plateformes.

Prérequis (voir connectors/README.md) :
- compte upload-post.com avec les profils sociaux connectés ;
- variable UPLOAD_POST_API_KEY ;
- réglages dans state/channels.json : {"adapter": "upload_post", "user": "<nom du profil upload-post>", "platform": "instagram"}.
Les champs et l'URL de l'API sont ceux documentés par upload-post (https://docs.upload-post.com) ;
vérifier la documentation à l'installation, l'API évolue.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _http import require_env, request_multipart  # noqa: E402

BASE = "https://api.upload-post.com/api"
PLATFORM_MAP = {"instagram": "instagram", "facebook": "facebook", "linkedin": "linkedin", "youtube": "youtube", "tiktok": "tiktok"}


def publish(channel, settings, caption, assets, manifest):
    key = require_env("UPLOAD_POST_API_KEY")
    user = settings.get("user")
    if not user:
        raise RuntimeError("réglage manquant : channels.%s.user (profil upload-post)" % channel)
    platform = settings.get("platform") or PLATFORM_MAP.get(channel)
    if not platform:
        raise RuntimeError("plateforme upload-post inconnue pour le canal %s" % channel)
    if not assets:
        endpoint = BASE + "/upload_text"
        fields = [("user", user), ("platform[]", platform), ("title", caption)]
        files = []
    else:
        videos = [a for a in assets if a.lower().endswith((".mp4", ".mov"))]
        pdfs = [a for a in assets if a.lower().endswith(".pdf")]
        if pdfs:  # carrousel PDF (LinkedIn) : point d'entrée « document »
            endpoint = BASE + "/upload_document"
            fields = [("user", user), ("platform[]", platform), ("title", (manifest.get("title") or caption)[:100]), ("description", caption)]
            files = [("document", pdfs[0])]
        elif videos:
            endpoint = BASE + "/upload"
            fields = [("user", user), ("platform[]", platform), ("title", caption)]
            files = [("video", videos[0])]
        else:
            endpoint = BASE + "/upload_photos"
            fields = [("user", user), ("platform[]", platform), ("title", caption), ("caption", caption)]
            files = [("photos[]", a) for a in assets]
    res = request_multipart(endpoint, fields, files, headers={"Authorization": "Apikey %s" % key})
    # Réponse synchrone : succès par plateforme ; réponse asynchrone : request_id à suivre (Upload Status).
    per = res.get("results") or {}
    ok = bool(res.get("success")) or (isinstance(per, dict) and any(isinstance(v, dict) and v.get("success") for v in per.values()))
    state = "published" if ok else ("submitted" if res.get("request_id") else "submitted")
    url = None
    if isinstance(per, dict):
        for v in per.values():
            if isinstance(v, dict) and v.get("url"):
                url = v["url"]
    return {"state": state, "id": res.get("request_id") or res.get("id"), "url": url or res.get("url"), "raw": res}
