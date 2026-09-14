"""Petit client HTTP stdlib partagé par les adaptateurs (JSON et multipart).

Deux familles d'erreurs, et une seule règle : tout ce qui n'est pas prouvé sans effet distant est une issue inconnue.
- PreflightError : levée AVANT tout appel réseau (variable ou réglage manquant, fichier absent) ; aucune tentative n'est partie.
- RemoteRejected : le serveur a répondu et refusé explicitement (4xx, success false) ; rien n'a été publié.
Toute autre exception (timeout, réseau, 5xx, réponse illisible après un appel) laisse une tentative d'issue inconnue.
"""
import json
import mimetypes
import os
import urllib.error
import urllib.request
import uuid


class PreflightError(RuntimeError):
    """Échec certain avant envoi : rien n'est parti."""


class RemoteRejected(RuntimeError):
    """Refus explicite du serveur : rien n'a été publié."""


def require_env(name):
    v = os.environ.get(name)
    if not v:
        raise PreflightError("variable d'environnement manquante : %s (à déclarer dans skills.entries.novia-publish.env)" % name)
    return v


def _open(req, timeout):
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        if 400 <= e.code < 500:
            body = ""
            try:
                body = e.read().decode("utf-8", "ignore")[:300]
            except Exception:
                pass
            raise RemoteRejected("HTTP %s : %s" % (e.code, body or e.reason))
        raise


def request_json(method, url, headers=None, data=None, timeout=60):
    body = None
    h = {"Accept": "application/json"}
    h.update(headers or {})
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    with _open(req, timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}  # une réponse illisible après envoi = issue inconnue (ValueError non certain)


def request_multipart(url, fields, files, headers=None, timeout=300):
    """fields: dict ou liste de (nom, valeur) ; files: liste de (nom_champ, chemin)."""
    boundary = "----novia" + uuid.uuid4().hex
    parts = []
    items = fields.items() if isinstance(fields, dict) else fields
    for k, v in items:
        parts.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v)).encode("utf-8"))
    for field, path in files:
        name = os.path.basename(path)
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            content = f.read()
        parts.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n" % (boundary, field, name, ctype)).encode("utf-8"))
        parts.append(content)
        parts.append(b"\r\n")
    parts.append(("--%s--\r\n" % boundary).encode("utf-8"))
    body = b"".join(parts)
    h = {"Content-Type": "multipart/form-data; boundary=%s" % boundary, "Accept": "application/json"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, method="POST", headers=h)
    with _open(req, timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}
