"""Generate the hero field drawing (inline SVG): templates/includes/_hero_field.html.

Follows "How the field is built" in the brand style guide:
  1. evenly spaced horizontal lines across the lower half of the canvas;
  2. each displaced by three overlapping sines, full strength at the left,
     fading to none by about two thirds of the way across;
  3. every line pulled toward one point so all meet at the ring;
  4. the rings stay clean: only the orange decision line crosses them;
  5. fewer lines leave than enter, evenly spaced, to the right edge.

Two canvases, one shown at a time by CSS: WIDE (the guide's 1584-wide base, tablet and desktop)
and NARROW (phones, up to 720 px). A phone cannot show the wide drawing whole: cropped to its
height, only the rings survive and the noise, which lives in the left two thirds, is never seen.
The narrow canvas has the phone hero's shape (about 390 x 220) and about one unit per CSS pixel,
so the noise, the drift and the motion constants read the same as on desktop.

Deterministic (seeded), so re-running produces identical markup.

The static paths are the first frame of the motion in pages/static/js/brand-motion.js, which
recomputes them live from the same formula. Each incoming path therefore carries its own
parameters (y0, k and the three waves) as data attributes, and the canvas constants sit on the
<svg>. The incoming lines are split into three interleaved depth layers for the parallax.

Usage: python tools/gen_field.py templates/includes/_hero_field.html
"""
import math
import random
import sys

DEPTHS = 3                    # back, middle, front: parallax layers of the incoming lines
STEP = 8                      # svg units between path points (brand-motion.js uses the same)

# Each wave is ((amplitude range), (wavelength range)); its phase is drawn from 0..2 pi.
WIDE = {
    "name": "wide", "W": 1584, "H": 300,      # cropped to ~a third of a view
    "CX": 1251, "CY": 165,                    # ring centre at 79% of the width
    "RINGS": [(72, 1.25), (54, 1), (36, 1), (18, 1)],
    "N_IN": 20, "Y0": (128, 272), "BAND": (60, 290),   # incoming lines stay inside the band
    "WAVES": [((30, 46), (280, 440)), ((10, 18), (120, 180)), ((3, 6), (50, 75))],
    "N_OUT": 7, "OUT_GAP": 13, "OUT_FAN": 7, "OUT_RUN": 92,
    "SEED": 20261121, "LABELS": True,
}
NARROW = {
    "name": "narrow", "W": 440, "H": 248,     # the phone hero: ~390 x 220 CSS px
    "CX": 300, "CY": 140,                     # ring at 68%: the noise gets the left 58%
    "RINGS": [(46, 1.25), (34, 1), (23, 1), (11, 1)],
    "N_IN": 14, "Y0": (96, 226), "BAND": (44, 240),
    "WAVES": [((20, 30), (95, 150)), ((7, 12), (40, 62)), ((2, 4), (17, 26))],
    "N_OUT": 5, "OUT_GAP": 11, "OUT_FAN": 9, "OUT_RUN": 56,
    "SEED": 20261122, "LABELS": False,
}


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def xc(c):
    """Incoming lines meet at the outer ring's left edge."""
    return c["CX"] - c["RINGS"][0][0]


def wave_set(rng, c):
    return [(rng.uniform(*amp), rng.uniform(*lam), rng.uniform(0, 2 * math.pi)) for amp, lam in c["WAVES"]]


def incoming_paths(c):
    """Each line as {d, y0, k, waves}; waves are (amplitude, wavelength, phase) triples."""
    rng = random.Random(c["SEED"])
    W, CY, XC = c["W"], c["CY"], xc(c)
    (top, bottom), (y_min, y_max) = c["Y0"], c["BAND"]
    paths = []
    for i in range(c["N_IN"]):
        y0 = top + i * (bottom - top) / (c["N_IN"] - 1)
        waves = wave_set(rng, c)
        xs = list(range(0, XC, STEP)) + [XC]
        disp = []
        for x in xs:
            fade = 1 - smoothstep(x / (W * 2 / 3))
            disp.append(sum(a * math.sin(2 * math.pi * x / lam + ph) for a, lam, ph in waves) * fade)
        # Keep every line inside the band by scaling its displacement, so nothing is cut flat
        # at the band edge in the middle of the page.
        up, down = max(0.0, -min(disp)), max(0.0, max(disp))
        k = min(1.0, (y0 - y_min) / up if up else 1.0, (y_max - y0) / down if down else 1.0)
        pts = []
        for x, d in zip(xs, disp):
            pull = (x / XC) ** 2.2
            pts.append((x, (y0 + d * k) * (1 - pull) + CY * pull))
        paths.append({
            "d": "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in pts),
            "y0": y0, "k": k, "waves": waves,
        })
    return paths


def output_paths(c):
    CX, CY, r, n = c["CX"], c["CY"], c["RINGS"][0][0], c["N_OUT"]
    paths = []
    for j in range(n):
        k = j - (n - 1) / 2
        ang = math.radians(k * c["OUT_FAN"])       # leave the ring fanned out
        sx, sy = CX + r * math.cos(ang), CY + r * math.sin(ang)
        ty = CY + k * c["OUT_GAP"]                 # then run parallel
        ex = CX + r + c["OUT_RUN"]
        paths.append(
            f"M{fmt(sx)} {fmt(sy)} C{fmt(sx + 40)} {fmt(sy + (ty - sy) * 0.15)} "
            f"{fmt(ex - 46)} {fmt(ty)} {fmt(ex)} {fmt(ty)} L{c['W']} {fmt(ty)}"
        )
    return paths


def leader(c):
    r = c["RINGS"][0][0]
    a = math.radians(-42)
    x1, y1 = c["CX"] + (r + 4) * math.cos(a), c["CY"] + (r + 4) * math.sin(a)
    return f"M{fmt(x1)} {fmt(y1)} L{fmt(x1 + 18)} {fmt(y1 - 20)}"


def canvas_svg(c):
    W, H, CX, CY, clip = c["W"], c["H"], c["CX"], c["CY"], f"field-clip-{c['name']}"
    out = [
        f'<svg class="field field-{c["name"]}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMaxYMid slice" '
        f'data-cx="{CX}" data-cy="{CY}" data-xc="{xc(c)}" data-ymin="{c["BAND"][0]}" data-ymax="{c["BAND"][1]}" '
        'aria-hidden="true" focusable="false">',
        f'<defs><clipPath id="{clip}"><rect width="{W}" height="{H}"/></clipPath></defs>',
        f'<g class="field-in" clip-path="url(#{clip})">',
    ]
    lines = incoming_paths(c)
    for depth in range(DEPTHS):   # interleaved, so every depth spans the whole band
        out.append(f'<g class="field-depth" data-depth="{depth}">')
        for line in lines[depth::DEPTHS]:
            waves = ",".join(f"{v:.4f}" for wave in line["waves"] for v in wave)
            out.append(f'<path d="{line["d"]}" data-y0="{line["y0"]:.4f}" '
                       f'data-k="{line["k"]:.6f}" data-w="{waves}"/>')
        out.append("</g>")
    out += ["</g>", f'<g class="field-out" clip-path="url(#{clip})">']
    out += [f'<path d="{d}"/>' for d in output_paths(c)]
    out += ["</g>", '<g class="field-rings">']
    for idx, (r, sw) in enumerate(c["RINGS"]):
        cls = ' class="core"' if idx == len(c["RINGS"]) - 1 else ""
        out.append(f'<circle{cls} cx="{CX}" cy="{CY}" r="{r}" style="stroke-width:{sw}px"/>')
    out.append("</g>")
    if c["LABELS"]:
        out.append(f'<path class="field-leader" d="{leader(c)}"/>')
    out += [
        f'<line class="decision" x1="{CX}" y1="-1200" x2="{CX}" y2="{CY}"/>',
        f'<circle class="decision-dot" cx="{CX}" cy="{CY}" r="4"/>',
        "</svg>",
    ]
    return out


def labels(c):
    """Drawing labels (wide canvas only): HTML so they stay 12 px at every width; % of the canvas."""
    W, H, CX, CY, r = c["W"], c["H"], c["CX"], c["CY"], c["RINGS"][0][0]

    def pct(v, total):
        return f"{v / total * 100:.2f}%"
    spans = [
        ("field-label-in", f"right:{pct(W - (xc(c) - 30), W)};top:{pct(CY - 44, H)}", '{% trans "Stakeholder inputs" %}'),
        ("field-label-vision", f"left:{pct(CX + 12, W)};top:{pct(CY - r - 30, H)}", '{% trans "Vision" %}'),
        ("field-label-machine", f"left:{pct(CX + 78, W)};top:{pct(CY - 86, H)}", '{% trans "The machine" %}'),
        ("field-label-out", f"right:{pct(36, W)};top:{pct(CY + 3 * c['OUT_GAP'] + 14, H)}", '{% trans "Products · Services" %}'),
    ]
    # Look-away phrases (brand-decode.js): each time the hero leaves the view and returns, the
    # input label decodes into the next one. Phrases from the brand guide's tested list.
    variants = {"field-label-in": "|".join([
        "{% trans 'Known rules to the machine · unknown rules to the engineer' %}",
        "{% trans 'AI is the activator · the engineer is the inhibitor' %}",
        "{% trans 'Electricity is the new fire' %}",
    ])}
    out = []
    for cls, style, text in spans:
        extra = f' data-variants="{variants[cls]}"' if cls in variants else ""
        out.append(f'<span class="field-label {cls}" style="{style}"{extra} aria-hidden="true">{text}</span>')
    return out


def svg():
    out = [
        "{% load i18n %}",
        "{% comment %}Generated by tools/gen_field.py: field lines, rings, output lines and the",
        "decision line, on a wide canvas (tablet, desktop) and a narrow one (phones); CSS shows one.",
        "Colours come from the brand tokens via CSS classes; brand-motion.js animates the incoming",
        "lines of the visible canvas from the data attributes. Do not edit by hand.{% endcomment %}",
        '<div class="hero-field">',
    ]
    out += canvas_svg(WIDE) + canvas_svg(NARROW) + labels(WIDE)
    out.append("</div>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    with open(sys.argv[1], "w", encoding="utf-8") as fh:
        fh.write(svg())
