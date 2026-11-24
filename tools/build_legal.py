#!/usr/bin/env python3
"""Turn the three policy markdown files into styled static pages under public/.

Run from the repo root:  python3 tools/build_legal.py

The source of truth is the markdown in legal/. These pages are
generated, so edit the markdown and re-run rather than editing the HTML.
"""

import datetime
import html
import pathlib
import re
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "legal"
OUT = ROOT / "public"

PAGES = [
    ("privacy.md", "privacy.html", "Privacy Policy"),
    ("terms.md", "terms.html", "Terms of Service"),
    ("cookies.md", "cookies.html", "Cookie Statement"),
]

# Styling borrowed from the app so a policy page reads as part of Bringest and
# not a bare document: same palette, same variable font, same thick borders.
SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} &middot; Bringest</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#F3F9F8">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Bringest">
<meta property="og:title" content="{title} &middot; Bringest">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://bringest.com/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://bringest.com/og.png">
<link rel="preload" href="/fonts/fira-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/fira-sans-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:400;font-display:swap;
  src:url(/fonts/fira-sans-latin-ext-400-normal.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:400;font-display:swap;
  src:url(/fonts/fira-sans-latin-400-normal.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:500;font-display:swap;
  src:url(/fonts/fira-sans-latin-ext-500-normal.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:500;font-display:swap;
  src:url(/fonts/fira-sans-latin-500-normal.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:600;font-display:swap;
  src:url(/fonts/fira-sans-latin-ext-600-normal.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:600;font-display:swap;
  src:url(/fonts/fira-sans-latin-600-normal.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:700;font-display:swap;
  src:url(/fonts/fira-sans-latin-ext-700-normal.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:700;font-display:swap;
  src:url(/fonts/fira-sans-latin-700-normal.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:800;font-display:swap;
  src:url(/fonts/fira-sans-latin-ext-800-normal.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Sans';font-style:normal;font-weight:800;font-display:swap;
  src:url(/fonts/fira-sans-latin-800-normal.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}
@font-face {{font-family:'Fira Sans';font-style:italic;font-weight:400;font-display:swap;
  src:url(/fonts/fira-sans-latin-ext-400-italic.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Sans';font-style:italic;font-weight:400;font-display:swap;
  src:url(/fonts/fira-sans-latin-400-italic.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}
@font-face {{font-family:'Fira Sans';font-style:italic;font-weight:700;font-display:swap;
  src:url(/fonts/fira-sans-latin-ext-700-italic.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Sans';font-style:italic;font-weight:700;font-display:swap;
  src:url(/fonts/fira-sans-latin-700-italic.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}
@font-face {{font-family:'Fira Mono';font-style:normal;font-weight:400;font-display:swap;
  src:url(/fonts/fira-mono-latin-ext-400-normal.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Mono';font-style:normal;font-weight:400;font-display:swap;
  src:url(/fonts/fira-mono-latin-400-normal.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}
@font-face {{font-family:'Fira Mono';font-style:normal;font-weight:500;font-display:swap;
  src:url(/fonts/fira-mono-latin-ext-500-normal.woff2) format('woff2');
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;}}
@font-face {{font-family:'Fira Mono';font-style:normal;font-weight:500;font-display:swap;
  src:url(/fonts/fira-mono-latin-500-normal.woff2) format('woff2');
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;}}

:root{{
  --ink:#012F19;
  --ground:#F3F9F8;
  --wash:#F0F6F5;
  --edge:#BACAC6;
  --note:#4a564d;
  --absent:#69726C;
  --rule:#E9F1EE;
}}

*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{
  margin:0;
  background:var(--ground);
  color:var(--ink);
  font-family:'Fira Sans',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;
  font-size:1rem;
  line-height:1.62;
}}

.wrap{{max-width:40rem;margin:0 auto;padding:1.4rem 16px 3.5rem}}

/* ---- top bar ---- */
.top{{
  display:flex;align-items:center;justify-content:space-between;gap:1rem;
  padding-bottom:1rem;margin-bottom:1.7rem;border-bottom:2.5px solid var(--ink);
}}
.home{{
  font-size:1.18rem;font-weight:800;letter-spacing:-.4px;text-decoration:none;
  color:var(--ink);
}}
.home:hover{{text-decoration:underline;text-decoration-thickness:2px}}
.back{{font-size:.84rem;color:var(--note);text-decoration:none;border-bottom:1.5px solid var(--edge)}}
.back:hover{{color:var(--ink);border-bottom-color:var(--ink)}}

/* ---- document ---- */
h1{{
  font-size:1.75rem;line-height:1.2;letter-spacing:-.6px;margin:0 0 .3rem;
  font-weight:800;
}}
h2{{
  font-size:1.07rem;line-height:1.35;margin:2.3rem 0 .55rem;font-weight:800;
  letter-spacing:-.1px;
}}
h2+p,h2+ul,h2+table{{margin-top:0}}
p{{margin:0 0 .95rem}}
h1+p em{{
  display:block;font-style:normal;font-size:.84rem;color:var(--absent);
  text-transform:uppercase;letter-spacing:.4px;font-weight:700;margin-bottom:1.6rem;
}}
strong{{font-weight:800}}
a{{color:var(--ink);text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:2px}}
a:hover{{text-decoration-thickness:2.5px}}
ul,ol{{margin:0 0 .95rem;padding-left:1.25rem}}
li{{margin-bottom:.4rem}}
li>p{{margin:0 0 .4rem}}
code{{
  font-family:'Fira Mono',ui-monospace,monospace;font-size:.9em;
  background:var(--wash);border:1.5px solid var(--edge);border-radius:5px;padding:.08em .32em;
}}
hr{{border:0;border-top:2px solid var(--rule);margin:2.2rem 0}}

/* ---- tables ---- */
.tablewrap{{overflow-x:auto;margin:0 0 1.2rem;-webkit-overflow-scrolling:touch}}
table{{border-collapse:collapse;width:100%;min-width:30rem;font-size:.88rem}}
th,td{{text-align:left;vertical-align:top;padding:.55rem .7rem;border-bottom:1.5px solid var(--edge)}}
th{{
  font-weight:800;font-size:.76rem;text-transform:uppercase;letter-spacing:.4px;
  color:var(--note);border-bottom:2.5px solid var(--ink);
}}
tr:last-child td{{border-bottom:0}}

/* ---- foot ---- */
.foot{{
  margin-top:3rem;padding-top:1.1rem;border-top:2.5px solid var(--ink);
  font-size:.84rem;color:var(--note);
}}
.foot a{{margin-right:1rem;white-space:nowrap}}
.foot .maker{{margin:.9rem 0 0;font-size:.78rem;line-height:1.7;color:var(--absent)}}
.foot .maker b{{font-weight:700;color:var(--note)}}
.foot .maker a{{margin:0;color:var(--absent)}}

@media (max-width:420px){{
  .wrap{{padding-top:1.1rem}}
  h1{{font-size:1.5rem}}
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <a class="home" href="/">Bringest</a>
    <a class="back" href="/">&larr; Back to Bringest</a>
  </div>
  <main>
{body}
  </main>
  <div class="foot">
{nav}
    <p class="maker">Bringest is a <b>DIB&nbsp;Works</b> product, operated by LVT8&nbsp;Technical&nbsp;LLC.<br>
      &copy; {year}</p>
  </div>
</div>
</body>
</html>
"""

CONTACT = ("mailto:support@dib.works", "Contact")

NAV = {
    "privacy.html": [("/terms", "Terms of Service"), ("/cookies", "Cookie Statement"), CONTACT],
    "terms.html": [("/privacy", "Privacy Policy"), ("/cookies", "Cookie Statement"), CONTACT],
    "cookies.html": [("/privacy", "Privacy Policy"), ("/terms", "Terms of Service"), CONTACT],
}


def first_sentence(md_text):
    """A one-line description for the meta tag, drawn from the document itself."""
    for line in md_text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "_", "|", "-", "*")):
            continue
        # Strip inline markdown links down to their text.
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = line.replace("**", "").replace("*", "")
        return line.split(". ")[0].rstrip(".") + "."
    return "Bringest policy."


def build(src_name, out_name, title):
    md_path = SRC / src_name
    if not md_path.exists():
        sys.exit(f"missing source: {md_path}")
    text = md_path.read_text(encoding="utf-8")

    body = markdown.markdown(text, extensions=["tables", "sane_lists", "smarty"])

    # Tables need a scroll container on a phone; the markdown library won't add one.
    body = body.replace("<table>", '<div class="tablewrap"><table>')
    body = body.replace("</table>", "</table></div>")

    body = "\n".join("    " + ln for ln in body.splitlines())

    nav = "\n".join(
        f'    <a href="{href}">{html.escape(label)}</a>' for href, label in NAV[out_name]
    )

    page = SHELL.format(
        title=html.escape(title),
        desc=html.escape(first_sentence(text), quote=True),
        body=body,
        nav=nav,
        year=datetime.date.today().year,
    )
    (OUT / out_name).write_text(page, encoding="utf-8")
    print(f"{out_name}: {len(page):,} bytes")


if __name__ == "__main__":
    for args in PAGES:
        build(*args)
