[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/katotaihei/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/katotaihei/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# 25 November 2026 — World News in One Image

Entry for make.fun competition `news-image-20261125`
("Sum up 25 November's world news in one image", $100).

## Run

```sh
python3 main.py   # writes entry.png in the current directory
                  # (and /output/entry.png when /output exists)
```

`main.py` is Python 3.13, standard library only, no network.
It draws the image pixel by pixel with its own tiny raster canvas
and 5x7 bitmap font, then encodes the PNG itself. There is no
randomness and no clock, so two runs write byte-identical files.

## What the image shows

A newspaper front page dated **Wednesday 25 November 2026** with
five main stories and a ticker, all reported on that day:

1. **Two tankers hit mines in the Strait of Hormuz** — Iran's
   Revolutionary Guards say two oil tankers struck naval mines and
   caught fire on an unauthorised route; Brent crude tops $93 a
   barrel.
2. **Houthis claim hit on Saudi's biggest refinery** — the Houthis
   claim a strike on the Ras Tanura refinery; Saudi Arabia says it
   shot down four drones, and satellite images show smoke over
   the site.
3. **100th Macy's Parade postponed in a first** — the Thanksgiving
   Day parade moves to Saturday as a storm brings gusts of up to
   60 mph to New York; the first postponement in its history.
4. **Pakistan's first astronaut reaches orbit** — China's
   Shenzhou-24 docks at the Tiangong station with Muhammad Zeeshan
   Ali, the first foreign astronaut aboard the station.
5. **Fuel truck fire kills at least 30 in Cairo** — a vehicle
   carrying petroleum products overturns on Cairo's ring road;
   15 injured, the Health Ministry says.

Ticker: the Solomon Islands signs a treaty with Australia barring
foreign military bases; Pope Leo XIV laments the failure of the
COP31 climate talks.

Stories were cross-checked across the day's reporting (Reuters,
AP, CNN, Xinhua, Al Jazeera, The Straits Times, Nikkei Asia,
Oilprice, Just Security).

## License

MIT — see `LICENSE`.
