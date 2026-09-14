#!/usr/bin/env python3
"""Transcribe a video with ElevenLabs Scribe (word-level, verbatim).

Extracts mono 16k audio, uploads to Scribe, writes word-level JSON next to the
video (<stem>.words.json) — precise per-word timings for caption sync.

  ELEVENLABS_API_KEY=... python3 transcribe.py <video> [--language fr] [--model scribe_v1] [--out words.json]

Key in env, or a .env in cwd / this dir with ELEVENLABS_API_KEY=...
"""
import argparse, json, os, subprocess, sys, tempfile, time, uuid, urllib.request, urllib.error

def load_key():
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"]
    for p in [os.path.join(os.getcwd(), ".env"), os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")]:
        if os.path.exists(p):
            for line in open(p):
                if line.strip().startswith("ELEVENLABS_API_KEY"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("ELEVENLABS_API_KEY not found (env or .env)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--language", default=None, help="e.g. fr, en (auto if omitted)")
    ap.add_argument("--model", default="scribe_v1", help="Scribe model id (default scribe_v1)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    key = load_key()
    out = a.out or os.path.splitext(a.video)[0] + ".words.json"

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        try:
            subprocess.run(["ffmpeg", "-y", "-i", a.video, "-vn", "-ac", "1", "-ar", "16000",
                            "-c:a", "pcm_s16le", wav], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            sys.exit(f"ffmpeg failed: {(e.stderr or '')[-800:]}")
        # multipart upload (unique boundary per request avoids any collision with WAV bytes)
        boundary = "----supermonteur-" + uuid.uuid4().hex
        fields = {"model_id": a.model, "timestamps_granularity": "word"}
        if a.language:
            fields["language_code"] = a.language
        body = b""
        for k, v in fields.items():
            body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\n"
                 "Content-Type: audio/wav\r\n\r\n").encode()
        body += open(wav, "rb").read() + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", data=body,
            headers={"xi-api-key": key, "Content-Type": f"multipart/form-data; boundary={boundary}"})
        resp = None
        for attempt in range(3):
            try:
                resp = json.loads(urllib.request.urlopen(req, timeout=600).read())
                break
            except urllib.error.HTTPError as e:
                sys.exit(f"Scribe error {e.code}: {e.read().decode(errors='replace')[:300]}")
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 2:
                    sys.exit(f"Scribe network error after 3 attempts: {e}")
                time.sleep(2 ** attempt)

    words = [{"text": w["text"], "start": w["start"], "end": w["end"]}
             for w in resp.get("words", [])
             if w.get("type", "word") == "word" and all(k in w for k in ("text", "start", "end")) and str(w["text"]).strip()]
    if not words:
        sys.exit("Scribe returned no usable words (check audio / language).")
    json.dump({"language": resp.get("language_code"), "text": resp.get("text", ""), "words": words},
              open(out, "w"), ensure_ascii=False, indent=1)
    print(f"{len(words)} words -> {out}")

if __name__ == "__main__":
    main()
