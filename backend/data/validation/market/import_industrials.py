import zipfile
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
ZIP_PATH = Path("/tmp/ff30.zip")
OUTPUT_PATH = BASE_DIR / "industrials.csv"

ASSETS = [
    "Cnstr",
    "Steel",
    "FabPr",
    "ElcEq",
    "Autos",
    "Carry",
    "Mines",
    "Coal",
]


def main():
    with zipfile.ZipFile(ZIP_PATH) as z:
        with z.open("30_Industry_Portfolios.csv") as f:
            df = pd.read_csv(f, skiprows=11, nrows=1202)

    df = df.iloc[:, :31].copy()

    df["date"] = pd.to_datetime(
        df.iloc[:, 0].astype(str),
        format="%Y%m",
    )

    returns = df[ASSETS].apply(pd.to_numeric, errors="coerce")

    if returns.isna().any().any():
        raise ValueError("Missing values found in INDUSTRIALS source data")

    if (returns <= -99).any().any():
        raise ValueError("Fama-French sentinel values found in INDUSTRIALS source data")

    monthly_return = returns.mean(axis=1)

    index = 100.0 * (1.0 + monthly_return / 100.0).cumprod()

    output = pd.DataFrame(
        {
            "date": df["date"].dt.strftime("%Y-%m-%d"),
            "asset": "INDUSTRIALS",
            "value": index,
            "source": "KENNETH_FRENCH_30_INDUSTRY_EQUALLY_WEIGHTED",
            "value_type": "total_return_index",
        }
    )

    output.to_csv(OUTPUT_PATH, index=False)

    print(f"Created: {OUTPUT_PATH}")
    print(f"Rows: {len(output)}")
    print(f"First: {output.iloc[0].to_dict()}")
    print(f"Last: {output.iloc[-1].to_dict()}")


if __name__ == "__main__":
    main()
