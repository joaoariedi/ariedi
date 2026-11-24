"""Render the social share cards (1200 x 630, Open Graph / Twitter): one per language.

  pages/static/images/brand/share-en.png
  pages/static/images/brand/share-pt-br.png

Each card is the hero on the night sheet: the drafting grid, the headline and subline in the
page's language, the field drawing across the bottom (the wide canvas from
templates/includes/_hero_field.html, regenerate that first with tools/gen_field.py) with its
nebula and the orange decision line, the signature and the address. Styles come from the site's
own CSS (brand-tokens, brand, brand-glow), the words from the pt-BR catalogue, so the card
follows the brand when either changes.

Dev only: needs Playwright with Chromium, not a project dependency.
Usage: python tools/gen_share_image.py [path/to/chromium]
"""
import html
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "pages" / "static" / "css"
OUT = ROOT / "pages" / "static" / "images" / "brand"
W, H = 1200, 630

HEADLINE = "I build the machine that turns vision into revenue"
SUB_IN, SUB_OUT = "Business opportunities in", "products and services out"


def catalogue():
    """msgid -> msgstr from the pt-BR catalogue (single-line entries, as makemessages writes them)."""
    po = (ROOT / "locale" / "pt_BR" / "LC_MESSAGES" / "django.po").read_text(encoding="utf-8")
    return {m.group(1): m.group(2) for m in re.finditer(r'^msgid "(.+)"\nmsgstr "(.+)"$', po, re.M)}


def field_svg():
    """The wide canvas of the generated hero drawing (its labels are HTML, left out here)."""
    include = (ROOT / "templates" / "includes" / "_hero_field.html").read_text(encoding="utf-8")
    return re.search(r'<svg class="field field-wide".*?</svg>', include, re.S).group(0)


def card(words):
    links = "".join(f'<link rel="stylesheet" href="{(CSS / f).as_uri()}">'
                    for f in ("brand-tokens.css", "brand.css", "brand-glow.css"))
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
{links}
<style>
html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; }}
body {{
  position: relative; background-color: var(--ground);
  background-image:
    repeating-linear-gradient(0deg, var(--scan) 0 1px, transparent 1px 2px),
    linear-gradient(var(--grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size: auto, var(--unit) var(--unit), var(--unit) var(--unit);
}}
.top {{ position: absolute; left: 56px; right: 56px; top: 44px; display: flex; justify-content: space-between;
  font: 500 15px/20px var(--font-mono); letter-spacing: .1em; text-transform: uppercase; color: var(--label); }}
.top b {{ color: var(--text); font-weight: 500; }}
h1 {{ position: absolute; left: 56px; top: 104px; width: 820px; margin: 0;
  font: 700 60px/64px var(--font-display); letter-spacing: .02em; text-transform: uppercase; color: var(--text); }}
.rule {{ position: absolute; left: 56px; top: 316px; width: 150px; height: 2px;
  background: repeating-linear-gradient(90deg, var(--accent) 0 10px, transparent 10px 16px); }}
.sub {{ position: absolute; left: 56px; top: 336px; font: 400 18px/24px var(--font-mono);
  letter-spacing: .04em; text-transform: uppercase; color: var(--label); }}
.hero-field {{ position: absolute; left: 0; bottom: 0; width: {W}px; aspect-ratio: 1584 / 400; margin: 0; }}
.hero-field .field {{ overflow: visible; }}
</style></head><body>
<div class="top"><span><b>J. Ariedi</b> · {html.escape(words['practice'])}</span><span>ariedi.com</span></div>
<h1>{html.escape(words['headline'])}</h1>
<div class="rule"></div>
<div class="sub">{html.escape(words['sub'])}</div>
<div class="hero-field">{field_svg()}</div>
</body></html>"""


def main():
    pt = catalogue()
    practice = "Engineering advisory · Ventures"
    languages = {
        "en": {"headline": HEADLINE, "sub": f"{SUB_IN} · {SUB_OUT}", "practice": practice},
        "pt-br": {"headline": pt[HEADLINE], "sub": f"{pt[SUB_IN]} · {pt[SUB_OUT]}", "practice": pt[practice]},
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=sys.argv[1]) if len(sys.argv) > 1 else p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, reduced_motion="reduce")
        for code, words in languages.items():
            tmp = OUT / f".share-{code}.html"
            tmp.write_text(card(words), encoding="utf-8")
            page.goto(tmp.as_uri(), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.screenshot(path=str(OUT / f"share-{code}.png"))
            tmp.unlink()
            print(f"share-{code}.png")
        browser.close()


if __name__ == "__main__":
    main()
