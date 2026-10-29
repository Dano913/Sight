from pathlib import Path

import numpy as np
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
    / "uncertainty_by_asset_horizon.csv"
)

N_BOOTSTRAPS = 2000
BLOCK_LENGTH = 12
CONFIDENCE_LEVEL = 0.95
RANDOM_SEED = 42


def circular_block_bootstrap_means(
    values: np.ndarray,
    n_bootstraps: int,
    block_length: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Estima medias mediante bloques temporales circulares."""
    n = len(values)

    if n == 0:
        return np.array([])

    block_length = min(block_length, n)
    blocks_needed = int(np.ceil(n / block_length))
    offsets = np.arange(block_length)

    bootstrap_means = np.empty(n_bootstraps)

    for i in range(n_bootstraps):
        starts = rng.integers(0, n, size=blocks_needed)

        indices = (
            starts[:, None] + offsets[None, :]
        ) % n

        sample = values[indices.ravel()[:n]]
        bootstrap_means[i] = sample.mean()

    return bootstrap_means


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

    required = {
        "date",
        "asset",
        "horizon_months",
        "forward_return",
    }

    missing = required - set(df.columns)

    if missing:
        print(f"ERROR: faltan columnas: {sorted(missing)}")
        return 1

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["forward_return"] = pd.to_numeric(
        df["forward_return"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "date",
            "asset",
            "horizon_months",
            "forward_return",
        ]
    )

    df = df.sort_values("date")

    rng = np.random.default_rng(RANDOM_SEED)
    alpha = 1 - CONFIDENCE_LEVEL
    results = []

    for (asset, horizon), group in df.groupby(
        ["asset", "horizon_months"],
        sort=True,
    ):
        group = group.sort_values("date")
        values = group["forward_return"].to_numpy(dtype=float)
        n = len(values)

        if n < 2:
            continue

        bootstrap_means = circular_block_bootstrap_means(
            values=values,
            n_bootstraps=N_BOOTSTRAPS,
            block_length=BLOCK_LENGTH,
            rng=rng,
        )

        lower = np.quantile(bootstrap_means, alpha / 2)
        upper = np.quantile(bootstrap_means, 1 - alpha / 2)

        results.append(
            {
                "asset": asset,
                "horizon_months": horizon,
                "observations": n,
                "mean_return": values.mean(),
                "median_return": np.median(values),
                "block_length_months": BLOCK_LENGTH,
                "bootstrap_repetitions": N_BOOTSTRAPS,
                "confidence_level": CONFIDENCE_LEVEL,
                "ci_lower": lower,
                "ci_upper": upper,
                "ci_width": upper - lower,
                "ci_excludes_zero": lower > 0 or upper < 0,
            }
        )

    if not results:
        print("ERROR: no se han podido calcular resultados.")
        return 1

    result = pd.DataFrame(results).sort_values(
        ["asset", "horizon_months"]
    )

    result.to_csv(OUTPUT_FILE, index=False)

    print("=== INCERTIDUMBRE ESTADÍSTICA ===")
    print(f"Filas válidas: {len(df)}")
    print(f"Combinaciones activo-horizonte: {len(result)}")
    print(f"Réplicas bootstrap: {N_BOOTSTRAPS}")
    print(f"Longitud de bloque: {BLOCK_LENGTH} meses")
    print(f"Archivo generado: {OUTPUT_FILE}")

    print("\nEjemplo: BROAD_MARKET")
    example = result[result["asset"] == "BROAD_MARKET"]

    if not example.empty:
        print(
            example[
                [
                    "horizon_months",
                    "observations",
                    "mean_return",
                    "ci_lower",
                    "ci_upper",
                    "ci_width",
                    "ci_excludes_zero",
                ]
            ].to_string(index=False)
        )

    print("\nIntervalos más amplios:")
    print(
        result.nlargest(10, "ci_width")[
            [
                "asset",
                "horizon_months",
                "mean_return",
                "ci_lower",
                "ci_upper",
                "ci_width",
            ]
        ].to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())