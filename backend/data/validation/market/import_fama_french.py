from __future__ import annotations

import calendar
import csv
import zipfile
from datetime import date
from pathlib import Path


ZIP_PATH = Path("/tmp/ff30.zip")
OUTPUT_PATH = Path(__file__).resolve().parent / "fama_french.csv"

ASSET_MAPPING = {
    "Fin": "FINANCIALS",
    "BusEq": "TECHNOLOGY",
    "Oil": "ENERGY",
    "Util": "UTILITIES",
}


def month_end(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])


def parse_monthly_returns(text: str) -> dict[str, list[tuple[date, float]]]:
    lines = text.splitlines()

    header_index = None

    for index, line in enumerate(lines):
        if line.strip().startswith("Average Value Weighted Returns -- Monthly"):
            header_index = index
            break

    if header_index is None:
        raise ValueError("Monthly value-weighted section not found")

    header = [
        column.strip()
        for column in lines[header_index + 1].split(",")
    ]

    if header[0] != "":
        raise ValueError("Unexpected Fama-French header format")

    industries = header[1:]

    result: dict[str, list[tuple[date, float]]] = {
        industry: []
        for industry in ASSET_MAPPING
    }

    for line in lines[header_index + 2:]:
        stripped = line.strip()

        if not stripped:
            break

        parts = [part.strip() for part in line.split(",")]

        if not parts or not parts[0].isdigit():
            continue

        period = parts[0]

        if len(period) != 6:
            continue

        year = int(period[:4])
        month = int(period[4:])

        if not 1 <= month <= 12:
            continue

        values = parts[1:]

        for industry in ASSET_MAPPING:
            column_index = industries.index(industry)

            if column_index >= len(values):
                continue

            raw_value = values[column_index]

            if raw_value in {"-99.99", "-999"}:
                continue

            result[industry].append(
                (
                    month_end(year, month),
                    float(raw_value),
                )
            )

    return result


def build_indices(
    returns: dict[str, list[tuple[date, float]]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for industry, observations in returns.items():
        asset = ASSET_MAPPING[industry]

        index_value = 100.0

        for observation_date, monthly_return in observations:
            index_value *= 1.0 + monthly_return / 100.0

            rows.append(
                {
                    "date": observation_date.isoformat(),
                    "asset": asset,
                    "value": index_value,
                    "source": "KENNETH_FRENCH_30_INDUSTRY",
                    "value_type": "total_return_index",
                }
            )

    return sorted(
        rows,
        key=lambda row: (
            str(row["asset"]),
            str(row["date"]),
        ),
    )


def main() -> None:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Fama-French ZIP not found: {ZIP_PATH}")

    with zipfile.ZipFile(ZIP_PATH) as archive:
        csv_names = [
            name
            for name in archive.namelist()
            if name.endswith("30_Industry_Portfolios.csv")
        ]

        if not csv_names:
            raise ValueError(
                "30_Industry_Portfolios.csv not found in ZIP"
            )

        with archive.open(csv_names[0]) as file:
            text = file.read().decode("latin-1")

    returns = parse_monthly_returns(text)
    rows = build_indices(returns)

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

    for asset in sorted({str(row["asset"]) for row in rows}):
        count = sum(1 for row in rows if row["asset"] == asset)
        print(f"{asset}: {count}")


if __name__ == "__main__":
    main()