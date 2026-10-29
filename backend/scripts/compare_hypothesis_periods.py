from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "validation" / "investment_hypotheses"

INPUT_FILE = DATA_DIR / "hypothesis_forward_returns.csv"
OUTPUT_FILE = DATA_DIR / "robustness_by_period.csv"

START_DATE = "1975-01-01"
END_DATE = "2015-12-31"
FIRST_PERIOD_END = "1995-12-31"

HORIZON_MONTHS = 12
BLOCK_LENGTH = 12
BOOTSTRAP_REPLICATES = 1000
CONFIDENCE_LEVEL = 0.95
RANDOM_SEED = 42

# Dimensiones de hipótesis.
# Nota: 'assessment' se ha unificado con 'macro_bias' para eliminar duplicados redundantes.
DIMENSIONS = [
    "direction",
    "macro_bias",
    "regime",
    "confidence",
    "conviction",
]

GROUP_COLUMNS = [
    "period",
    "asset",
    "market_file",
    "market_value_type",
    "horizon_months",
    "indicator_code",
    "hypothesis_dimension",
    "hypothesis_category",
]


def assign_period(date: pd.Timestamp) -> str:
    if date <= pd.Timestamp(FIRST_PERIOD_END):
        return "1975-1995"

    return "1996-2015"


def moving_block_indices(
    n: int,
    block_length: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Genera índices bootstrap mediante bloques circulares."""
    blocks_needed = int(np.ceil(n / block_length))
    starts = rng.integers(0, n, size=blocks_needed)

    indices = np.concatenate(
        [
            (start + np.arange(block_length)) % n
            for start in starts
        ]
    )

    return indices[:n]


def bootstrap_difference(
    category_values: np.ndarray,
    baseline_values: np.ndarray,
    rng: np.random.Generator,
) -> tuple[float, float, int]:
    """
    Estima un intervalo de confianza para la diferencia de medias.

    Las dos series están alineadas por fecha. Los bloques mantienen
    parte de la dependencia temporal de las rentabilidades solapadas.
    """
    valid = np.isfinite(baseline_values)

    category_values = category_values[valid]
    baseline_values = baseline_values[valid]

    n = len(baseline_values)

    if n < 2 or not np.isfinite(category_values).any():
        return np.nan, np.nan, 0

    differences = []

    for _ in range(BOOTSTRAP_REPLICATES):
        indices = moving_block_indices(
            n,
            min(BLOCK_LENGTH, n),
            rng,
        )

        sampled_category = category_values[indices]
        sampled_baseline = baseline_values[indices]

        valid_category = sampled_category[~np.isnan(sampled_category)]

        if len(valid_category) == 0:
            continue

        category_mean = np.mean(valid_category)
        baseline_mean = np.mean(sampled_baseline)

        if np.isfinite(category_mean) and np.isfinite(baseline_mean):
            differences.append(category_mean - baseline_mean)

    if len(differences) < 100:
        return np.nan, np.nan, len(differences)

    alpha = 1 - CONFIDENCE_LEVEL

    lower, upper = np.quantile(
        differences,
        [alpha / 2, 1 - alpha / 2],
    )

    return float(lower), float(upper), len(differences)


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"No existe el archivo: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, parse_dates=["evaluation_date"])

    required = {
        "evaluation_date",
        "region_code",
        "asset",
        "market_file",
        "market_value_type",
        "horizon_months",
        "indicator_code",
        "forward_return",
        *DIMENSIONS,
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Faltan columnas: {sorted(missing)}")

    df = df[
        df["evaluation_date"].between(START_DATE, END_DATE)
        & (df["horizon_months"] == HORIZON_MONTHS)
        & df["region_code"].eq("US")
    ].copy()

    df = df.dropna(subset=["evaluation_date", "forward_return"])

    if df.empty:
        raise ValueError("No hay rentabilidades disponibles para analizar.")

    df["period"] = df["evaluation_date"].apply(assign_period)

    # Referencia: una rentabilidad por fecha y activo.
    market_keys = [
        "period",
        "evaluation_date",
        "asset",
        "market_file",
        "market_value_type",
    ]

    market = (
        df[market_keys + ["forward_return"]]
        .drop_duplicates(subset=market_keys)
        .sort_values("evaluation_date")
    )

    rng = np.random.default_rng(RANDOM_SEED)
    results = []

    for dimension in DIMENSIONS:
        keys = [
            "period",
            "asset",
            "market_file",
            "market_value_type",
            "indicator_code",
            dimension,
        ]

        for group_key, category_df in df.groupby(
            keys,
            dropna=False,
            sort=False,
        ):
            (
                period,
                asset,
                market_file,
                market_value_type,
                indicator_code,
                category,
            ) = group_key

            baseline = market[
                (market["period"] == period)
                & (market["asset"] == asset)
                & (market["market_file"] == market_file)
                & (market["market_value_type"] == market_value_type)
            ].copy()

            if baseline.empty:
                continue

            category_dates = category_df[
                ["evaluation_date", "forward_return"]
            ].drop_duplicates(subset=["evaluation_date"])

            category_dates = category_dates.rename(
                columns={"forward_return": "category_return"}
            )

            aligned = baseline.merge(
                category_dates,
                on="evaluation_date",
                how="left",
                validate="one_to_one",
            )

            category_values = aligned["category_return"].to_numpy(
                dtype=float
            )
            baseline_values = aligned["forward_return"].to_numpy(
                dtype=float
            )

            observed = category_values[np.isfinite(category_values)]

            if len(observed) == 0:
                continue

            lower, upper, valid_replicates = bootstrap_difference(
                category_values,
                baseline_values,
                rng,
            )

            baseline_mean = float(np.mean(baseline_values))
            category_mean = float(np.mean(observed))

            results.append(
                {
                    "period": period,
                    "asset": asset,
                    "market_file": market_file,
                    "market_value_type": market_value_type,
                    "horizon_months": HORIZON_MONTHS,
                    "indicator_code": indicator_code,
                    "hypothesis_dimension": dimension,
                    "hypothesis_category": category,
                    "observations": len(observed),
                    "mean_forward_return": category_mean,
                    "median_forward_return": float(np.median(observed)),
                    "positive_fraction": float(np.mean(observed > 0)),
                    "baseline_observations": len(baseline_values),
                    "baseline_mean_return": baseline_mean,
                    "baseline_median_return": float(
                        np.median(baseline_values)
                    ),
                    "baseline_positive_fraction": float(
                        np.mean(baseline_values > 0)
                    ),
                    "mean_return_difference": (
                        category_mean - baseline_mean
                    ),
                    "ci_lower_95": lower,
                    "ci_upper_95": upper,
                    "bootstrap_replicates_valid": valid_replicates,
                    "block_length_months": BLOCK_LENGTH,
                }
            )

    summary = pd.DataFrame(results)

    if summary.empty:
        raise ValueError("No se han podido generar resultados.")

    summary = summary.sort_values(
        [
            "period",
            "asset",
            "indicator_code",
            "hypothesis_dimension",
        ]
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_FILE, index=False)

    print(f"Archivo generado: {OUTPUT_FILE}")
    print(f"Filas generadas: {len(summary)}")
    print(f"Réplicas bootstrap solicitadas: {BOOTSTRAP_REPLICATES}")
    print(f"Longitud de bloque: {BLOCK_LENGTH} meses")
    print(f"Semilla aleatoria: {RANDOM_SEED}")

    print("\nEjemplo: GDP / BROAD_MARKET / macro_bias")

    example = summary[
        summary["asset"].eq("BROAD_MARKET")
        & summary["indicator_code"].eq("GDP")
        & summary["hypothesis_dimension"].eq("macro_bias")
    ]

    columns = [
        "period",
        "hypothesis_category",
        "observations",
        "mean_forward_return",
        "median_forward_return",
        "positive_fraction",
        "mean_return_difference",
        "ci_lower_95",
        "ci_upper_95",
    ]

    print(example[columns].to_string(index=False))


if __name__ == "__main__":
    main()