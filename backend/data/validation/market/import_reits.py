from pathlib import Path

import pandas as pd


SOURCE_FILE = Path("/tmp/MonthlyHistoricalReturns.xls")
OUTPUT_FILE = Path(__file__).parent / "reits.csv"


def main() -> None:
    df = pd.read_excel(
        SOURCE_FILE,
        sheet_name="Index Data",
        header=None,
        skiprows=9,
        usecols=[0, 23],
        names=["date", "value"],
    )

    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    if df["date"].duplicated().any():
        raise ValueError("Duplicate dates found")

    if df["value"].isna().any():
        raise ValueError("Missing values found")

    df = df.sort_values("date").reset_index(drop=True)

    month_keys = df["date"].dt.year * 12 + df["date"].dt.month
    if (month_keys.diff().dropna() != 1).any():
        raise ValueError("Monthly gaps found")

    output = pd.DataFrame(
        {
            "date": df["date"].dt.strftime("%Y-%m-%d"),
            "asset": "REITS",
            "value": df["value"],
            "source": "FTSE_NAREIT_US_ALL_EQUITY_REITS",
            "value_type": "total_return_index",
        }
    )

    output.to_csv(OUTPUT_FILE, index=False)

    print(f"Created: {OUTPUT_FILE}")
    print(f"Rows: {len(output)}")
    print(f"First: {output.iloc[0].to_dict()}")
    print(f"Last: {output.iloc[-1].to_dict()}")


if __name__ == "__main__":
    main()
