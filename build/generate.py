#!/usr/bin/env python3
"""Generate every graphic on this profile as hand-built SVG.

One palette per theme, one function per sheet. No templates, no third-party
renderers, no trackers. Run:  python3 build/generate.py
"""
from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape as esc

OUT = Path(__file__).resolve().parent.parent / "assets"
REV = "2026.11"

THEMES = {
    "light": dict(bg="#F4F1EA", ink="#17171B", muted="#6E6A62", faint="#DDD7CA",
                  grid="#E8E3D7", side1="#E4DED0", side2="#D3CCBB", accent="#E4572E"),
    "dark":  dict(bg="#0E1217", ink="#ECE7DC", muted="#8B9099", faint="#262C35",
                  grid="#161B22", side1="#1B2129", side2="#232A34", accent="#FF6B3D"),
}

SANS = "Inter, 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"
EASE = 'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"'


def base_css(p: dict) -> str:
    return f"""<style>
  .s{{font-family:{SANS};fill:{p['ink']}}}
  .m{{font-family:{MONO};fill:{p['muted']}}}
  .a{{fill:{p['accent']}}}
  .i{{fill:{p['ink']}}}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
  @keyframes rise{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
  .pulse{{animation:pulse 1.6s ease-in-out infinite}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def svg(w: int, h: int, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>{body}</svg>\n')


def chip(x: float, y: float, text: str, p: dict, size: int = 12, accent: bool = False) -> tuple[str, float]:
    w = len(text) * size * 0.62 + 20
    col = p["accent"] if accent else p["faint"]
    s = (f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{size + 14}" rx="3" fill="none" stroke="{col}"/>'
         f'<text x="{x + 10}" y="{y + size + 5}" class="m" font-size="{size}" '
         f'style="fill:{p["ink"] if not accent else p["accent"]}">{esc(text)}</text>')
    return s, w


# ---------------------------------------------------------------- hero sheet
def iso_plate(cx, cy, a, b, t, p, face, accent=False):
    """An isometric slab: two shaded sides plus an opaque top face."""
    left = f"{cx-a},{cy} {cx},{cy+b} {cx},{cy+b+t} {cx-a},{cy+t}"
    right = f"{cx},{cy+b} {cx+a},{cy} {cx+a},{cy+t} {cx},{cy+b+t}"
    top = f"{cx-a},{cy} {cx},{cy-b} {cx+a},{cy} {cx},{cy+b}"
    stroke = p["accent"] if accent else p["ink"]
    tint = (f'<polygon points="{top}" fill="{p["accent"]}" opacity=".10">'
            f'<animate attributeName="opacity" values=".06;.22;.06" dur="3.2s" repeatCount="indefinite"/></polygon>'
            if accent else "")
    # draw `face` in unit-square coordinates projected onto the top face
    proj = f'matrix({a},{-b},{a},{b},{cx-a},{cy})'
    return (f'<polygon points="{left}" fill="{p["side1"]}" stroke="{stroke}" stroke-width="1.2" stroke-linejoin="round"/>'
            f'<polygon points="{right}" fill="{p["side2"]}" stroke="{stroke}" stroke-width="1.2" stroke-linejoin="round"/>'
            f'<polygon points="{top}" fill="{p["bg"]}" stroke="{stroke}" stroke-width="1.5" stroke-linejoin="round"/>{tint}'
            f'<g transform="{proj}" fill="none" stroke="{stroke}" stroke-width="1" '
            f'vector-effect="non-scaling-stroke">{face}</g>')


def faces():
    nss = 'vector-effect="non-scaling-stroke"'
    ui = (f'<rect x=".18" y=".18" width=".64" height=".64" {nss}/>'
          f'<line x1=".18" y1=".32" x2=".82" y2=".32" {nss}/>'
          f'<rect x=".26" y=".42" width=".22" height=".3" {nss}/>'
          f'<line x1=".56" y1=".46" x2=".74" y2=".46" {nss}/><line x1=".56" y1=".56" x2=".74" y2=".56" {nss}/>')
    pts = [(x, y) for x in (.25, .5, .75) for y in (.25, .5, .75)]
    svc = "".join(f'<line x1="{x}" y1="{y}" x2=".5" y2=".5" {nss}/>' for x, y in pts if (x, y) != (.5, .5))
    svc += "".join(f'<rect x="{x-.04}" y="{y-.04}" width=".08" height=".08" {nss}/>' for x, y in pts)
    ai = "".join(f'<line x1=".5" y1=".5" x2="{.5+.3*math.cos(k*math.pi/4):.3f}" y2="{.5+.3*math.sin(k*math.pi/4):.3f}" {nss}/>'
                 for k in range(8))
    ai += f'<circle cx=".5" cy=".5" r=".12" {nss}/><circle cx=".5" cy=".5" r=".3" stroke-dasharray="2 3" {nss}/>'
    data = "".join(f'<line x1=".2" y1="{y:.2f}" x2=".8" y2="{y:.2f}" {nss}/>' for y in (.2, .35, .5, .65, .8))
    data += f'<line x1=".38" y1=".2" x2=".38" y2=".8" {nss}/>'
    return [ui, svc, ai, data]


def hero(p: dict) -> str:
    W, H = 1200, 460
    o = [base_css(p)]
    o.append(f'<defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse">'
             f'<path d="M20 0H0V20" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>'
             f'<marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
             f'<path d="M0 2 L10 5 L0 8z" fill="{p["muted"]}"/></marker></defs>')
    o.append(f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>')
    o.append(f'<rect x="28" y="28" width="1144" height="404" fill="url(#g)"/>')
    o.append(f'<rect x="14.5" y="14.5" width="1171" height="431" fill="none" stroke="{p["ink"]}" stroke-width="1"/>')
    o.append(f'<rect x="28" y="28" width="1144" height="404" fill="none" stroke="{p["ink"]}" stroke-width="1.5"/>')
    # drawing-sheet zone markers
    zw = 1144 / 6
    for k in range(6):
        x = 28 + zw * k
        if k:
            o.append(f'<line x1="{x:.1f}" y1="14" x2="{x:.1f}" y2="28" stroke="{p["ink"]}"/>'
                     f'<line x1="{x:.1f}" y1="432" x2="{x:.1f}" y2="446" stroke="{p["ink"]}"/>')
        for y in (24.5, 442.5):
            o.append(f'<text x="{x+zw/2:.1f}" y="{y}" class="m" font-size="9" text-anchor="middle">{k+1}</text>')
    zh = 404 / 3
    for k, letter in enumerate("ABC"):
        y = 28 + zh * k
        if k:
            o.append(f'<line x1="14" y1="{y:.1f}" x2="28" y2="{y:.1f}" stroke="{p["ink"]}"/>'
                     f'<line x1="1172" y1="{y:.1f}" x2="1186" y2="{y:.1f}" stroke="{p["ink"]}"/>')
        for x in (21, 1179):
            o.append(f'<text x="{x}" y="{y+zh/2+3:.1f}" class="m" font-size="9" text-anchor="middle">{letter}</text>')

    # ---- identity block
    o.append(f'<text x="72" y="96" class="m" font-size="12" letter-spacing="2.5" style="fill:{p["accent"]}">'
             f'◆ ENGINEERING PROFILE · REV {REV}</text>')
    o.append('<text x="68" y="178" class="s" font-size="80" font-weight="800" letter-spacing="-3">Tofique Adam</text>')
    o.append(f'<rect x="72" y="200" width="56" height="4" fill="{p["accent"]}"/>')
    o.append('<text x="72" y="246" class="s" font-size="30" font-weight="500" letter-spacing="-.5">'
             'Full-stack &amp; AI engineer.</text>')
    o.append('<text x="72" y="290" class="m" font-size="14">I design and build web platforms, APIs and</text>')
    o.append('<text x="72" y="312" class="m" font-size="14">LLM-powered tools — from the interface down to the data.</text>')
    for x, k, v in ((72, "FOCUS", "Applied AI"), (222, "STACK", "Python · TypeScript"), (432, "STATUS", "Building")):
        o.append(f'<text x="{x}" y="362" class="m" font-size="10" letter-spacing="2">{k}</text>')
        dx = 16 if k == "STATUS" else 0
        o.append(f'<text x="{x+dx}" y="386" class="s" font-size="17" font-weight="600">{v}</text>')
    o.append(f'<circle cx="437" cy="380" r="5" class="a pulse"/>')

    # ---- exploded stack
    cx, a, b, t = 840, 125, 72, 12
    cys = [112, 176, 240, 304]
    shifts = [-9, -3, 3, 9]
    labels = [("01", "INTERFACE", "react · next.js · ts"), ("02", "SERVICES", "fastapi · node · rest"),
              ("03", "INTELLIGENCE", "llms · agents · vision"), ("04", "DATA", "postgres · redis · sql")]
    # dimension line breathes with the outer plates
    o.append(f'<line x1="686" y1="{cys[0]-b}" x2="836" y2="{cys[0]-b}" stroke="{p["muted"]}" stroke-width=".6" stroke-dasharray="3 3">'
             f'<animate attributeName="y1" values="40;31;40" dur="6s" repeatCount="indefinite" {EASE}/>'
             f'<animate attributeName="y2" values="40;31;40" dur="6s" repeatCount="indefinite" {EASE}/></line>')
    bot = cys[-1] + b + t
    o.append(f'<line x1="686" y1="{bot}" x2="836" y2="{bot}" stroke="{p["muted"]}" stroke-width=".6" stroke-dasharray="3 3">'
             f'<animate attributeName="y1" values="{bot};{bot+9};{bot}" dur="6s" repeatCount="indefinite" {EASE}/>'
             f'<animate attributeName="y2" values="{bot};{bot+9};{bot}" dur="6s" repeatCount="indefinite" {EASE}/></line>')
    o.append(f'<line x1="694" y1="44" x2="694" y2="{bot-4}" stroke="{p["muted"]}" stroke-width="1" '
             f'marker-start="url(#ar)" marker-end="url(#ar)">'
             f'<animate attributeName="y1" values="44;35;44" dur="6s" repeatCount="indefinite" {EASE}/>'
             f'<animate attributeName="y2" values="{bot-4};{bot+5};{bot-4}" dur="6s" repeatCount="indefinite" {EASE}/></line>')
    o.append(f'<text transform="translate(684 {(40+bot)/2}) rotate(-90)" class="m" font-size="10" '
             f'letter-spacing="4" text-anchor="middle">FULL STACK</text>')
    o.append(f'<line x1="{cx}" y1="34" x2="{cx}" y2="424" stroke="{p["muted"]}" stroke-width=".7" stroke-dasharray="16 4 2 4"/>')
    for k in reversed(range(4)):
        cy, (num, name, sub) = cys[k], labels[k]
        acc = k == 2
        lx = cx + a
        g = [iso_plate(cx, cy, a, b, t, p, faces()[k], accent=acc),
             f'<polyline points="{lx+6},{cy} {lx+30},{cy}" fill="none" stroke="{p["accent"] if acc else p["muted"]}"/>',
             f'<circle cx="{lx+3}" cy="{cy}" r="2.5" fill="{p["accent"] if acc else p["ink"]}"/>',
             f'<text x="{lx+38}" y="{cy+4}" font-size="12" letter-spacing="1.5" style="font-family:{MONO}">'
             f'<tspan fill="{p["accent"]}">{num}</tspan><tspan fill="{p["ink"]}" font-weight="700"> {name}</tspan></text>',
             f'<text x="{lx+38}" y="{cy+21}" class="m" font-size="11">{sub}</text>']
        o.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 {shifts[k]};0 0" '
                 f'dur="6s" repeatCount="indefinite" {EASE}/>{"".join(g)}</g>')

    # ---- title block
    x0, y0, w = 932, 384, 240
    o.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="48" fill="{p["bg"]}" stroke="{p["ink"]}" stroke-width="1.5"/>')
    o.append(f'<line x1="{x0}" y1="{y0+18}" x2="{x0+w}" y2="{y0+18}" stroke="{p["ink"]}"/>')
    o.append(f'<text x="{x0+8}" y="{y0+13}" class="m" font-size="9" letter-spacing="1">github.com/</text>'
             f'<text x="{x0+76}" y="{y0+13}" font-size="10" font-weight="700" style="font-family:{MONO};fill:{p["ink"]}">tofiqueadam</text>')
    for j, (k, v) in enumerate((("DRAWN", "T. ADAM"), ("SCALE", "1 : 1"), ("SHEET", "01/01"))):
        cxx = x0 + j * 80
        if j:
            o.append(f'<line x1="{cxx}" y1="{y0+18}" x2="{cxx}" y2="{y0+48}" stroke="{p["ink"]}"/>')
        o.append(f'<text x="{cxx+8}" y="{y0+28}" class="m" font-size="7.5" letter-spacing="1">{k}</text>'
                 f'<text x="{cxx+8}" y="{y0+43}" font-size="11" font-weight="700" style="font-family:{MONO};fill:{p["ink"]}">{v}</text>')
    return svg(W, H, "".join(o), "Tofique Adam — Full-stack & AI engineer")


# ------------------------------------------------------- bill of materials
STACK = [
    ("Interface", ["TypeScript", "React", "Next.js", "Tailwind CSS", "HTML / CSS"]),
    ("Services", ["Python", "FastAPI", "Node.js", "Express", "REST · JWT auth"]),
    ("Intelligence", ["Gemini API", "LLM agents", "vision · voice", "TensorFlow Lite"]),
    ("Data", ["PostgreSQL", "Redis", "SQL"]),
    ("Mobile", ["Flutter", "Dart", "Kotlin", "Java · Android"]),
    ("Delivery", ["Docker", "Git", "Linux", "Bash", "Cloudflare Workers"]),
]


def bom(p: dict) -> str:
    W, RH, top = 1200, 52, 140
    H = top + RH * len(STACK) + 28
    o = [base_css(p), f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>']
    o.append(f'<text x="40" y="44" class="m" font-size="12" letter-spacing="2.5" style="fill:{p["accent"]}">◆ BILL OF MATERIALS</text>')
    o.append('<text x="38" y="88" class="s" font-size="34" font-weight="750" letter-spacing="-1">What I build with</text>')
    o.append(f'<text x="1160" y="88" class="m" font-size="11" letter-spacing="2" text-anchor="end">'
             f'{len(STACK)} LAYERS · INTERFACE → DELIVERY</text>')
    for x, h in ((40, "NO."), (110, "LAYER"), (330, "PARTS")):
        o.append(f'<text x="{x}" y="{top-10}" class="m" font-size="10" letter-spacing="2">{h}</text>')
    o.append(f'<line x1="40" y1="{top}" x2="1160" y2="{top}" stroke="{p["ink"]}" stroke-width="1.5"/>')
    for i, (layer, parts) in enumerate(STACK):
        y = top + RH * i
        acc = layer == "Intelligence"
        row = [f'<text x="40" y="{y+32}" font-size="13" style="font-family:{MONO};fill:{p["accent"]}">{i+1:02d}</text>',
               f'<text x="110" y="{y+33}" class="s" font-size="18" font-weight="650">{layer}</text>']
        x = 330
        for part in parts:
            s, w = chip(x, y + 13, part, p, accent=acc)
            row.append(s)
            x += w + 8
        row.append(f'<line x1="40" y1="{y+RH}" x2="1160" y2="{y+RH}" stroke="{p["faint"]}"/>')
        o.append(f'<g style="animation:rise .7s cubic-bezier(.2,.7,.2,1) {0.1+i*0.09:.2f}s both">{"".join(row)}</g>')
    return svg(W, H, "".join(o), "Tech stack: " + "; ".join(f"{l}: {', '.join(ps)}" for l, ps in STACK))


# ------------------------------------------------------------ project figs
def g_memora(p):
    dots = "".join(f'<circle cx="{88+k*16}" cy="128" r="4" fill="{p["accent"]}" style="animation:pulse 1.2s {k*0.2:.1f}s infinite"/>'
                   for k in range(3))
    hist = "".join(f'<rect x="{12+k*6}" y="{8+k*7}" width="{120-k*12}" height="4" rx="2" fill="{p["muted"]}" opacity="{0.5-k*0.14:.2f}"/>'
                   for k in range(3))
    return (hist +
            f'<rect x="0" y="40" width="136" height="46" rx="10" fill="none" stroke="{p["ink"]}" stroke-width="1.5"/>'
            f'<path d="M18 86 l-6 12 l18 -12" fill="{p["bg"]}" stroke="{p["ink"]}" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<rect x="16" y="56" width="90" height="4" rx="2" class="i" opacity=".7"/><rect x="16" y="68" width="60" height="4" rx="2" class="i" opacity=".4"/>'
            f'<rect x="60" y="106" width="124" height="44" rx="10" fill="none" stroke="{p["accent"]}" stroke-width="1.5"/>'
            f'<path d="M166 150 l6 12 l-18 -12" fill="{p["bg"]}" stroke="{p["accent"]}" stroke-width="1.5" stroke-linejoin="round"/>'
            + dots)


def g_agent(p):
    bars = []
    for k in range(17):
        h = 10 + 26 * abs(math.sin(k * 1.7)) 
        bars.append(f'<rect x="{30+k*8}" y="{60-h/2:.1f}" width="4" height="{h:.1f}" rx="2" fill="{p["accent"]}" '
                    f'style="transform-box:fill-box;transform-origin:center;animation:wave 1.1s {k*0.07:.2f}s ease-in-out infinite alternate"/>')
    return (f'<style>@keyframes wave{{from{{transform:scaleY(.25)}}to{{transform:scaleY(1)}}}}</style>'
            f'<rect x="0" y="22" width="184" height="76" rx="12" fill="none" stroke="{p["ink"]}" stroke-width="1.5"/>'
            f'<polygon points="12,50 22,60 12,70" fill="{p["ink"]}"/>' + "".join(bars) +
            f'<rect x="0" y="114" width="84" height="62" rx="6" fill="none" stroke="{p["ink"]}" stroke-width="1.5"/>'
            f'<polyline points="8,166 30,140 46,156 58,146 76,166" fill="none" stroke="{p["ink"]}" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<circle cx="62" cy="128" r="6" fill="none" stroke="{p["accent"]}" stroke-width="1.5"/>'
            f'<path d="M98 145 h40 m-8 -7 l8 7 l-8 7" fill="none" stroke="{p["muted"]}" stroke-width="1.5"/>'
            f'<rect x="150" y="128" width="34" height="34" rx="17" fill="none" stroke="{p["accent"]}" stroke-width="1.5"/>'
            f'<text x="167" y="150" text-anchor="middle" font-size="12" font-weight="700" style="font-family:{MONO};fill:{p["accent"]}">AI</text>')


def array_pattern(beta: float, n: int = 6, cx: float = 92, cy: float = 90, R: float = 82, floor_db: float = 30) -> str:
    """Polar plot of an n-element, half-wave-spaced linear array steered by phase `beta`."""
    pts = []
    for s in range(181):
        th = 2 * math.pi * s / 180
        psi = math.pi * math.cos(th) + beta
        den = n * math.sin(psi / 2)
        af = 1.0 if abs(den) < 1e-9 else abs(math.sin(n * psi / 2) / den)
        db = 20 * math.log10(max(af, 1e-6))
        r = R * max(0.0, (db + floor_db) / floor_db)
        pts.append(f"{cx + r*math.sin(th):.1f},{cy - r*math.cos(th):.1f}")
    return "M" + " L".join(pts) + "Z"


def g_antenna(p):
    cx, cy = 92, 90
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{p["faint"]}"/>' for r in (20.5, 41, 61.5, 82))
    spokes = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx+82*math.cos(k*math.pi/6):.1f}" y2="{cy+82*math.sin(k*math.pi/6):.1f}" stroke="{p["faint"]}"/>'
                     for k in range(12))
    betas = [0, .7, 1.4, .7, 0, -.7, -1.4, -.7, 0]
    vals = ";".join(array_pattern(bb) for bb in betas)
    elems = "".join(f'<rect x="{cx-2}" y="{cy-25+k*10-2}" width="4" height="4" fill="{p["ink"]}"/>' for k in range(6))
    return (rings + spokes +
            f'<path d="{array_pattern(0)}" fill="{p["accent"]}" fill-opacity=".12" stroke="{p["accent"]}" stroke-width="1.6" stroke-linejoin="round">'
            f'<animate attributeName="d" values="{vals}" dur="9s" repeatCount="indefinite"/></path>' + elems +
            f'<text x="184" y="12" text-anchor="end" class="m" font-size="9" letter-spacing="1">AF · N=6 · d=λ/2</text>'
            f'<text x="184" y="178" text-anchor="end" class="m" font-size="9" letter-spacing="1">BEAM STEERING</text>')


def g_leaf(p):
    leaf = "M20 150 C 30 60, 110 10, 176 20 C 168 92, 104 170, 20 150 Z"
    veins = "".join(f'<path d="M{x} {y} q {dx} -10 {dx+14} -30" fill="none" stroke="{p["muted"]}" stroke-width="1"/>'
                    for x, y, dx in ((60, 120, 6), (90, 96, 8), (120, 72, 8), (146, 50, 6)))
    spots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{p["accent"]}" opacity=".85"/>'
                    for x, y, r in ((112, 104, 6), (122, 96, 3.5), (104, 112, 3), (70, 84, 2.5)))
    return (f'<defs><clipPath id="lc"><path d="{leaf}"/></clipPath></defs>'
            f'<path d="{leaf}" fill="none" stroke="{p["ink"]}" stroke-width="1.6"/>'
            f'<path d="M20 150 Q 100 92 176 20" fill="none" stroke="{p["ink"]}" stroke-width="1.2"/>' + veins + spots +
            f'<g clip-path="url(#lc)"><rect x="0" y="0" width="190" height="3" fill="{p["accent"]}" opacity=".7">'
            f'<animateTransform attributeName="transform" type="translate" values="0 10;0 160;0 10" dur="4s" repeatCount="indefinite" {EASE}/></rect></g>'
            f'<rect x="92" y="84" width="40" height="38" fill="none" stroke="{p["accent"]}" stroke-width="1.4" stroke-dasharray="4 3"/>'
            f'<rect x="92" y="70" width="52" height="14" fill="{p["accent"]}"/>'
            f'<text x="96" y="80.5" font-size="9" font-weight="700" letter-spacing="1" style="font-family:{MONO};fill:{p["bg"]}">DETECT</text>')

ETH = "'Noto Sans Ethiopic', Nyala, Ebrima, Kefa, 'Abyssinica SIL', sans-serif"


def g_fidel(p):
    grid = ["ሰሱሲሳ", "ለሉሊላ", "መሙሚማ"]
    cell = 40
    o = []
    for r, chars in enumerate(grid):
        for c, ch in enumerate(chars):
            o.append(f'<rect x="{14+c*cell}" y="{8+r*cell}" width="{cell}" height="{cell}" fill="none" stroke="{p["faint"]}"/>'
                     f'<text x="{34+c*cell}" y="{36+r*cell}" text-anchor="middle" font-size="20" style="font-family:{ETH};fill:{p["ink"]}">{ch}</text>')
    o.append(f'<rect x="14" y="8" width="{4*cell}" height="{3*cell}" fill="none" stroke="{p["ink"]}" stroke-width="1.5"/>')
    path = [(0, 0), (1, 3), (2, 2), (0, 3), (1, 1), (2, 0)]
    xs = ";".join(str(14 + c*cell) for _, c in path)
    ys = ";".join(str(8 + r*cell) for r, _ in path)
    o.append(f'<rect width="{cell}" height="{cell}" fill="{p["accent"]}" fill-opacity=".14" stroke="{p["accent"]}" stroke-width="2">'
             f'<animate attributeName="x" values="{xs}" dur="7.2s" calcMode="discrete" repeatCount="indefinite"/>'
             f'<animate attributeName="y" values="{ys}" dur="7.2s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    o.append(f'<text x="14" y="160" font-size="15" style="font-family:{ETH};fill:{p["ink"]}">ሰላም</text>'
             f'<text x="64" y="160" class="m" font-size="13" style="fill:{p["accent"]}">→ selam</text>'
             f'<text x="14" y="182" font-size="15" style="font-family:{ETH};fill:{p["ink"]}">፳፻፲፮</text>'
             f'<text x="64" y="182" class="m" font-size="13" style="fill:{p["accent"]}">→ 2016</text>')
    return "".join(o)


PROJECTS = [
    ("fidel", "fidel · ፊደል", "Python", ["Dependency-free toolkit for Amharic", "text: normalization, tokenizing, SERA", "transliteration, Ethiopic numerals."],
     ["Python", "NLP", "Unicode", "open source"], g_fidel),
    ("memora", "Memora AI", "Python", ["Telegram assistant built on Google", "Gemini with multi-turn memory. Runs", "as a poller or a serverless Worker."],
     ["Python", "Gemini", "Cloudflare Workers"], g_memora),
    ("antenna", "Antenna Design", "Python", ["Radiation analysis for dipoles, helix,", "Yagi–Uda and linear arrays, up to", "Dolph–Chebyshev synthesis."],
     ["NumPy", "SciPy", "Matplotlib"], g_antenna),
    ("leaf", "Mango Leaf Scan", "Dart", ["Flutter app that runs a TensorFlow", "Lite classifier on-device to flag", "mango leaf disease from a photo."],
     ["Flutter", "TFLite", "on-device ML"], g_leaf),
]


def card(p: dict, n: int, title: str, lang: str, desc: list[str], tags: list[str], glyph) -> str:
    W, H = 580, 320
    o = [base_css(p), f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="none" stroke="{p["faint"]}"/>']
    for x, y, sx, sy in ((10, 10, 1, 1), (W-10, 10, -1, 1), (10, H-10, 1, -1), (W-10, H-10, -1, -1)):
        o.append(f'<path d="M{x} {y+14*sy} V{y} H{x+14*sx}" fill="none" stroke="{p["accent"]}" stroke-width="1.5"/>')
    o.append(f'<text x="32" y="44" class="m" font-size="12" letter-spacing="2.5" style="fill:{p["accent"]}">FIG. {n:02d}</text>')
    o.append(f'<text x="548" y="44" class="m" font-size="11" letter-spacing="1.5" text-anchor="end">{lang.upper()}</text>')
    o.append(f'<line x1="32" y1="58" x2="548" y2="58" stroke="{p["faint"]}"/>')
    o.append(f'<text x="30" y="110" class="s" font-size="30" font-weight="750" letter-spacing="-1">{esc(title)}</text>')
    for k, line in enumerate(desc):
        o.append(f'<text x="32" y="{146+k*22}" class="s" font-size="15" style="fill:{p["muted"]}">{esc(line)}</text>')
    x = 32
    for tg in tags:
        s, w = chip(x, 246, tg, p, size=11)
        o.append(s)
        x += w + 6
    o.append(f'<text x="548" y="289" class="m" font-size="11" letter-spacing="1.5" text-anchor="end" style="fill:{p["accent"]}">VIEW SOURCE →</text>')
    o.append(f'<g transform="translate(362 72)">{glyph(p)}</g>')
    return svg(W, H, "".join(o), f"Fig. {n}: {title} — {' '.join(desc)}")


# ------------------------------------------------------------------ footer
def footer(p: dict) -> str:
    W, H = 1200, 110
    o = [base_css(p), f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>',
         f'<line x1="40" y1="36" x2="1160" y2="36" stroke="{p["muted"]}" stroke-width=".8" stroke-dasharray="22 5 3 5"/>',
         f'<rect x="594" y="30" width="12" height="12" transform="rotate(45 600 36)" fill="{p["accent"]}"/>',
         f'<text x="40" y="78" class="m" font-size="11" letter-spacing="2">END OF SHEET 01/01</text>',
         f'<text x="600" y="78" class="m" font-size="12" text-anchor="middle">'
         f'every graphic here is hand-written SVG · generated by build/generate.py · zero trackers</text>',
         f'<text x="1160" y="78" class="m" font-size="11" letter-spacing="2" text-anchor="end">REV {REV}</text>']
    return svg(W, H, "".join(o), "End of sheet")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for theme, p in THEMES.items():
        (OUT / f"hero-{theme}.svg").write_text(hero(p))
        (OUT / f"stack-{theme}.svg").write_text(bom(p))
        (OUT / f"footer-{theme}.svg").write_text(footer(p))
        for n, (slug, title, lang, desc, tags, glyph) in enumerate(PROJECTS, 1):
            (OUT / f"fig-{slug}-{theme}.svg").write_text(card(p, n, title, lang, desc, tags, glyph))
    print(f"wrote {len(list(OUT.glob('*.svg')))} files to {OUT}")


if __name__ == "__main__":
    main()
