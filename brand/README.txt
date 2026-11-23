BRINGEST BRAND ASSETS
Bring things. Together.

The deep green is #012F19. The cream is #F3F9F8. The accent green used for
the saying is #8FBFA0 on dark and #446C53 on light. The typeface is
Recursive, at weight 800 for the wordmark and 600 for the saying.

Everything here is rendered from the same basket artwork and the same font
file the live site uses, so nothing in this folder can drift from bringest.com.


icon-dark/     The square icon, cream basket on deep green. This is the one
               the site uses and the one to match the social card.
icon-light/    The same icon inverted, for placing on a dark background.

               bringest-icon.svg          vector, scales to any size
               bringest-icon-1024.png     app stores
               bringest-icon-512.png      PWA manifests, social profile pictures
               bringest-icon-256.png      desktop and docs
               bringest-icon-128.png      small UI, browser extensions

               The basket sits at 80% of the square so it survives the circular
               and rounded-rectangle masks that iOS, Android and most social
               profiles apply. Don't add your own rounded corners — the
               platform does it, and doing it twice shows.

social/        bringest-card-dark.png     1200x630, live on the site now
               bringest-card-light.png    1200x630, the cream alternative

               This is what appears when a bringest.com link is pasted into a
               message, a feed or a Slack channel.

source/        The icon as standalone SVG in both treatments.


To regenerate any of this after a change, run tools/build_brand.py from the
repo root. Editing a PNG by hand will be overwritten the next time it runs.
