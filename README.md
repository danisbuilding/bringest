# Bringest

Sign-up lists for potlucks and collective meals. A host writes down what's
needed, shares one link, and guests claim a dish, say what they're bringing, and
leave a note.

**No accounts, no sign-in, no email address, no app to install.** A host is
identified by holding a secret link, and a guest by nothing at all.

Live at **bringest.com**

The history before the rename belongs to two earlier private builds this grew
out of; Bringest is the one that is maintained.

## What it does

| | |
|---|---|
| Host | Writes the list: items, how many of each, an optional note per item |
| Guest | Claims an item, names the dish, says hot or cold and how many it serves |
| Notes | One for everyone on the list, one only the host can read |
| Counts | "3 needed" before anyone signs up, "3 more needed" once someone has |
| Colour | Nine themes, picked per event |
| Top of the page | Optional header photo, cropped in the browser to 1200x600 |
| Host link | Copy, share sheet, email draft, or a calendar file |
| Retention | An event is deleted after three years with no activity |

No AI, no payments, no tracking cookies, and the only third party is Cloudflare.

## Layout

```
public/index.html          the whole frontend: router, views, styles
public/fonts/              self-hosted Recursive variable woff2
public/_redirects          /h/* and /e/* -> index.html
public/_headers            CSP and security headers
functions/api/[[path]].js  the whole API, one onRequest handler
functions/img/[[path]].js  serves header photos out of R2, outside /api
schema.sql                 D1 and R2 shapes
tests/api.test.mjs         47 integration tests
```

No framework, no bundler, no dependencies.

## Tests

```
node --test tests/api.test.mjs
```

Needs Node 22+ (`node:sqlite`). No network, no wrangler, no database — the suite
shims D1 over in-memory SQLite and applies the real `schema.sql`, and shims R2
over a `Map`.

Rendering is checked against a server that parses `public/_headers` and applies
it, because a plain static server ignores the CSP — which is how a CSP bug
shipped once already.

## Header photos

Optional, one per event, and absent from the DOM entirely when unset — the
page then starts with the title exactly as it did before.

The editor normalises every photo to **1200x600 JPEG** on a canvas before it
leaves the browser, so a stored banner is always the same shape and the page can
reserve its box with `aspect-ratio` instead of jumping when the bytes land. A
photo taller than 2:1 gets a drag control to choose which band survives the
crop; centre-cropping a portrait is otherwise a coin flip on whether faces make
it. Sources under 1000x500 are refused rather than upscaled into a soft banner.

The server does not trust any of that. It re-sniffs the JPEG magic bytes (never
the content-type header, which the caller sets), re-checks the 2 MB cap, and
requires the host key. Uploads count against the host write throttle.

Objects live in R2 under the same string the `events.header_image` column
stores, minus the leading slash. Replacing a photo deletes the object it
replaced; deleting an event deletes its object. Keys carry a random token, so
any stored image is immutable and `/img/` serves it with a year-long immutable
cache. `/img/` is a separate Function precisely so that the `Cache-Control:
no-store` rule `_headers` puts on `/api/*` does not reach it.

Because images are served from the app's own origin, `img-src 'self'` in the CSP
already covers them. Nothing in `_headers` needed to open up.

## The one rule that matters

`claims.note_to_host` is a **host-only** column. It is excluded from the `SELECT`
in every guest-facing response, not merely left unrendered by the client. The
guest payload is unauthenticated and returns the full claim set, so a column
that ships in the JSON is readable by anyone with the guest link and a dev-tools
panel.

Three tests guard this. If you touch `loadItems`, keep the audience split.

"Host-only" means whoever holds the host URL. There is no password.

## Themes

Nine, in `THEMES` at the top of the script. Each is sixteen derived tokens, not
hand-picked colours — deep tier at L\*16 C\*24, with burnt orange the one
mid-tier theme at L\*40 C\*68. All clear WCAG AA on every checked pair.

Don't hand-edit a single value; regenerate the set so the relationships hold.
Event pages take the host's theme; the landing page and dashboard always stay
forest so the app keeps an identity of its own.

## Deploying

Cloudflare Pages, connected to this repo. Framework preset **None**, build
command **empty**, build output directory **`public`**. D1 database bound as
**`DB`**, R2 bucket bound as **`IMG`**.

Without the R2 binding everything still works and photo uploads return a clear
503 — the feature is additive, not load-bearing.

`functions/` sits at the repo root, beside `public/` — not inside it. Pages only
compiles Functions from a Git-connected project; a dashboard folder upload ships
static files only and the API silently 404s.

Schema changes go in the D1 console one statement at a time — the console
flattens a multi-line paste onto one line, which turns `--` comments into a
comment that swallows the rest.

## The two link blocks

The host page shows the guest link and the host link in separate blocks. They
used to share one heading that read "Share this with guests", which was wrong
about half of what sat under it: the host link must not be shared.

The guest block offers Copy and Share. The host block offers Email, Share and a
calendar file, under the warning that there is no password and no recovery.

`navigator.share` is missing in Firefox and some desktop browsers, so the Share
buttons are **absent** there rather than disabled — a button that can never work
is worse than one that was never offered. Below 360px the three host buttons
would need ~330px of content against the 250px an iPhone SE gives, so the third
drops to its own full-width row.

## Calendar files

`events.starts_at` is an optional floating local `YYYY-MM-DDTHH:MM`, or a bare
`YYYY-MM-DD` for an all-day entry. No zone and no offset: the event is at
3pm where it is, and pinning a zone would shift it for anyone adding it from
elsewhere. A date without a time becomes all-day rather than a guessed hour.

It does not replace `when_text`, which stays the line guests read. It exists
only so an `.ics` file can be built, and the Calendar button is absent until a
date is set.

The file is generated in the browser to RFC 5545, folded at 75 octets — without
that the host link pushes DESCRIPTION over the limit and Outlook and Apple
Calendar reject the file outright. The host link goes in the description with a
warning not to invite guests to the entry, since the calendar entry carries a
secret.

Validation is whole-value, not truncating: `startsAt` rejects anything over 16
characters rather than slicing it, so a malformed `2026-11-28T15:00:00` is
refused instead of being quietly trimmed into something valid.

## Deployment record

| | |
|---|---|
| Pages project | `bringest` |
| Repo | `danisbuilding/bringest`, branch `main` |
| Build output directory | `public` |
| Build command | none |
| D1 database | `bringest`, bound as `DB` |
| R2 bucket | `bringest-images`, bound as `IMG` |
| Domains | `bringest.com`, `bringest.pages.dev` |
| Analytics | Cloudflare Web Analytics, enabled on the Pages project |

The CSP already allows the analytics beacon, and `Referrer-Policy` is
`same-origin` rather than `no-referrer` because the beacon is rejected without a
Referer. Change either back and the dashboard silently reads zero.

Health check: `/api/health` returns `db_bound` and `db_query`. Both must be
`true`. A binding added after a deployment does not reach it — redeploy, or push
a commit, so a new deployment picks it up.
