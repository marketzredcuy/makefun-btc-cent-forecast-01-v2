# btc-cent-forecast-01 — 4-hour mean-reversion forecaster

A program that forecasts Bitcoin's US-dollar price 240 minutes
(4 hours) after a checkpoint, from the 4,320 one-minute closes of
the 72 hours up to that checkpoint.

Model: mean reversion on the 4-hour log return. BTC's 4-hour return
is negatively correlated with the next 4-hour return (about -0.38
on the practice window), so the forecast fades the last 4 hours'
move by a factor of 0.2 in log space: `guess = last * exp(-0.2 * r)`
where `r = log(last / price 240 minutes ago)`. With no recent move
this is persistence, the house baseline. The factor was picked on
the practice cases: it beats persistence on the walk-forward test
(-6% MAE) and the synthetic set (-2.7%), and stays close to it on
the real practice cases and on 30 days of hourly data. Momentum,
EWMA, reversion to the 24h/72h mean and trend extrapolation all
tested worse than persistence overall.

Run: `python3 main.py` (reads `$MAKEFUN_INPUT_DIR`, else `/input`;
writes `$MAKEFUN_OUTPUT_DIR`, else `/output`). One
`/output/<id>.out` per `/input/<id>.in`, JSON
`{"forecasts": [{"case": <id>, "price": <guess>}]}`.

Standard library only, offline, deterministic.

License: MIT.
