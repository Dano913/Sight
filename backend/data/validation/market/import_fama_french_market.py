from __future__ import annotations

import calendar
import csv
import zipfile
from datetime import date
from pathlib import Path


ZIP_PATH = Path("/tmp/ff_factors.zip")
OUTPUT_PATH = Path(__file__).resolve().parent / "fama_french_market.csv"


def month_end(year: int, month: int) -> date:
    return date(
        year,
        month,
        calendar.monthrange(year, month)[1],
    )


def parse_market_returns(text: str) -> list[tuple[date, float]]:
    rows: list[tuple[date, float]] = []

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        parts = [part.strip() for part in line.split(",")]

        if len(parts) != 5:
            continue

        period = parts[0]

        if len(period) != 6 or not period.isdigit():
            continue

        year = int(period[:4])
        month = int(period[4:])

        if not 1 <= month <= 12:
            continue

        try:
            market_excess_return = float(parts[1])
            risk_free_rate = float(parts[4])
        except ValueError:
            continue

        market_return = market_excess_return + risk_free_rate

        rows.append(
            (
                month_end(year, month),
                market_return,
            )
        )

    return rows


def build_index(
    returns: list[tuple[date, float]],
) -> list[dict[str, object]]:
    index_value = 100.0
    rows: list[dict[str, object]] = []

    for observation_date, monthly_return in returns:
        index_value *= 1.0 + monthly_return / 100.0

        rows.append(
            {
                "date": observation_date.isoformat(),
                "asset": "BROAD_MARKET",
                "value": index_value,
                "source": "KENNETH_FRENCH_RESEARCH_FACTORS",
                "value_type": "total_return_index",
            }
        )

    return rows


def main() -> None:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(
            f"Fama-French factors ZIP not found: {ZIP_PATH}"
        )

    with zipfile.ZipFile(ZIP_PATH) as archive:
        csv_name = "F-F_Research_Data_Factors.csv"

        if csv_name not in archive.namelist():
            raise ValueError(
                f"{csv_name} not found in ZIP"
            )

        with archive.open(csv_name) as file:
            text = file.read().decode("latin-1")

    returns = parse_market_returns(text)
    rows = build_index(returns)

    if not rows:
        raise ValueError("No monthly market observations found")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "date",
                "asset",
                "value",
                "source",
                "value_type",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {OUTPUT_PATH}")
    print(f"Rows: {len(rows)}")
    print(f"First: {rows[0]}")
    print(f"Last: {rows[-1]}")


if __name__ == "__main__":
    main()