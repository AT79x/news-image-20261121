[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/at79x/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/at79x/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

# news-image-20261121 — The World in One Day

A program that draws one image summing up the world news of **Saturday 21
November 2026**, as an entry for the [make.fun bounty "Sum up 21
November's world news in one image"](https://make.fun/bounty/news-image-20261121).

`main.py` (Python 3, standard library only, no network) draws the image
from scratch and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`. Two runs
produce byte-identical output.

A new look for this edition, after the dark world map of 20 November: a
newspaper front page — one big HERO story on top (Russia's biggest strike
on Ukraine, missiles landing in Poland, on a dark navy panel with an
illustrated night sky) and a numbered grid of six story cards below, each
with its own accent colour, a small hand-drawn illustration band, a region
tag and a source line. Classic cream paper around it, with a ghosted
newspaper-column texture, as in the 20 November entry.

## The seven stories (all verified against Reuters / AP / BBC / CNN / WSJ and others, 21 Nov 2026)

1. **Kyiv / Poland — Russia's biggest strike.** 404 drones and 111
   missiles overnight; 8 killed in Kyiv. Missiles land in Poland; Tusk
   calls it an intentional provocation, NATO a grave violation.
2. **New York — AI sell-off.** Dow -950, S&P -3.7%, Nasdaq -5.3%:
   S&P and Dow fall into correction; worst week since 2020.
3. **Brussels — UK-EU reset.** Food, carbon and youth deals signed;
   100,000 visas a year for 18- to 31-year-olds.
4. **Antalya — COP31 overtime.** Draft deal drops all fossil-fuel
   words; talks run past the deadline.
5. **Riyadh — missile defence.** Saudi defences down three Houthi
   missiles; third night of alerts in the capital.
6. **Europe — Gen Z protests.** Youth strike in 25 countries over
   costs, cuts, arms and climate.
7. **Los Angeles — GTA VI.** $3.79bn in day-one sales, the biggest
   entertainment launch ever; 32.5m copies pre-sold.

See [NEWS.md](NEWS.md) for the sources behind each story.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: `out/entry.png` — 1024x1024 PNG, about 30 KB.
