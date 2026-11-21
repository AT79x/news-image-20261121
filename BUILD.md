# Build notes — news-image-20261121

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024 PNG, ~30 KB).

## Determinism check

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out1/entry.png out2/entry.png   # must be identical
```

Verified 21 Nov 2026: both runs
`e1674c870cafe786766b648958399318bb5875668a089bcd18ab11639169ef59`
(29,880 bytes, 1024x1024, valid PNG).

## Design

- Pure Python 3 standard library only (`math`, `os`, `struct`, `zlib`).
  No network, no files read at run time, no randomness, no clock.
- Hand-written 5x7 bitmap font (same font as the 18, 19 and 20 Nov
  entries), all copy in capitals.
- NEW LOOK for this edition, per AT (21 Nov, from the news.make.fun
  19 Nov front page): a newspaper front page — ONE big HERO story on
  top, then a numbered grid of story cards, each with a region tag and
  a source line. NOT a copy of the website's photo layout: each card's
  top band is a small hand-drawn illustration in the story's colours
  (falling chart, EU stars + deal papers, sun over waves, defence
  dome, crowd with placards, neon skyline), and the hero panel is a
  dark navy night scene (missile trails over a lit city skyline).
- Dark identity kept from the 20 Nov entry: cream paper outside, dark
  navy hero panel and dark illustration bands, each story with its own
  accent colour — 1 gold, 2 red, 3 sky blue, 4 orange, 5 teal,
  6 violet, 7 magenta — used for the number badge, the illustration
  band, the place kicker, the stat line and the card's top rule.
- Typography and graphics as in the 20 Nov entry: bold = a second pass
  offset 1px, tracking = extra px between glyphs. Type scale: 5
  masthead date (bold), 3 tracked masthead title, 3 bold hero
  headline, 2 bold headlines/kickers/stats, 2 facts, 1 tracked
  labels. Ghosted newspaper texture (column dividers + rows of short
  'text' lines) on the masthead band and every story card, drawn just
  above the cream so the columns read without fighting the copy.
- Seven stories, each verified against at least two independent
  sources — see NEWS.md for sources.
- `out/`, `out1/` and `out2/` are local test outputs only; do not
  commit them. The repository ships no pre-rendered `entry.png`:
  `main.py` draws the image fresh on every run.
