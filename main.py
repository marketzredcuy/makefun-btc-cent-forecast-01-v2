#!/usr/bin/env python3
"""BTC 4-hour-ahead price forecast for btc-cent-forecast-01.

For each case, read 4,320 one-minute BTC/USDC closes covering the
72 hours before a checkpoint, then write a single forecast: the
price expected 240 minutes after the checkpoint. Output goes to
/output/<case>.out as {"forecasts": [{"case": <id>, "price": <n>}]}

Approach: fade the last 4-hour move. Over the practice window the
4-hour log return is negatively correlated (about -0.38) with the
following 4-hour return, so a rally tends to retrace a little and
a drop tends to recover a little. The forecast shrinks the latest
4-hour log move by 20%:

    move = ln(close / close_240m_ago)
    forecast = close * exp(-0.20 * move)

A flat market (move = 0) gives plain persistence, the baseline the
house entry uses. The 20% fade was picked on the practice cases:
it beats persistence on the walk-forward test (-6% mean error) and
on the synthetic set (-2.7%), while staying close to it on the real
practice cases. Pure standard library, no network, deterministic.
"""
import json
import math
import os

INPUT = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

FLOOR = 0.00001
CEILING = 9_999_999.99999
FADE = 0.2
LOOKBACK = 240


def snap(value):
    """Round to the 5-decimal price grid, clamped to the allowed range."""
    clipped = min(CEILING, max(FLOOR, value))
    return round(clipped * 100000) / 100000


def predict(closes):
    """Forecast the price 240 minutes after the final close."""
    if not closes:
        raise ValueError("empty price series")
    close = closes[-1]
    if not isinstance(close, (int, float)) or not math.isfinite(close):
        raise ValueError("final close is not a finite number")
    if len(closes) <= LOOKBACK or close <= 0:
        return snap(close)
    start = closes[-LOOKBACK - 1]
    if not isinstance(start, (int, float)) or not math.isfinite(start) \
            or start <= 0:
        return snap(close)
    move = math.log(close / start)
    return snap(close * math.exp(-FADE * move))


def run():
    os.makedirs(OUTPUT, exist_ok=True)
    names = sorted(n for n in os.listdir(INPUT) if n.endswith(".in"))
    for name in names:
        case_id = name.removesuffix(".in")
        with open(os.path.join(INPUT, name), encoding="utf-8") as handle:
            case = json.load(handle)
        markets = case.get("markets")
        if not isinstance(markets, list) or len(markets) != 1:
            raise ValueError(f"{name} must contain exactly one market")
        closes = markets[0].get("prices")
        if not isinstance(closes, list) or not closes:
            raise ValueError(f"{name} has no price series")
        payload = {"forecasts": [{"case": case_id, "price": predict(closes)}]}
        with open(os.path.join(OUTPUT, case_id + ".out"), "w",
                  encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
