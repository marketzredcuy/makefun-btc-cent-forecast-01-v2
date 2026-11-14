# btc-cent-forecast-01 — fading the 4-hour move

Predicts where BTC/USDC trades 4 hours after a checkpoint, using
the 4,320 one-minute closes from the 72 hours before it.

Idea: the 4-hour return mean-reverts. On the practice window the
last 4-hour log return correlates about -0.38 with the next one,
so the forecast pulls the latest 4-hour move 20% back toward
where it started: `forecast = close * exp(-0.20 * ln(close /
close_240m_ago))`. No recent move means plain persistence, the
house baseline. The 20% fade won on walk-forward (-6% MAE) and
synthetic (-2.7%) practice tests; momentum, EWMA, long-mean
reversion and trend fits all did worse than persistence.

Usage: `python3 main.py`. It reads `$MAKEFUN_INPUT_DIR`
(default `/input`) and writes one JSON file per case to
`$MAKEFUN_OUTPUT_DIR` (default `/output`):
`{"forecasts": [{"case": <id>, "price": <guess>}]}`.

Standard library only. No network. Deterministic.

License: MIT.
