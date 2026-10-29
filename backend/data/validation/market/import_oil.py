from pathlib import Path

import pandas as pd


SOURCE_FILE = Path(__file__).parent / "CMO-Historical-Data-Monthly.xlsx"
OUTPUT_FILE = Path(__file__).parent / "oil.csv"

SHEET_NAME = "Monthly Prices"
SOURCE = "WORLD_BANK_COMMODITY_PRICE_DATA"
ASSET = "OIL"
VALUE_TYPE = "price_index"


def main() -> None:
    df = pd.read_excel(SOURCE_FILE, sheet_name=SHEET_NAME, header=None)

    data = df.iloc[6:, [0, 1]].copy()
    data.columns = ["date", "oil"]

    data["date"] = pd.to_datetime(data["date"], format="%YM%m", errors="coerce")
    data["oil"] = pd.to_numeric(data["oil"], errors="coerce")
    data = data.dropna(subset=["date", "oil"]).reset_index(drop=True)

    if data.empty:
        raise ValueError("No OIL observations found.")

    if data["date"].duplicated().any():
        raise ValueError("OIL contains duplicate dates.")

    dates = data["date"].tolist()

    monthly_gaps = sum(
        (
            dates[i].year * 12 + dates[i].month
            - dates[i - 1].year * 12 - dates[i - 1].month
        ) != 1
        for i in range(1, len(dates))
    )

    if monthly_gaps:
        raise ValueError(f"OIL contains {monthly_gaps} monthly gaps.")

    base_value = data.iloc[0]["oil"]

    if base_value <= 0:
        raise ValueError("Initial OIL price must be positive.")

    data["value"] = data["oil"] / base_value * 100.0
    data["asset"] = ASSET
    data["source"] = SOURCE
    data["value_type"] = VALUE_TYPE

    output = data[["date", "asset", "value", "source", "value_type"]].copy()
    output["date"] = output["date"].dt.strftime("%Y-%m-%d")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False)

    print(f"Created: {OUTPUT_FILE.resolve()}")
    print(f"Rows: {len(output)}")
    print(f"First: {output.iloc[0].to_dict()}")
    print(f"Last: {output.iloc[-1].to_dict()}")


if __name__ == "__main__":
    main()
