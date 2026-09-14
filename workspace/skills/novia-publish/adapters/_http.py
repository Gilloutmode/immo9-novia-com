"""Petit client HTTP stdlib partagé par les adaptateurs (JSON et multipart)."""
import json
import mimetypes
import os
import urllib.request
import uuid


def require_env(name):
    v = os.environ.get(name)
    if not v:
        raise RuntimeError("variable d'environnement manquante : %s (à déclarer dans skills.entries.novia-publish.env)" % name)
    return v


def request_json(method, url, headers=None, data=None, timeout=60):
    body = None
    h = {"Accept": "application/json"}
    h.update(headers or {})
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


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
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}
