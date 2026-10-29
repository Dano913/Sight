from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "data" / "validation" / "backtest" / "forward_returns.csv"
OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "validation"
    / "backtest"
    / "summary_by_subperiod.csv"
)

PERIODS = [
    ("1975-1984", "1975-01-01", "1984-12-31"),
    ("1985-1994", "1985-01-01", "1994-12-31"),
    ("1995-2004", "1995-01-01", "2004-12-31"),
    ("2005-2015", "2005-01-01", "2015-12-31"),
]

GROUP_COLUMNS = [
    "asset",
    "market_value_type",
    "horizon_months",
    "macro_regime",
    "signal_status",
]


def main() -> int:
    input_file = INPUT_FILE
    if not input_file.exists():
        gz_candidate = INPUT_FILE.with_name(INPUT_FILE.name + ".gz")
        if gz_candidate.exists():
            input_file = gz_candidate
        else:
            print(f"ERROR: no existe el archivo de entrada: {INPUT_FILE}")
            return 1

    details = pd.read_csv(input_file)

    required_columns = GROUP_COLUMNS + ["date", "forward_return"]
    missing_columns = [
        column
        for column in required_columns
        if column not in details.columns
    ]

    if missing_columns:
        print(
            "ERROR: faltan columnas en forward_returns.csv: "
            + ", ".join(missing_columns)
        )
        return 1

    details["date"] = pd.to_datetime(details["date"], errors="coerce")
    details["forward_return"] = pd.to_numeric(
        details["forward_return"],
        errors="coerce",
    )

    details = details.dropna(
        subset=["date", "forward_return"]
    ).copy()

    details = details[
        details["forward_return"].map(
            lambda value: pd.notna(value) and abs(value) != float("inf")
        )
    ].copy()

    results = []

    for period_name, start, end in PERIODS:
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)

        period_data = details[
            details["date"].between(start_date, end_date)
        ]

        if period_data.empty:
            continue

        summary = (
            period_data.groupby(
                GROUP_COLUMNS,
                dropna=False,
            )
            .agg(
                observations=("forward_return", "count"),
                mean_forward_return=("forward_return", "mean"),
                median_forward_return=("forward_return", "median"),
                positive_fraction=(
                    "forward_return",
                    lambda values: float((values > 0).mean()),
                ),
            )
            .reset_index()
        )

        summary.insert(0, "subperiod", period_name)
        summary.insert(1, "period_start", start)
        summary.insert(2, "period_end", end)

        results.append(summary)

    if not results:
        print("ERROR: no hay retornos válidos para los subperiodos.")
        return 1

    output = pd.concat(results, ignore_index=True)

    output = output.sort_values(
        [
            "asset",
            "horizon_months",
            "subperiod",
            "macro_regime",
            "signal_status",
        ]
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False)

    print("\n=== ESTABILIDAD TEMPORAL ===")
    print(f"Retornos de entrada: {len(details)}")
    print(f"Filas de resumen: {len(output)}")
    print(f"Subperiodos incluidos: {output['subperiod'].nunique()}")
    print(f"Archivo generado: {OUTPUT_FILE}")

    print("\nEjemplo de resultados:")
    print(
        output[
            [
                "asset",
                "horizon_months",
                "subperiod",
                "observations",
                "mean_forward_return",
                "median_forward_return",
                "positive_fraction",
            ]
        ].head(12).to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())