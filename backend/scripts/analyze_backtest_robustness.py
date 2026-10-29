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
    / "bootstrap_sensitivity.csv"
)

BLOCK_LENGTHS = [6, 12, 24]
N_BOOTSTRAPS = 2000
CONFIDENCE_LEVEL = 0.95
RANDOM_SEED = 42


def bootstrap_means(
    values: np.ndarray,
    block_length: int,
    n_bootstraps: int,
    rng: np.random.Generator,
) -> np.ndarray:
    n = len(values)
    block_length = min(block_length, n)
    blocks_needed = int(np.ceil(n / block_length))
    offsets = np.arange(block_length)

    means = np.empty(n_bootstraps)

    for i in range(n_bootstraps):
        starts = rng.integers(0, n, size=blocks_needed)
        indices = (starts[:, None] + offsets[None, :]) % n
        sample = values[indices.ravel()[:n]]
        means[i] = sample.mean()

    return means


def main() -> int:
    input_file = INPUT_FILE
    if not input_file.exists():
        gz_candidate = INPUT_FILE.with_name(INPUT_FILE.name + ".gz")
        if gz_candidate.exists():
            input_file = gz_candidate
        else:
            print(f"ERROR: no existe {INPUT_FILE}")
            return 1

    df = pd.read_csv(input_file)

    required = {"date", "asset", "horizon_months", "forward_return"}
    missing = required - set(df.columns)

    if missing:
        print(f"ERROR: faltan columnas: {sorted(missing)}")
        return 1

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["forward_return"] = pd.to_numeric(
        df["forward_return"], errors="coerce"
    )

    df = df.dropna(
        subset=["date", "asset", "horizon_months", "forward_return"]
    )

    rng = np.random.default_rng(RANDOM_SEED)
    alpha = 1 - CONFIDENCE_LEVEL
    results = []

    for (asset, horizon), group in df.groupby(
        ["asset", "horizon_months"], sort=True
    ):
        group = group.sort_values("date")

        # Evita calcular sobre series con fechas duplicadas o huecos
        # que harían que los bloques no representasen meses consecutivos.
        if group["date"].duplicated().any():
            print(
                f"AVISO: fechas duplicadas para {asset}, "
                f"horizonte {horizon}; se omite esta combinación."
            )
            continue

        dates = group["date"]
        month_index = dates.dt.year * 12 + dates.dt.month

        if len(month_index) > 1 and not np.all(
            np.diff(month_index.to_numpy()) == 1
        ):
            print(
                f"AVISO: serie mensual incompleta para {asset}, "
                f"horizonte {horizon}; se omite esta combinación."
            )
            continue

        values = group["forward_return"].to_numpy(dtype=float)

        if len(values) < max(BLOCK_LENGTHS) * 2:
            print(
                f"AVISO: muestra insuficiente para {asset}, "
                f"horizonte {horizon}; se omite."
            )
            continue

        for block_length in BLOCK_LENGTHS:
            means = bootstrap_means(
                values=values,
                block_length=block_length,
                n_bootstraps=N_BOOTSTRAPS,
                rng=rng,
            )

            lower, upper = np.quantile(
                means, [alpha / 2, 1 - alpha / 2]
            )

            results.append({
                "asset": asset,
                "horizon_months": horizon,
                "observations": len(values),
                "block_length_months": block_length,
                "bootstrap_repetitions": N_BOOTSTRAPS,
                "mean_return": values.mean(),
                "ci_lower": lower,
                "ci_upper": upper,
                "ci_width": upper - lower,
                "ci_excludes_zero": lower > 0 or upper < 0,
            })

    if not results:
        print("ERROR: no se han generado resultados.")
        return 1

    result = pd.DataFrame(results).sort_values(
        ["asset", "horizon_months", "block_length_months"]
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print("=== SENSIBILIDAD DEL BOOTSTRAP ===")
    print(f"Combinaciones calculadas: {len(result)}")
    print(f"Longitudes de bloque: {BLOCK_LENGTHS}")
    print(f"Réplicas por combinación: {N_BOOTSTRAPS}")
    print(f"Archivo generado: {OUTPUT_FILE}")

    print("\nBROAD_MARKET:")
    broad = result[result["asset"] == "BROAD_MARKET"]

    if broad.empty:
        print("No hay resultados para BROAD_MARKET.")
    else:
        print(
            broad[
                [
                    "horizon_months",
                    "block_length_months",
                    "mean_return",
                    "ci_lower",
                    "ci_upper",
                    "ci_width",
                    "ci_excludes_zero",
                ]
            ].to_string(index=False)
        )

    comparison = result.groupby(
        ["asset", "horizon_months"]
    ).agg(
        min_ci_lower=("ci_lower", "min"),
        max_ci_lower=("ci_lower", "max"),
        min_ci_upper=("ci_upper", "min"),
        max_ci_upper=("ci_upper", "max"),
        min_width=("ci_width", "min"),
        max_width=("ci_width", "max"),
        all_exclude_zero=("ci_excludes_zero", "all"),
        any_exclude_zero=("ci_excludes_zero", "any"),
    ).reset_index()

    print("\n=== RESUMEN DE ROBUSTEZ ===")
    print(
        "Combinaciones cuyos tres intervalos excluyen cero: "
        f"{comparison['all_exclude_zero'].sum()} "
        f"de {len(comparison)}"
    )
    print(
        "Combinaciones donde la conclusión sobre cero cambia: "
        f"{(
            comparison['all_exclude_zero']
            != comparison['any_exclude_zero']
        ).sum()}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())