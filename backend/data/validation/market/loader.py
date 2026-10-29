from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .schema import MarketObservation


class MarketDataLoader:
    """
    Loads normalized historical market observations from CSV.
    """

    REQUIRED_COLUMNS = {
        "date",
        "asset",
        "value",
        "source",
        "value_type",
    }

    @classmethod
    def load(cls, path: str | Path) -> list[MarketObservation]:
        csv_path = Path(path)

        with csv_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            columns = set(reader.fieldnames or [])
            missing = cls.REQUIRED_COLUMNS - columns

            if missing:
                raise ValueError(
                    f"Missing required columns: {sorted(missing)}"
                )

            observations: list[MarketObservation] = []

            for row in reader:
                observations.append(
                    MarketObservation(
                        date=date.fromisoformat(row["date"]),
                        asset=row["asset"],
                        value=float(row["value"]),
                        source=row["source"],
                        value_type=row["value_type"],
                    )
                )

        return sorted(
            observations,
            key=lambda observation: (
                observation.asset,
                observation.date,
            ),
        )