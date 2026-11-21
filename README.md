[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/gregorionainggolan8-tech/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/gregorionainggolan8-tech/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# The World Today — Saturday, 21 November 2026

A one-page newspaper front page summing up the world news of Saturday
21 November 2026, drawn entirely in code by `main.py` (Python 3 standard
library only) and written to `/output/entry.png` (1024x1024 PNG).

## How it works

`main.py` draws everything itself: a hand-written PNG encoder (zlib +
struct), a small canvas library (rects, lines, circles, polygons), and an
embedded 5x7 bitmap font. No network access, no downloaded images, no
third-party packages — so two runs produce byte-identical output.

Run it with:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## The six stories (all reported on 21 November 2026)

1. **Russian missiles land in Poland** — Russia fired 400+ drones and 110
   missiles at Ukraine overnight; at least eight killed in Kyiv. Two
   Russian missiles and a suspected drone came down in Poland; PM Donald
   Tusk called it a deliberate provocation and NATO jets scrambled.
   (BBC, Reuters, AP)
2. **Markets tumble** — US stocks fell sharply in an AI sell-off: the S&P
   500 dropped 3.7% into correction, the Nasdaq 5.3%, Nvidia 13.8% as the
   SEC opened a probe into its accounting. (FT, Guardian, CNBC)
3. **Genocide ruling** — The International Court of Justice ruled Myanmar
   committed genocide against the Rohingya in 2017, the first time it has
   held a state responsible. (BBC, UN News)
4. **Shenzhen summit** — Presidents Trump, Xi and Putin met in Shenzhen;
   Trump called the Ukraine talks "very good" and said humans must stay in
   charge of military AI decisions. (Reuters, Axios)
5. **Quake hits Peru** — A magnitude 6.8 earthquake struck Junin in
   central Peru; tremors were felt in Lima, 320 km away.
   (Peru Geophysical Institute)
6. **COP31 stalls** — Climate talks in Antalya, Turkiye, missed their
   deadline, and the draft text dropped any mention of fossil fuels.
   (Reuters, Euronews)

## License

MIT — see `LICENSE`.
