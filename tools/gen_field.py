"""Generate the hero field drawing (inline SVG): templates/includes/_hero_field.html.

Follows "How the field is built" in the brand style guide:
  1. evenly spaced horizontal lines across the lower half of the canvas;
  2. each displaced by three overlapping sines, full strength at the left and still turbulent
     close to the ring, fading to none only at the line's own point on it;
  3. every line pulled toward the ring, each to its own point on the outer ring's left arc:
     the noise is not funnelled into one point, it arrives ordered, at many points;
  4. the rings stay clean: only the orange decision line crosses them;
  5. fewer lines leave than enter, evenly spaced and gently diverging to the right edge:
     order out of the noise, set toward several goals.

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
    "name": "wide", "W": 1584, "H": 400,      # the phone's proportions: ring ~0.36 of the height
    "CX": 1251, "CY": 214,                    # ring centre at 79% of the width
    "RINGS": [(72, 1.25), (54, 1), (36, 1), (18, 1)],
    "N_IN": 20, "Y0": (74, 384), "BAND": (60, 392),    # a high, tall start; the top strip is the label's
    "WAVES": [((38, 56), (280, 440)), ((12, 22), (120, 180)), ((4, 7), (50, 75))],
    "N_OUT": 7, "OUT_GAP": 15, "OUT_FAN": 7, "OUT_RUN": 92, "OUT_HANDLES": (40, 46),
    "ARC": 84, "OUT_SPREAD": 4,               # arrival arc (deg either side), output divergence (deg per line)
    "FADE": 0.7, "PULL": 5.5,                 # turbulence for 70% of the way; a late, steep funnel
    "SEED": 20261121, "LABELS": True,
}
NARROW = {
    "name": "narrow", "W": 440, "H": 248,     # the phone hero: ~390 x 220 CSS px
    "CX": 300, "CY": 140,                     # ring at 68%: the noise gets the left 58%
    "RINGS": [(46, 1.25), (34, 1), (23, 1), (11, 1)],
    "N_IN": 14, "Y0": (78, 230), "BAND": (44, 240),
    "WAVES": [((20, 30), (95, 150)), ((7, 12), (40, 62)), ((2, 4), (17, 26))],
    "N_OUT": 5, "OUT_GAP": 11, "OUT_FAN": 9, "OUT_RUN": 34, "OUT_HANDLES": (14, 16),
    "ARC": 84, "OUT_SPREAD": 4,
    "FADE": 0.6, "PULL": 4.0,
    "SEED": 20261122, "LABELS": False,
}


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def xc(c):
    """The outer ring's left edge."""
    return c["CX"] - c["RINGS"][0][0]


def round1(v):
    return float(f"{v:.1f}")


def targets(c):
    """Where each incoming line meets the outer ring: evenly spread over its left arc, top line
    to the top of the arc, so the lines arrive in their order and never cross. Rounded to the
    precision written into data-tx/data-ty, which brand-motion.js computes from."""
    CX, CY, r, n, arc = c["CX"], c["CY"], c["RINGS"][0][0], c["N_IN"], c["ARC"]
    out = []
    for i in range(n):
        a = math.radians(180 + arc - i * 2 * arc / (n - 1))
        out.append((round1(CX + r * math.cos(a)), round1(CY + r * math.sin(a))))
    return out


def wave_fade(c, x, tx):
    """Full turbulence until FADE of the way to the line's own point on the ring, then it dies
    out over the rest, reaching none exactly at the ring."""
    return 1 - smoothstep((x / tx - c["FADE"]) / (1 - c["FADE"]))


def pull_at(c, x, tx):
    """How far the line has given in to its target: late (PULL), so the noise holds until close."""
    return (x / tx) ** c["PULL"]


def line_xs(tx):
    xs, x = [], 0
    while x < tx:
        xs.append(x)
        x += STEP
    return xs + [tx]


def wave_set(rng, c):
    return [(rng.uniform(*amp), rng.uniform(*lam), rng.uniform(0, 2 * math.pi)) for amp, lam in c["WAVES"]]


def incoming_paths(c):
    """Each line as {d, y0, k, waves, tx, ty}; waves are (amplitude, wavelength, phase) triples."""
    rng = random.Random(c["SEED"])
    W = c["W"]
    (top, bottom), (y_min, y_max) = c["Y0"], c["BAND"]
    paths = []
    for i, (tx, ty) in enumerate(targets(c)):
        y0 = top + i * (bottom - top) / (c["N_IN"] - 1)
        waves = wave_set(rng, c)
        xs = line_xs(tx)
        disp = []
        for x in xs:
            disp.append(sum(a * math.sin(2 * math.pi * x / lam + ph) for a, lam, ph in waves) * wave_fade(c, x, tx))
        # Keep every line inside the band by scaling its displacement, so nothing is cut flat
        # at the band edge in the middle of the page.
        up, down = max(0.0, -min(disp)), max(0.0, max(disp))
        k = min(1.0, (y0 - y_min) / up if up else 1.0, (y_max - y0) / down if down else 1.0)
        pts = []
        for x, d in zip(xs, disp):
            pull = pull_at(c, x, tx)
            pts.append((x, (y0 + d * k) * (1 - pull) + ty * pull))
        paths.append({
            "d": "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in pts),
            "y0": y0, "k": k, "waves": waves, "tx": tx, "ty": ty,
        })
    return paths


def output_line(c, j):
    """One output line: (start, control 1, control 2, settle point, end at the right edge)."""
    CX, CY, r, n = c["CX"], c["CY"], c["RINGS"][0][0], c["N_OUT"]
    k = j - (n - 1) / 2
    ang = math.radians(k * c["OUT_FAN"])           # leave the ring fanned out
    sx, sy = CX + r * math.cos(ang), CY + r * math.sin(ang)
    ty = CY + k * c["OUT_GAP"]                     # settle into even spacing...
    ex = CX + r + c["OUT_RUN"]
    slope = math.tan(math.radians(k * c["OUT_SPREAD"]))   # ...that keeps opening, gently
    h1, h2 = c["OUT_HANDLES"]                      # curve handles, sized to the canvas's run
    return ((sx, sy), (sx + h1, sy + (ty - sy) * 0.15), (ex - h2, ty - h2 * slope),
            (ex, ty), (c["W"], ty + (c["W"] - ex) * slope))


def output_paths(c):
    paths = []
    for j in range(c["N_OUT"]):
        (sx, sy), (c1x, c1y), (c2x, c2y), (ex, ey), (wx, wy) = output_line(c, j)
        paths.append(f"M{fmt(sx)} {fmt(sy)} C{fmt(c1x)} {fmt(c1y)} {fmt(c2x)} {fmt(c2y)} "
                     f"{fmt(ex)} {fmt(ey)} L{fmt(wx)} {fmt(wy)}")
    return paths


def canvas_svg(c):
    W, H, CX, CY, clip = c["W"], c["H"], c["CX"], c["CY"], f"field-clip-{c['name']}"
    out = [
        f'<svg class="field field-{c["name"]}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMaxYMid slice" '
        f'data-cx="{CX}" data-cy="{CY}" data-xc="{xc(c)}" data-ymin="{c["BAND"][0]}" data-ymax="{c["BAND"][1]}" '
        f'data-fade="{c["FADE"]}" data-pull="{c["PULL"]}" '
        'aria-hidden="true" focusable="false">',
        f'<defs><clipPath id="{clip}"><rect width="{W}" height="{H}"/></clipPath>'
        f'<clipPath id="{clip}-in"><path clip-rule="evenodd" d="M0 0H{W}V{H}H0Z'
        f'M{xc(c)} {CY}a{c["RINGS"][0][0]} {c["RINGS"][0][0]} 0 1 0 {2 * c["RINGS"][0][0]} 0'
        f'a{c["RINGS"][0][0]} {c["RINGS"][0][0]} 0 1 0 {-2 * c["RINGS"][0][0]} 0Z"/></clipPath></defs>',
        f'<g class="field-in" clip-path="url(#{clip}-in)">',
    ]
    lines = incoming_paths(c)
    for depth in range(DEPTHS):   # interleaved, so every depth spans the whole band
        out.append(f'<g class="field-depth" data-depth="{depth}">')
        for line in lines[depth::DEPTHS]:
            waves = ",".join(f"{v:.4f}" for wave in line["waves"] for v in wave)
            out.append(f'<path d="{line["d"]}" data-y0="{line["y0"]:.4f}" '
                       f'data-k="{line["k"]:.6f}" data-tx="{fmt(line["tx"])}" data-ty="{fmt(line["ty"])}" '
                       f'data-w="{waves}"/>')
        out.append("</g>")
    out += ["</g>", f'<g class="field-out" clip-path="url(#{clip})">']
    out += [f'<path d="{d}"/>' for d in output_paths(c)]
    out += ["</g>", '<g class="field-rings">']
    for idx, (r, sw) in enumerate(c["RINGS"]):
        cls = ' class="core"' if idx == len(c["RINGS"]) - 1 else ""
        out.append(f'<circle{cls} cx="{CX}" cy="{CY}" r="{r}" style="stroke-width:{sw}px"/>')
    out.append("</g>")
    out += [
        f'<line class="decision" x1="{CX}" y1="-1200" x2="{CX}" y2="{CY}"/>',
        f'<circle class="decision-dot" cx="{CX}" cy="{CY}" r="4"/>',
        "</svg>",
    ]
    return out


def labels(c):
    """Drawing labels (wide canvas only): HTML so they stay 12 px at every width; % of the canvas.

    One row in the strip the band keeps clear at the top, each label over the part of the flow it
    names, in reading order: the stakeholders' vision over the noise (aligned with the headline),
    the divergent intelligence where the turbulence starts to converge, the machine over the ring
    (left of the decision line), products and services over the output fan (right of it)."""
    W, H, CX, r = c["W"], c["H"], c["CX"], c["RINGS"][0][0]

    def pct(v, total):
        return f"{v / total * 100:.2f}%"
    # The band's soft edge reaches 20 units above it; the label (22 units) sits 8 above that.
    row = f"top:{pct(c['BAND'][0] - 20 - 8 - 22, H)}"
    spans = [
        ("field-label-in", f"left:max(36px, calc((100% - 1152px) / 2));{row}", '{% trans "Stakeholders Vision" %}'),
        ("field-label-divergent", f"left:{pct(c['FADE'] * xc(c), W)};{row}", '{% trans "Divergent Intelligence" %}'),
        ("field-label-machine", f"right:{pct(W - (CX - 20), W)};{row}", '{% trans "The Machine" %}'),
        ("field-label-out", f"left:{pct(CX + r + 12, W)};{row}", '{% trans "Products and Services" %}'),
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
