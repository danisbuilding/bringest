# Policy sources

These markdown files are the source of truth for the three policy pages. The
HTML under `public/` is generated — edit the markdown here and run:

    python3 tools/build_legal.py

Changing a policy means changing the "Effective" date at the top of the file.

| Source | Served at |
|---|---|
| `privacy.md` | `/privacy` |
| `terms.md` | `/terms` |
| `cookies.md` | `/cookies` |

Cloudflare Pages serves an extensionless path from the matching `.html` file
and 301s `/privacy.html` to `/privacy`, so the app links to the short form.
