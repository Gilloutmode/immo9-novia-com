"""Adaptateur Meta Graph API : Instagram (compte professionnel) et Page Facebook.

Prérequis (voir connectors/README.md) :
- application Meta, compte Instagram professionnel lié à une Page Facebook, jeton de Page longue durée
  avec les permissions instagram_basic, instagram_content_publish, pages_manage_posts, pages_read_engagement ;
- variable META_PAGE_ACCESS_TOKEN ;
- réglages state/channels.json : {"adapter": "meta_graph", "ig_user_id": "1784…", "fb_page_id": "1234…",
  "public_base_url": "https://media.exemple.fr/novia"} ;
- Instagram exige une URL publique (HTTPS) pour chaque image ou vidéo : public_base_url doit servir le dossier outbox/
  (par exemple via nginx en lecture seule sur ce seul dossier). Sans cela, utiliser l'adaptateur upload_post.
Version d'API : GRAPH_VERSION ci-dessous, à aligner sur la version courante documentée par Meta.
"""
import os
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _http import require_env, request_json  # noqa: E402

GRAPH_VERSION = "v23.0"
BASE = "https://graph.facebook.com/%s" % GRAPH_VERSION


def _public_url(settings, asset_path, manifest):
    base = settings.get("public_base_url")
    if not base:
        raise RuntimeError("réglage manquant : public_base_url (Instagram exige une URL publique pour les médias)")
    rel = "%s/%s" % (manifest["id"], os.path.basename(asset_path))
    return base.rstrip("/") + "/" + urllib.parse.quote(rel)


def _post(url, params):
    q = urllib.parse.urlencode(params)
    return request_json("POST", url + "?" + q)


def publish(channel, settings, caption, assets, manifest):
    token = require_env("META_PAGE_ACCESS_TOKEN")
    if channel == "instagram":
        ig = settings.get("ig_user_id")
        if not ig:
            raise RuntimeError("réglage manquant : ig_user_id")
        if not assets:
            raise RuntimeError("Instagram exige au moins un média")
        images = [a for a in assets if not a.lower().endswith((".mp4", ".mov"))]
        videos = [a for a in assets if a.lower().endswith((".mp4", ".mov"))]
        if videos:
            container = _post("%s/%s/media" % (BASE, ig), {"media_type": "REELS", "video_url": _public_url(settings, videos[0], manifest), "caption": caption, "access_token": token})
        elif len(images) == 1:
            container = _post("%s/%s/media" % (BASE, ig), {"image_url": _public_url(settings, images[0], manifest), "caption": caption, "access_token": token})
        else:
            children = []
            for img in images[:10]:
                c = _post("%s/%s/media" % (BASE, ig), {"image_url": _public_url(settings, img, manifest), "is_carousel_item": "true", "access_token": token})
                children.append(c["id"])
            container = _post("%s/%s/media" % (BASE, ig), {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption, "access_token": token})
        pub = _post("%s/%s/media_publish" % (BASE, ig), {"creation_id": container["id"], "access_token": token})
        return {"id": pub.get("id"), "url": None, "raw": pub}
    if channel == "facebook":
        page = settings.get("fb_page_id")
        if not page:
            raise RuntimeError("réglage manquant : fb_page_id")
        images = [a for a in assets if not a.lower().endswith((".mp4", ".mov"))]
        if images:
            res = _post("%s/%s/photos" % (BASE, page), {"url": _public_url(settings, images[0], manifest), "message": caption, "access_token": token})
        else:
            res = _post("%s/%s/feed" % (BASE, page), {"message": caption, "access_token": token})
        pid = res.get("post_id") or res.get("id")
        return {"id": pid, "url": ("https://www.facebook.com/%s" % pid) if pid else None, "raw": res}
    raise RuntimeError("canal non géré par meta_graph : %s" % channel)
