#!/usr/bin/env python3
"""Render the brand assets from one source of truth.

Everything here comes from the same basket paths and the same Fira Sans font
files the landing page uses, so an exported card can't drift from the site. Run from
the repo root:  python3 tools/build_brand.py
"""

import pathlib
import shutil
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
OUT = ROOT / "brand"
FONT_800 = (PUB / "fonts" / "fira-sans-latin-800-normal.woff2").as_uri()
FONT_600 = (PUB / "fonts" / "fira-sans-latin-600-normal.woff2").as_uri()

INK_DARK, GROUND_DARK, ACCENT_DARK = "#EDF6F0", "#012F19", "#8FBFA0"
INK_LIGHT, GROUND_LIGHT, ACCENT_LIGHT = "#012F19", "#F3F9F8", "#446C53"

# The basket, the baguette, the apple and the greens — identical to the
# wordmark's SVG in index.html.
BASKET = """
  <path d="M7 27h38l-3.6 16a4 4 0 0 1-3.9 3H14.5a4 4 0 0 1-3.9-3z"/>
  <path d="M4 27h44"/>
  <path d="M17 32.5 18.5 41M26 32.5V41M35 32.5 33.5 41"/>
  <path d="M31 25.5 41.5 12a4.2 4.2 0 0 1 6.5 5.2L38 26"/>
  <path d="M38.5 18.5 41 21M41.5 15 44 17.5"/>
  <circle cx="17" cy="18.5" r="7"/>
  <path d="M17 11.5V8"/>
  <path d="M17.5 9c2-2.2 4.4-2.4 6-1.6-.4 2.2-2.2 3.6-4.6 3.6"/>
  <path d="M26.5 26c-1.5-4 0-8 3.5-10.5"/>
  <path d="M28 20.5c-2.6-.6-4.5.4-5.6 2.2"/>
"""


def icon_svg(ink, ground, radius=0, scale=0.80):
    """A square icon. Scaled in from the edges so it survives platform masking,
    which crops roughly 10% off every side on a rounded or circular mask."""
    rx = f' rx="{radius}"' if radius else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52" width="52" height="52">
  <title>Bringest</title>
  <rect width="52" height="52"{rx} fill="{ground}"/>
  <g fill="none" stroke="{ink}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"
     transform="translate(26 26) scale({scale}) translate(-26 -26)">{BASKET}</g>
</svg>
"""


def card_html(ink, ground, accent):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Fira Sans';font-style:normal;font-weight:800;
  src:url({FONT_800}) format('woff2');}}
@font-face{{font-family:'Fira Sans';font-style:normal;font-weight:600;
  src:url({FONT_600}) format('woff2');}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1200px;height:630px;display:flex;align-items:center;justify-content:center;
  font-family:'Fira Sans',sans-serif;background:{ground};overflow:hidden}}
.card{{display:flex;flex-direction:column;align-items:center}}
.row{{display:flex;align-items:center;gap:30px}}
svg{{width:150px;height:150px;fill:none;stroke:{ink};stroke-width:2.3;
  stroke-linecap:round;stroke-linejoin:round}}
/* Weight and tracking copied from .lhero h1 on the landing page, so the card's
   lettering and the site's hero are the same type at different sizes. */
h1{{font-size:132px;font-weight:800;letter-spacing:-.035em;color:{ink};line-height:.98}}
p{{font-size:52px;font-weight:600;color:{accent};margin-top:34px;letter-spacing:-.015em}}
</style></head><body><div class="card"><div class="row">
<svg viewBox="0 0 52 52">{BASKET}</svg><h1>Bringest</h1></div>
<p>Bring things. Together.</p></div></body></html>
"""


def shoot(page, html, path, w, h):
    tmp = OUT / "_tmp.html"
    tmp.write_text(html, encoding="utf-8")
    page.set_viewport_size({"width": w, "height": h})
    page.goto(tmp.as_uri())
    page.wait_for_timeout(450)
    page.screenshot(path=str(path))
    tmp.unlink()


ICON_SIZES = [1024, 512, 256, 128]


def main():
    for sub in ("icon-dark", "icon-light", "social", "source"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_context(device_scale_factor=1).new_page()

        # --- social cards ---
        for name, (ink, ground, accent) in {
            "bringest-card-dark": (INK_DARK, GROUND_DARK, ACCENT_DARK),
            "bringest-card-light": (INK_LIGHT, GROUND_LIGHT, ACCENT_LIGHT),
        }.items():
            shoot(page, card_html(ink, ground, accent),
                  OUT / "social" / f"{name}.png", 1200, 630)
            print(f"social/{name}.png  1200x630")

        # --- square icons, full-bleed so platforms can mask them ---
        for folder, (ink, ground) in {
            "icon-dark": (INK_DARK, GROUND_DARK),
            "icon-light": (INK_LIGHT, GROUND_LIGHT),
        }.items():
            svg = icon_svg(ink, ground)
            (OUT / folder / "bringest-icon.svg").write_text(svg, encoding="utf-8")
            page_html = ("<!doctype html><meta charset=utf-8>"
                         "<style>html,body{margin:0;padding:0}"
                         "svg{width:100vw;height:100vh;display:block}</style>" + svg)
            for size in ICON_SIZES:
                shoot(page, page_html, OUT / folder / f"bringest-icon-{size}.png", size, size)
            print(f"{folder}/  svg + {', '.join(str(s) for s in ICON_SIZES)}")

        # --- what the live site serves ---
        # Rounded on a tab bar, square everywhere a platform does its own masking.
        (PUB / "favicon.svg").write_text(icon_svg(INK_DARK, GROUND_DARK, radius=11),
                                         encoding="utf-8")
        shoot(page, "<!doctype html><meta charset=utf-8>"
                    "<style>html,body{margin:0;padding:0}svg{width:100vw;height:100vh;"
                    "display:block}</style>" + icon_svg(INK_DARK, GROUND_DARK),
              PUB / "apple-touch-icon.png", 180, 180)
        shutil.copy(OUT / "social" / "bringest-card-dark.png", PUB / "og.png")
        print("public/: favicon.svg, apple-touch-icon.png, og.png (dark)")

        b.close()

    # The wordmark lockup, for anyone who needs it as vector.
    shutil.copy(OUT / "icon-dark" / "bringest-icon.svg", OUT / "source" / "basket-dark.svg")
    shutil.copy(OUT / "icon-light" / "bringest-icon.svg", OUT / "source" / "basket-light.svg")


if __name__ == "__main__":
    sys.exit(main())
