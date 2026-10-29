from pathlib import Path

import pandas as pd


SOURCE_FILE = Path(__file__).parent / "CMO-Historical-Data-Monthly.xlsx"
OUTPUT_FILE = Path(__file__).parent / "gold.csv"

SOURCE = "WORLD_BANK_COMMODITY_PRICE_DATA"
ASSET = "GOLD"
VALUE_TYPE = "price_index"

GOLD_COLUMN = 69
FIRST_DATA_ROW = 6


def main() -> None:
    df = pd.read_excel(
        SOURCE_FILE,
        sheet_name="Monthly Prices",
        header=None,
    )

    data = df.iloc[FIRST_DATA_ROW:, [0, GOLD_COLUMN]].copy()
    data.columns = ["date", "gold"]

    data = data[data["date"].notna()].copy()
    data["gold"] = pd.to_numeric(data["gold"], errors="coerce")

    if data["gold"].isna().any():
        raise ValueError("Gold series contains non-numeric values")

    dates = pd.to_datetime(
        data["date"].str.replace("M", "-", regex=False) + "-01"
    )

    if dates.duplicated().any():
        raise ValueError("Gold series contains duplicate dates")

    month_numbers = dates.dt.year * 12 + dates.dt.month

    if (month_numbers.diff().dropna() != 1).any():
        raise ValueError("Gold series contains monthly gaps")

    base_value = data["gold"].iloc[0]

    if base_value <= 0:
        raise ValueError("Gold base value must be positive")

    data["value"] = data["gold"] / base_value * 100

    output = pd.DataFrame(
        {
            "date": dates.dt.strftime("%Y-%m-%d"),
            "asset": ASSET,
            "value": data["value"],
            "source": SOURCE,
            "value_type": VALUE_TYPE,
        }
    )

    output.to_csv(OUTPUT_FILE, index=False)

    print(f"Created: {OUTPUT_FILE}")
    print(f"Rows: {len(output)}")
    print(f"First: {output.iloc[0].to_dict()}")
    print(f"Last: {output.iloc[-1].to_dict()}")


if __name__ == "__main__":
    main()