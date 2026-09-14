"""Adaptateur YouTube Data API v3 : dépôt d'une vidéo (privée par défaut) avec titre et description.

Prérequis (voir connectors/README.md) :
- projet Google Cloud avec YouTube Data API v3 activée, identifiants OAuth « application de bureau »,
  jeton de rafraîchissement obtenu une fois pour la chaîne IMMO9 ;
- variables YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN ;
- réglages state/channels.json : {"adapter": "youtube", "privacy": "private|unlisted|public", "category_id": "22"}.
Quota : un dépôt coûte 1 600 unités sur les 10 000 quotidiennes par défaut.
"""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _http import require_env, request_json  # noqa: E402


def _access_token():
    data = urllib.parse.urlencode({
        "client_id": require_env("YOUTUBE_CLIENT_ID"), "client_secret": require_env("YOUTUBE_CLIENT_SECRET"),
        "refresh_token": require_env("YOUTUBE_REFRESH_TOKEN"), "grant_type": "refresh_token"}).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["access_token"]


def publish(channel, settings, caption, assets, manifest):
    videos = [a for a in assets if a.lower().endswith((".mp4", ".mov"))]
    if not videos:
        raise RuntimeError("YouTube exige un fichier vidéo")
    token = _access_token()
    title = (manifest.get("title") or "Vidéo IMMO9")[:100]
    meta = {"snippet": {"title": title, "description": caption, "categoryId": settings.get("category_id", "22")},
            "status": {"privacyStatus": settings.get("privacy", "private"), "selfDeclaredMadeForKids": False}}
    init = urllib.request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        data=json.dumps(meta).encode("utf-8"), method="POST",
        headers={"Authorization": "Bearer %s" % token, "Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Type": "video/*"})
    with urllib.request.urlopen(init, timeout=60) as resp:
        upload_url = resp.headers["Location"]
    with open(videos[0], "rb") as f:
        req = urllib.request.Request(upload_url, data=f.read(), method="PUT", headers={"Authorization": "Bearer %s" % token, "Content-Type": "video/*"})
        with urllib.request.urlopen(req, timeout=1800) as resp:
            res = json.loads(resp.read().decode("utf-8"))
    vid = res.get("id")
    return {"id": vid, "url": ("https://www.youtube.com/watch?v=%s" % vid) if vid else None, "raw": {"privacy": meta["status"]["privacyStatus"]}}
