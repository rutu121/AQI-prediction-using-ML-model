#!/usr/bin/env python3
"""Simple 7-day AQI forecast using recent observations.

This is a lightweight baseline that:
- Loads daily AQI observations from CSV.
- Fits a simple linear trend using ordinary least squares.
- Blends the trend with a 7-day moving average.
- Emits 7 daily forecasts.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Tuple

DATE_FORMAT = "%Y-%m-%d"


@dataclass
class Observation:
    date: datetime
    aqi: float


def load_observations(path: Path) -> List[Observation]:
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    observations: List[Observation] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            date = datetime.strptime(row["date"], DATE_FORMAT)
            aqi = float(row["aqi"])
            observations.append(Observation(date=date, aqi=aqi))

    if len(observations) < 14:
        raise ValueError("Need at least 14 days of data for the baseline forecast.")

    observations.sort(key=lambda obs: obs.date)
    return observations


def linear_trend(observations: Iterable[Observation]) -> Tuple[float, float]:
    """Return slope and intercept for y = slope * x + intercept."""
    observations = list(observations)
    xs = list(range(len(observations)))
    ys = [obs.aqi for obs in observations]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = numerator / denominator if denominator else 0.0
    intercept = mean_y - slope * mean_x
    return slope, intercept


def moving_average(values: List[float], window: int) -> float:
    if window <= 0:
        raise ValueError("Window must be positive")
    if len(values) < window:
        raise ValueError("Not enough values for moving average")
    return sum(values[-window:]) / window


def forecast_next_7_days(observations: List[Observation]) -> List[Tuple[datetime, float]]:
    slope, intercept = linear_trend(observations)
    recent_values = [obs.aqi for obs in observations]
    avg_7 = moving_average(recent_values, window=7)

    last_date = observations[-1].date
    last_index = len(observations) - 1

    forecasts = []
    for horizon in range(1, 8):
        x = last_index + horizon
        trend_value = slope * x + intercept
        blended = 0.6 * trend_value + 0.4 * avg_7
        target_date = last_date + timedelta(days=horizon)
        forecasts.append((target_date, max(0.0, blended)))
    return forecasts


def format_forecast(forecasts: List[Tuple[datetime, float]]) -> str:
    lines = ["date,aqi_forecast"]
    for date, value in forecasts:
        lines.append(f"{date.strftime(DATE_FORMAT)},{value:.1f}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate 7-day AQI forecast.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/sample_aqi.csv"),
        help="Path to CSV with daily AQI observations.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    observations = load_observations(args.data)
    forecasts = forecast_next_7_days(observations)
    print(format_forecast(forecasts))


if __name__ == "__main__":
    main()
