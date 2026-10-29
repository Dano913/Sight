from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "validation"
    / "backtest"
    / "forward_returns.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "validation"
    / "backtest"
    / "dispersion_by_subperiod.csv"
)

PERIODS = [
    ("1975-1984", "1975-01-01", "1984-12-31"),
    ("1985-1994", "1985-01-01", "1994-12-31"),
    ("1995-2004", "1995-01-01", "2004-12-31"),
    ("2005-2015", "2005-01-01", "2015-12-31"),
]


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def main() -> int:
    input_file = INPUT_FILE
    if not input_file.exists():
        gz_candidate = INPUT_FILE.with_name(INPUT_FILE.name + ".gz")
        if gz_candidate.exists():
            input_file = gz_candidate
        else:
            print(f"ERROR: no existe el archivo: {INPUT_FILE}")
            return 1

    df = pd.read_csv(input_file)

    date_column = find_column(
        df,
        ["signal_date", "signal_origin_date", "date", "observation_date"],
    )
    return_column = find_column(
        df,
        ["forward_return", "forward_return_pct", "return"],
    )

    required = {"asset", "horizon_months"}
    missing = required - set(df.columns)

    if missing:
        print(f"ERROR: faltan columnas: {sorted(missing)}")
        print(f"Columnas disponibles: {list(df.columns)}")
        return 1

    if date_column is None or return_column is None:
        print("ERROR: no se han podido identificar las columnas de fecha y retorno.")
        print(f"Columnas disponibles: {list(df.columns)}")
        return 1

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df[return_column] = pd.to_numeric(
        df[return_column],
        errors="coerce",
    )

    df = df.dropna(
        subset=["asset", "horizon_months", date_column, return_column]
    )

    results = []

    for period_name, start, end in PERIODS:
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)

        period_df = df[
            df[date_column].between(start_date, end_date)
        ]

        for (asset, horizon), group in period_df.groupby(
            ["asset", "horizon_months"],
            dropna=False,
        ):
            returns = group[return_column]

            results.append(
                {
                    "asset": asset,
                    "horizon_months": horizon,
                    "subperiod": period_name,
                    "observations": len(returns),
                    "mean_return": returns.mean(),
                    "median_return": returns.median(),
                    "std_return": returns.std(),
                    "q10_return": returns.quantile(0.10),
                    "q25_return": returns.quantile(0.25),
                    "q75_return": returns.quantile(0.75),
                    "q90_return": returns.quantile(0.90),
                    "min_return": returns.min(),
                    "max_return": returns.max(),
                    "positive_fraction": (returns > 0).mean(),
                    "negative_fraction": (returns < 0).mean(),
                }
            )

    if not results:
        print("ERROR: no se han generado resultados.")
        return 1

    result = pd.DataFrame(results).sort_values(
        ["asset", "horizon_months", "subperiod"]
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print("=== DISPERSIÓN DE RETORNOS POR SUBPERIODO ===")
    print(f"Filas de entrada válidas: {len(df)}")
    print(f"Filas de resumen: {len(result)}")
    print(f"Archivo generado: {OUTPUT_FILE}")

    print("\nEjemplo: BROAD_MARKET")
    example = result[result["asset"] == "BROAD_MARKET"]

    if example.empty:
        print("No hay resultados para BROAD_MARKET.")
    else:
        print(
            example[
                [
                    "horizon_months",
                    "subperiod",
                    "observations",
                    "mean_return",
                    "std_return",
                    "q10_return",
                    "median_return",
                    "q90_return",
                    "positive_fraction",
                ]
            ].to_string(index=False)
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
