/**
 * supermonteur : build an animated-caption HyperFrames composition from a cam video + Scribe words.
 * Full-screen cam + word-by-word captions with the spoken word highlighted. Clean, readable,
 * social-safe, ready to post.
 *
 *   node build.mjs --cam clip.mp4 --words clip.words.json --out index.html [--accent "#28e0a8"]
 *
 * Then render with hyperframes:  npx hyperframes render . -q high
 */
import { readFileSync, writeFileSync, copyFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => {
  if (v.startsWith("--")) a.push([v.slice(2), arr[i + 1]]); return a;
}, []));
const cam = args.cam, wordsPath = args.words;
const out = args.out || "index.html";
const accent = args.accent || "#28e0a8";          // active-word colour (change to taste)
if (!cam || !wordsPath) { console.error("usage: --cam <mp4> --words <json> [--out] [--accent]"); process.exit(1); }
if (!/^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(accent)) { console.error(`--accent invalide: ${accent} (attendu #rgb ou #rrggbb)`); process.exit(1); }

// Escape for HTML text + attributes : keep UTF-8 accents/emoji intact, only neutralise markup chars.
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// Probe duration without a shell (path may contain spaces/quotes → avoids breakage + shell injection).
let dur;
try {
  dur = +execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", cam], { encoding: "utf8" }).trim();
  if (!Number.isFinite(dur) || dur <= 0) throw new Error("durée invalide");
} catch (e) { console.error(`ffprobe a échoué pour ${cam}: ${e.message}`); process.exit(1); }

// Load words; drop malformed timings, sort, clamp overlaps so highlights never collide.
const raw = JSON.parse(readFileSync(wordsPath, "utf8")).words ?? [];
const W = raw.map(w => ({ t: +w.start, e: +w.end, text: String(w.text ?? "").trim() }))
             .filter(w => w.text && Number.isFinite(w.t) && Number.isFinite(w.e) && w.e > w.t)
             .sort((a, b) => a.t - b.t);
for (let i = 0; i < W.length - 1; i++) W[i].e = Math.min(W[i].e, W[i + 1].t);
if (W.length === 0) { console.error(`Aucun mot exploitable dans ${wordsPath} : transcription vide ?`); process.exit(1); }

// Visual width estimate: uppercase + wide glyphs (MW@#%) + emoji cost more than 1 char → truer line breaks.
const vis = s => [...s.toUpperCase()].reduce((n, ch) => n + (/\p{Emoji}/u.test(ch) ? 2 : /[MW@#%]/.test(ch) ? 1.6 : 1), 0);
const MAX_VIS = 22;

// group into lines: <=4 words AND <=~22 visual units, break on sentence end or pause >0.5s
const lines = [];
let cur = [];
for (let i = 0; i < W.length; i++) {
  cur.push(W[i]);
  const width = vis(cur.map(w => w.text).join(" "));
  const next = W[i + 1];
  const gap = next ? next.t - W[i].e : Infinity;
  const endsSent = /[.!?]$/.test(W[i].text);
  if (endsSent || cur.length >= 4 || width >= MAX_VIS || gap > 0.5 || !next) { lines.push(cur); cur = []; }
}

// caption DOM + timeline ops
const FRAME = 1 / 25;                               // render fps : keep every animation duration >= 1 frame
let blocksHtml = "", ops = "";
lines.forEach((line, li) => {
  const start = line[0].t, end = Math.min(line[line.length - 1].e + 0.4, (lines[li + 1]?.[0].t ?? dur));
  const words = line.map((w, wi) => `<span class="cw" id="l${li}w${wi}">${esc(w.text)}</span>`).join(" ");
  blocksHtml += `<div class="cap" id="l${li}">${words}</div>\n`;
  // line in/out: slide-up + fade with easing (premium feel, still deterministic)
  ops += `tl.set("#l${li}",{opacity:0,y:18,scale:0.98},0);`
       + `tl.to("#l${li}",{opacity:1,y:0,scale:1,duration:0.16,ease:"power2.out"},${start.toFixed(3)});`
       + `tl.to("#l${li}",{opacity:0,y:-10,duration:0.12,ease:"power1.in"},${end.toFixed(3)});`;
  // active-word highlight: colour + subtle pop, released before the next word lights up
  line.forEach((w, wi) => {
    const nx = line[wi + 1];
    const off = Math.max(w.t + FRAME, Math.min(w.e + 0.05, nx ? nx.t - 0.005 : w.e + 0.05));
    ops += `tl.set("#l${li}w${wi}",{color:"#fff",scale:1},0);`
         + `tl.to("#l${li}w${wi}",{color:"${accent}",scale:1.06,duration:0.06,ease:"power1.out"},${w.t.toFixed(3)});`
         + `tl.to("#l${li}w${wi}",{color:"#fff",scale:1,duration:0.08,ease:"power1.in"},${off.toFixed(3)});`;
  });
});

// Copy vendored GSAP next to the output so the render is offline + deterministic. Loaded via
// <script src> rather than inlined : inlining would expose GSAP's internal Math.random() to the linter.
const GSAP_FILE = "gsap-3.14.2.min.js";
copyFileSync(join(dirname(fileURLToPath(import.meta.url)), "vendor", GSAP_FILE), join(dirname(out) || ".", GSAP_FILE));
const camSrc = esc(cam);

const html = `<!doctype html><html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=1080, height=1920"/>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:1080px;height:1920px;background:#000;overflow:hidden;font-family:"Montserrat","Inter",system-ui,sans-serif}
  #root{position:relative;width:1080px;height:1920px;background:#000;overflow:hidden}
  #cam{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
  /* captions anchored from the BOTTOM of the safe zone (bottom:430 keeps them above TikTok/Reels UI ~320-340px) */
  #caps{position:absolute;left:60px;right:60px;bottom:430px;text-align:center;z-index:10}
  .cap{position:absolute;left:0;right:0;bottom:0;opacity:0;will-change:opacity,transform}
  .cw{display:inline-block;font-weight:800;font-size:78px;line-height:1.14;color:#fff;letter-spacing:0.5px;
      text-transform:uppercase;overflow-wrap:anywhere;
      text-shadow:0 4px 0 rgba(0,0,0,.7),0 0 26px rgba(0,0,0,.9);
      -webkit-text-stroke:4px rgba(0,0,0,.6);will-change:color,transform}
</style></head>
<body>
  <div id="root" data-composition-id="root" data-start="0" data-duration="${dur.toFixed(2)}" data-width="1080" data-height="1920" data-fps="25">
    <video id="cam" class="clip" src="${camSrc}" muted playsinline preload="auto" data-start="0" data-duration="${dur.toFixed(2)}" data-track-index="0" data-has-audio="false"></video>
    <audio id="cam-audio" class="clip" src="${camSrc}" data-start="0" data-duration="${dur.toFixed(2)}" data-track-index="1" data-volume="1"></audio>
    <div id="caps">
      ${blocksHtml}
    </div>
  </div>
  <script src="${GSAP_FILE}"></script>
  <script>
    window.__timelines = window.__timelines || {};
    var tl = gsap.timeline({paused:true});
    ${ops}
    tl.to({},{duration:${dur.toFixed(2)}},0);
    window.__timelines["root"] = tl;
  </script>
</body></html>`;

writeFileSync(out, html);
console.log(`${W.length} words · ${lines.length} caption lines · ${dur.toFixed(1)}s -> ${out}`);
