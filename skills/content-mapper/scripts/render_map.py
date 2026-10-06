#!/usr/bin/env python3
"""Render content-map.md as a standalone HTML page with a visual map.

Usage: render_map.py [content-map.md] [-o content-map.html]
"""
import argparse
import html
import math
import re
import sys
from pathlib import Path

ANGLES = {
    "pain point": "pain",
    "how-to": "howto",
    "how to": "howto",
    "lesson learned": "lesson",
    "lesson": "lesson",
    "why it matters": "why",
    "harsh truth": "truth",
    "opinion": "opinion",
    "opinion on a popular idea": "opinion",
}


def parse(text):
    m = {"a": "", "b": "", "mission": "", "topics": []}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        kv = re.match(r"\*\*(Point A|Point B|Mission):\*\*\s*(.*)", line)
        if kv:
            key = {"Point A": "a", "Point B": "b", "Mission": "mission"}[kv[1]]
            m[key] = kv[2].strip()
        elif line.startswith("### "):
            if not m["topics"]:
                sys.exit("Subtopic before any broad topic: " + line)
            m["topics"][-1]["subs"].append({"name": line[4:].strip(), "ideas": []})
        elif line.startswith("## "):
            m["topics"].append({"name": line[3:].strip(), "subs": []})
        elif line.startswith("- "):
            if not m["topics"] or not m["topics"][-1]["subs"]:
                sys.exit("Idea before any subtopic: " + line)
            idea = re.match(r"-\s*\[([^\]]+)\]\s*(.*)", line)
            angle, body = (idea[1].strip(), idea[2].strip()) if idea else ("", line[2:].strip())
            m["topics"][-1]["subs"][-1]["ideas"].append({"angle": angle, "text": body})
    if not m["topics"]:
        sys.exit("No broad topics (## headings) found.")
    return m


def esc(s):
    return html.escape(s, quote=True)


def slug(*parts):
    return "-".join(re.sub(r"[^a-z0-9]+", "-", p.lower()).strip("-") for p in parts)


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines or [""]


def svg_map(m):
    """Radial map: mission in the centre, territories on the inner ring, cities outside."""
    R1, R2, HALF = 165, 300, 450
    subs = [(ti, s) for ti, t in enumerate(m["topics"]) for s in t["subs"]]
    slots = max(len(subs), 3)
    # Leave a one-slot gap between territories so their cities do not touch.
    gaps = len(m["topics"])
    step = 2 * math.pi / (slots + gaps)
    out, cities, terr = [], [], []
    a = -math.pi / 2 - step * (len(m["topics"][0]["subs"]) - 1) / 2
    for ti, t in enumerate(m["topics"]):
        angs = []
        for s in t["subs"]:
            angs.append(a)
            a += step
        a += step
        ta = sum(angs) / len(angs) if angs else a
        tx, ty = R1 * math.cos(ta), R1 * math.sin(ta)
        terr.append((ti, t, tx, ty))
        out.append(f'<path class="link t{ti % 4}" d="M0 0 Q{tx * .5:.1f} {ty * .5 + 18:.1f} {tx:.1f} {ty:.1f}"/>')
        for ang, s in zip(angs, t["subs"]):
            cx, cy = R2 * math.cos(ang), R2 * math.sin(ang)
            mx, my = (R1 + 60) * math.cos(ang), (R1 + 60) * math.sin(ang)
            out.append(f'<path class="link t{ti % 4}" d="M{tx:.1f} {ty:.1f} Q{mx:.1f} {my:.1f} {cx:.1f} {cy:.1f}"/>')
            cities.append((ti, t, s, ang, cx, cy))
    for ti, t, s, ang, cx, cy in cities:
        right = math.cos(ang) >= -0.01
        lx = cx + (14 if right else -14)
        anchor = "start" if right else "end"
        lines = wrap(s["name"], 16)
        dy0 = 4 - (len(lines) - 1) * 8
        tspans = "".join(
            f'<tspan x="{lx:.1f}" dy="{dy0 if i == 0 else 16}">{esc(l)}</tspan>' for i, l in enumerate(lines)
        )
        n = len(s["ideas"])
        out.append(
            f'<a href="#{slug(t["name"], s["name"])}" class="city t{ti % 4}">'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7"/>'
            f'<text x="{lx:.1f}" y="{cy:.1f}" text-anchor="{anchor}">{tspans}</text>'
            f'<title>{esc(s["name"])}: {n} idea{"s" if n != 1 else ""}</title></a>'
        )
    for ti, t, tx, ty in terr:
        lines = wrap(t["name"].upper(), 14)
        w = max(len(l) for l in lines) * 9 + 28
        h = len(lines) * 16 + 16
        tspans = "".join(
            f'<tspan x="{tx:.1f}" dy="{4 - (len(lines) - 1) * 8 if i == 0 else 16}">{esc(l)}</tspan>'
            for i, l in enumerate(lines)
        )
        out.append(
            f'<a href="#{slug(t["name"])}" class="territory t{ti % 4}">'
            f'<rect x="{tx - w / 2:.1f}" y="{ty - h / 2:.1f}" width="{w}" height="{h}" rx="{h / 2:.1f}"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle">{tspans}</text></a>'
        )
    out.append('<circle class="north" cx="0" cy="0" r="54"/>')
    out.append('<text class="north-label" x="0" y="-6" text-anchor="middle">A → B</text>')
    out.append('<text class="north-sub" x="0" y="14" text-anchor="middle">MISSION</text>')
    return (
        f'<svg viewBox="{-HALF} {-R2 - 40} {2 * HALF} {2 * R2 + 80}" role="img" '
        f'aria-label="Content map: {len(m["topics"])} broad topics, {len(subs)} subtopics">'
        '<g class="rings"><circle r="165"/><circle r="300"/></g>' + "".join(out) + "</svg>"
    )


def ideas_html(m):
    cols = []
    for ti, t in enumerate(m["topics"]):
        subs = []
        for s in t["subs"]:
            items = "".join(
                f'<li><span class="tag {ANGLES.get(i["angle"].lower(), "other")}">{esc(i["angle"] or "idea")}</span>'
                f'<span class="idea">{esc(i["text"])}</span></li>'
                for i in s["ideas"]
            )
            subs.append(
                f'<section class="sub" id="{slug(t["name"], s["name"])}">'
                f'<h3><span class="pin t{ti % 4}"></span>{esc(s["name"])}</h3><ul>{items}</ul></section>'
            )
        cols.append(
            f'<article class="territory-col t{ti % 4}" id="{slug(t["name"])}">'
            f'<h2>{esc(t["name"])}</h2>{"".join(subs)}</article>'
        )
    return "".join(cols)


CSS = """
/* Layout: route banner (A to B), radial map, then one column per territory. */
:root{
  --paper:#eef2ee; --sheet:#f8faf7; --ink:#17262b; --muted:#5b6b6c; --rule:#c9d4cf;
  --route:#1f6b5c; --a:#b4462e; --b:#1f6b5c;
  --t0:#2d6fa3; --t1:#b26b12; --t2:#7a4fa8; --t3:#2f8a55;
  --pain:#b4462e; --howto:#2d6fa3; --lesson:#2f8a55; --why:#8a6d12; --truth:#17262b; --opinion:#7a4fa8; --other:#5b6b6c;
  --f-display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;
  --f-body:"Atkinson Hyperlegible",ui-sans-serif,system-ui,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#111a1c; --sheet:#172225; --ink:#e3ebe8; --muted:#93a3a2; --rule:#2c3b3e;
  --route:#5cc0a6; --a:#e87a5f; --b:#5cc0a6;
  --t0:#6fa8d9; --t1:#e0a04a; --t2:#b392dc; --t3:#69c08b;
  --pain:#e87a5f; --howto:#6fa8d9; --lesson:#69c08b; --why:#d9bb55; --truth:#e3ebe8; --opinion:#b392dc; --other:#93a3a2;
  color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#111a1c; --sheet:#172225; --ink:#e3ebe8; --muted:#93a3a2; --rule:#2c3b3e;
  --route:#5cc0a6; --a:#e87a5f; --b:#5cc0a6;
  --t0:#6fa8d9; --t1:#e0a04a; --t2:#b392dc; --t3:#69c08b;
  --pain:#e87a5f; --howto:#6fa8d9; --lesson:#69c08b; --why:#d9bb55; --truth:#e3ebe8; --opinion:#b392dc; --other:#93a3a2;
  color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 var(--f-body);
  background-image:repeating-radial-gradient(circle at 85% -10%,transparent 0 38px,color-mix(in srgb,var(--rule) 45%,transparent) 38px 39px)}
.wrap{max-width:1180px;margin:0 auto;padding-inline:16px;padding-block:40px 64px;display:grid;gap:40px}
header{display:grid;gap:8px}
.eyebrow{font:500 12px/1 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
h1{font:700 clamp(32px,5vw,52px)/1.05 var(--f-display);margin:0;text-wrap:balance;letter-spacing:-.02em}
.route{display:grid;grid-template-columns:1fr auto 1fr;gap:20px;align-items:center;background:var(--sheet);
  border:1px solid var(--rule);border-radius:14px;padding:24px}
.point{display:grid;gap:6px;min-width:0}
.point b{font:600 12px/1 var(--f-mono);letter-spacing:.1em;text-transform:uppercase;display:flex;gap:8px;align-items:center}
.point b::before{content:"";width:12px;height:12px;border-radius:50%;background:currentColor}
.point.a b{color:var(--a)} .point.b b{color:var(--b)} .point.b{text-align:right} .point.b b{justify-content:flex-end}
.point p{margin:0;font-size:18px;text-wrap:balance}
.path{width:clamp(60px,14vw,180px);height:2px;background:repeating-linear-gradient(90deg,var(--route) 0 8px,transparent 8px 14px);position:relative}
.path::after{content:"";position:absolute;right:-2px;top:-5px;border:6px solid transparent;border-left:9px solid var(--route);border-right:0}
.mission{grid-column:1/-1;margin:0;padding-top:16px;border-top:1px dashed var(--rule);color:var(--muted);text-align:center}
.mission strong{color:var(--ink)}
.chart{overflow-x:auto}
svg{display:block;width:100%;min-width:620px;max-width:940px;margin:0 auto;height:auto}
.rings circle{fill:none;stroke:var(--rule);stroke-dasharray:2 6}
.link{fill:none;stroke-width:2;opacity:.55}
.t0{--c:var(--t0)} .t1{--c:var(--t1)} .t2{--c:var(--t2)} .t3{--c:var(--t3)}
.link{stroke:var(--c)}
.city circle{fill:var(--sheet);stroke:var(--c);stroke-width:3}
.city text{fill:var(--ink);font:500 14px var(--f-body)}
.city:hover circle,.city:focus circle{fill:var(--c)}
.territory rect{fill:var(--c)}
.territory text{fill:var(--sheet);font:700 13px var(--f-mono);letter-spacing:.06em}
.north{fill:var(--ink)}
.north-label{fill:var(--paper);font:700 18px var(--f-display)}
.north-sub{fill:var(--paper);font:500 10px var(--f-mono);letter-spacing:.14em;opacity:.75}
a:focus-visible{outline:2px solid var(--route);outline-offset:3px}
.legend{display:flex;flex-wrap:wrap;gap:8px 20px;justify-content:center}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px;align-items:start}
.territory-col{min-width:0;display:grid;gap:20px}
.territory-col h2{margin:0;padding-bottom:10px;border-bottom:1px solid var(--rule);font:700 24px/1.1 var(--f-display);color:var(--c)}
.sub{display:grid;gap:10px;scroll-margin-top:24px}
.sub:target h3{text-decoration:underline;text-decoration-color:var(--c);text-underline-offset:4px}
.sub h3{margin:0;font:600 17px/1.3 var(--f-body);display:flex;gap:10px;align-items:center}
.pin{flex:none;width:12px;height:12px;border-radius:50%;border:3px solid var(--c)}
ul{list-style:none;margin:0;padding:0 0 0 22px;display:grid;gap:10px}
li{display:grid;gap:4px;min-width:0}
.idea{overflow-wrap:anywhere}
.tag{justify-self:start;font:700 13px/1.2 var(--f-body);color:var(--tag)}
.pain{--tag:var(--pain)} .howto{--tag:var(--howto)} .lesson{--tag:var(--lesson)} .why{--tag:var(--why)}
.truth{--tag:var(--truth)} .opinion{--tag:var(--opinion)} .other{--tag:var(--other)}
footer{color:var(--muted);font-size:14px;text-align:center}
@media (max-width:640px){
  .route{grid-template-columns:1fr} .path{transform:rotate(90deg);margin:12px auto}
  .point.b{text-align:left} .point.b b{justify-content:flex-start}
}
"""


def render(m):
    total = sum(len(s["ideas"]) for t in m["topics"] for s in t["subs"])
    nsubs = sum(len(t["subs"]) for t in m["topics"])
    mission = m["mission"] or f"Help as many people as possible go from {m['a']} to {m['b']}"
    legend = "".join(
        f'<span class="tag {c}">{l}</span>'
        for l, c in [("Pain point", "pain"), ("How-to", "howto"), ("Lesson learned", "lesson"),
                     ("Why it matters", "why"), ("Harsh truth", "truth"), ("Opinion", "opinion")]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Content Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=JetBrains+Mono:wght@500;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
<span class="eyebrow">{len(m["topics"])} territories · {nsubs} cities · {total} post ideas</span>
<h1>Content map</h1>
</header>
<section class="route" aria-label="Mission">
<div class="point a"><b>Point A</b><p>{esc(m["a"])}</p></div>
<div class="path" aria-hidden="true"></div>
<div class="point b"><b>Point B</b><p>{esc(m["b"])}</p></div>
<p class="mission"><strong>Mission:</strong> {esc(mission)}</p>
</section>
<div class="chart">{svg_map(m)}</div>
<div class="legend">{legend}</div>
<div class="cols">{ideas_html(m)}</div>
<footer>Copy this map by hand onto one sheet of paper. Keep it next to where you work.</footer>
</div>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("src", nargs="?", default="content-map.md")
    p.add_argument("-o", "--out")
    args = p.parse_args()
    src = Path(args.src)
    out = Path(args.out) if args.out else src.with_suffix(".html")
    out.write_text(render(parse(src.read_text(encoding="utf-8"))), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
