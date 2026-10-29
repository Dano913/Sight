from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = (
    BASE_DIR
    / "data"
    / "validation"
    / "backtest"
    / "summary_by_subperiod.csv"
)
OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "validation"
    / "backtest"
    / "stability_by_asset_horizon.csv"
)


def main() -> int:
    if not INPUT_FILE.exists():
        print(f"ERROR: no existe {INPUT_FILE}")
        return 1

    df = pd.read_csv(INPUT_FILE)

    required = {
        "asset",
        "horizon_months",
        "subperiod",
        "observations",
        "mean_forward_return",
        "median_forward_return",
        "positive_fraction",
    }

    missing = required - set(df.columns)
    if missing:
        print(f"ERROR: faltan columnas: {sorted(missing)}")
        return 1

    metrics = [
        "mean_forward_return",
        "median_forward_return",
        "positive_fraction",
    ]

    for column in metrics:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    keys = ["asset", "horizon_months"]
    results = []

    for (asset, horizon), group in df.groupby(keys, dropna=False):
        means = group["mean_forward_return"].dropna()
        medians = group["median_forward_return"].dropna()
        positive = group["positive_fraction"].dropna()

        results.append({
            "asset": asset,
            "horizon_months": horizon,
            "subperiods": group["subperiod"].nunique(),
            "total_observations": group["observations"].sum(),
            "mean_return_min": means.min(),
            "mean_return_max": means.max(),
            "mean_return_range": means.max() - means.min(),
            "positive_fraction_min": positive.min(),
            "positive_fraction_max": positive.max(),
            "positive_fraction_range": positive.max() - positive.min(),
            "all_period_means_positive": (
                len(means) == group["subperiod"].nunique()
                and (means > 0).all()
            ),
            "all_period_medians_positive": (
                len(medians) == group["subperiod"].nunique()
                and (medians > 0).all()
            ),
        })

    result = pd.DataFrame(results).sort_values(
        ["asset", "horizon_months"]
    )

    result.to_csv(OUTPUT_FILE, index=False)

    print("=== RESUMEN DE ESTABILIDAD ===")
    print(f"Combinaciones activo-horizonte: {len(result)}")
    print(f"Archivo generado: {OUTPUT_FILE}")
    print("\nMayor variación del retorno medio:")
    print(
        result.nlargest(10, "mean_return_range")[
            [
                "asset",
                "horizon_months",
                "mean_return_range",
                "positive_fraction_range",
                "all_period_means_positive",
            ]
        ].to_string(index=False)
    )

    print("\nMenor variación del retorno medio:")
    print(
        result.nsmallest(10, "mean_return_range")[
            [
                "asset",
                "horizon_months",
                "mean_return_range",
                "positive_fraction_range",
                "all_period_means_positive",
            ]
        ].to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())