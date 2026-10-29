#!/usr/bin/env python3
"""
Contrasta las hipótesis históricas de Sight con retornos futuros.

Ejecutar desde backend/:
    python -m scripts.validate_investment_hypothesis_returns --region US

Entradas:
    data/validation/investment_hypotheses/investment_hypotheses.csv
    data/validation/market/*.csv

Salidas:
    data/validation/investment_hypotheses/
        hypothesis_forward_returns.csv
        summary_by_hypothesis.csv
        market_baseline.csv

No modifica la base de datos ni el código de producción.

Limitaciones:
- No elimina el sesgo de revisiones de los datos macroeconómicos.
- No comprueba las fechas históricas de publicación de cada dato.
- Una asociación histórica no demuestra capacidad predictiva.
- Los índices de precios y los índices de retorno total se analizan
  por separado.
- Los yields anualizados no se tratan como retornos de activos.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = (
    BASE_DIR / "data" / "validation" / "investment_hypotheses"
)
HYPOTHESES_PATH = INPUT_DIR / "investment_hypotheses.csv"
MARKET_DIR = BASE_DIR / "data" / "validation" / "market"

START_DATE = pd.Timestamp("1975-01-01")
END_DATE = pd.Timestamp("2015-12-31")

HORIZONS = (3, 6, 12, 24)

# Campos que se contrastarán con los retornos futuros.
# Nota: 'assessment' se ha unificado con 'macro_bias' al ser un alias idéntico.
HYPOTHESIS_DIMENSIONS = (
    "direction",
    "macro_bias",
    "regime",
    "confidence",
    "conviction",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def stop(message: str) -> None:
    raise RuntimeError(message)


def load_hypotheses(region_code: str) -> pd.DataFrame:
    """Carga las hipótesis previamente calculadas por Sight."""
    if not HYPOTHESES_PATH.exists():
        stop(
            f"No existe el archivo de hipótesis: {HYPOTHESES_PATH}\n"
            "Ejecuta primero:\n"
            "python -m scripts.validate_investment_hypotheses "
            f"--region {region_code}"
        )

    df = pd.read_csv(HYPOTHESES_PATH)

    required = {
        "evaluation_date",
        "region_code",
        "indicator_code",
        "investment_result",
    }

    missing = required - set(df.columns)

    if missing:
        stop(
            "Faltan columnas en el archivo de hipótesis: "
            + ", ".join(sorted(missing))
        )

    df["evaluation_date"] = pd.to_datetime(
        df["evaluation_date"],
        errors="coerce",
    )

    df["region_code"] = (
        df["region_code"].astype(str).str.upper()
    )

    df["indicator_code"] = (
        df["indicator_code"].astype(str).str.upper()
    )

    df = df[
        (df["region_code"] == region_code)
        & df["evaluation_date"].notna()
        & df["evaluation_date"].between(START_DATE, END_DATE)
    ].copy()

    if df.empty:
        stop(
            f"No hay hipótesis para {region_code} entre "
            f"{START_DATE.date()} y {END_DATE.date()}."
        )

    df["investment_result"] = df["investment_result"].apply(
        parse_json
    )

    # Extraemos las categorías que se contrastarán con los retornos.
    for dimension in HYPOTHESIS_DIMENSIONS:
        df[dimension] = df["investment_result"].apply(
            lambda result: extract_dimension(result, dimension)
        )

    logger.info("Hipótesis cargadas: %s", len(df))
    logger.info(
        "Indicadores: %s",
        ", ".join(sorted(df["indicator_code"].unique())),
    )
    logger.info(
        "Fechas: %s a %s",
        df["evaluation_date"].min().date(),
        df["evaluation_date"].max().date(),
    )

    return df


def parse_json(value: Any) -> dict[str, Any]:
    """Convierte el JSON almacenado en el CSV en un diccionario."""
    if isinstance(value, dict):
        return value

    if not isinstance(value, str) or not value.strip():
        return {}

    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

    return parsed if isinstance(parsed, dict) else {}


def extract_dimension(
    result: dict[str, Any],
    dimension: str,
) -> str:
    """
    Obtiene una categoría de overall o, para el régimen,
    del resultado principal o de la interpretación macro.
    """
    overall = result.get("overall", {})
    if not isinstance(overall, dict):
        overall = {}

    if dimension in overall:
        value = overall.get(dimension)

    elif dimension == "regime":
        value = result.get("regime")

        if value is None:
            interpretation = result.get(
                "investment_interpretation", {}
            )
            if isinstance(interpretation, dict):
                value = interpretation.get("regime")

        if value is None:
            value = result.get("transition")

    else:
        value = None

    if value is None:
        return "UNKNOWN"

    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
        )

    text = str(value).strip()

    return text if text else "UNKNOWN"


def load_market_series() -> dict[str, dict[str, Any]]:
    """
    Carga series comparables de los CSV de mercado.

    Solo admite índices de retorno total e índices de precios.
    Los yields y otras series no comparables quedan excluidos.
    """
    if not MARKET_DIR.exists():
        stop(f"No existe el directorio: {MARKET_DIR}")

    markets: dict[str, dict[str, Any]] = {}

    for path in sorted(MARKET_DIR.glob("*.csv")):
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
        except (OSError, pd.errors.ParserError) as exc:
            logger.warning(
                "No se pudo leer %s: %s",
                path.name,
                exc,
            )
            continue

        df.columns = [
            str(column).strip().lower()
            for column in df.columns
        ]

        required = {"date", "asset", "value", "value_type"}

        if not required.issubset(df.columns):
            continue

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce",
        )
        df["value"] = pd.to_numeric(
            df["value"],
            errors="coerce",
        )
        df["asset"] = df["asset"].astype(str).str.upper()
        df["value_type"] = (
            df["value_type"].astype(str).str.lower()
        )

        df = df.dropna(subset=["date", "value"])

        df = df[
            df["value_type"].isin(
                {"total_return_index", "price_index"}
            )
        ]

        for asset, group in df.groupby("asset"):
            group = (
                group.sort_values("date")
                .drop_duplicates("date", keep="last")
                .set_index("date")
            )

            if group.empty:
                continue

            value_types = group["value_type"].unique()

            if len(value_types) != 1:
                logger.warning(
                    "Se omite %s de %s: tiene varios value_type.",
                    asset,
                    path.name,
                )
                continue

            # Si un mismo activo aparece en varios archivos,
            # no sobrescribimos silenciosamente la serie anterior.
            if asset in markets:
                previous = markets[asset]["file"]
                logger.warning(
                    "Activo duplicado %s en %s y %s; "
                    "se conserva el primero.",
                    asset,
                    previous,
                    path.name,
                )
                continue

            markets[asset] = {
                "frame": group,
                "value_type": str(value_types[0]),
                "file": path.name,
            }

    if not markets:
        stop(
            "No se encontraron series de mercado comparables "
            "con value_type total_return_index o price_index."
        )

    logger.info("Series de mercado: %s", len(markets))

    for asset, market in sorted(markets.items()):
        frame = market["frame"]
        logger.info(
            "  %s | %s | %s | %s",
            asset,
            market["value_type"],
            frame.index.min().date(),
            frame.index.max().date(),
        )

    return markets


def forward_return(
    market: dict[str, Any],
    signal_date: pd.Timestamp,
    months: int,
) -> float | None:
    """
    Replica la lógica temporal del primer backtest.

    Inicio: último dato disponible en la fecha de señal.
    Final: primer dato disponible en la fecha objetivo o posterior.
    """
    frame = market["frame"]

    available = frame.loc[frame.index <= signal_date]

    if available.empty:
        return None

    start_date = available.index[-1]
    target_date = signal_date + pd.DateOffset(months=months)

    future = frame.loc[frame.index >= target_date]

    if future.empty:
        return None

    start_value = float(frame.loc[start_date, "value"])
    end_value = float(future.iloc[0]["value"])

    if start_value == 0:
        return None

    return end_value / start_value - 1.0


def calculate_forward_returns(
    hypotheses: pd.DataFrame,
    markets: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Calcula los retornos posteriores a cada hipótesis."""
    rows: list[dict[str, Any]] = []

    for number, (_, hypothesis) in enumerate(
        hypotheses.iterrows(),
        start=1,
    ):
        evaluation_date = hypothesis["evaluation_date"]

        for asset, market in markets.items():
            for horizon in HORIZONS:
                result = forward_return(
                    market,
                    evaluation_date,
                    horizon,
                )

                if result is None:
                    continue

                row = {
                    "evaluation_date": evaluation_date.date().isoformat(),
                    "region_code": hypothesis["region_code"],
                    "indicator_code": hypothesis["indicator_code"],
                    "asset": asset,
                    "market_file": market["file"],
                    "market_value_type": market["value_type"],
                    "horizon_months": horizon,
                    "forward_return": result,
                }

                for dimension in HYPOTHESIS_DIMENSIONS:
                    row[dimension] = hypothesis[dimension]

                rows.append(row)

        if number % 100 == 0:
            logger.info(
                "Hipótesis procesadas: %s/%s",
                number,
                len(hypotheses),
            )

    result_df = pd.DataFrame(rows)

    if result_df.empty:
        stop(
            "No se pudieron calcular retornos futuros. "
            "Comprueba el periodo de las series de mercado."
        )

    return result_df


def calculate_market_baseline(
    hypotheses: pd.DataFrame,
    markets: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """
    Calcula la referencia de mercado por activo y horizonte.

    Cada fecha mensual se cuenta una sola vez, evitando que una fecha
    pese más por tener hipótesis para varios indicadores.
    """
    dates = sorted(
        pd.Timestamp(value)
        for value in hypotheses["evaluation_date"].dropna().unique()
    )

    rows: list[dict[str, Any]] = []

    for asset, market in markets.items():
        for horizon in HORIZONS:
            for evaluation_date in dates:
                value = forward_return(
                    market,
                    evaluation_date,
                    horizon,
                )

                if value is None:
                    continue

                rows.append({
                    "evaluation_date": evaluation_date.date().isoformat(),
                    "asset": asset,
                    "market_file": market["file"],
                    "market_value_type": market["value_type"],
                    "horizon_months": horizon,
                    "forward_return": value,
                })

    baseline = pd.DataFrame(rows)

    if baseline.empty:
        stop("No se pudieron calcular los retornos de referencia.")

    return (
        baseline.groupby(
            ["asset", "market_file", "market_value_type", "horizon_months"],
            dropna=False,
        )
        .agg(
            baseline_observations=("forward_return", "count"),
            baseline_mean_return=("forward_return", "mean"),
            baseline_median_return=("forward_return", "median"),
            baseline_positive_fraction=(
                "forward_return",
                lambda values: float((values > 0).mean()),
            ),
        )
        .reset_index()
    )


def summarize_hypotheses(
    details: pd.DataFrame,
    baseline: pd.DataFrame,
) -> pd.DataFrame:
    """
    Resume los retornos por indicador y categoría de hipótesis.

    Cada fila representa una dimensión y una categoría concreta.
    """
    grouping_columns = [
        "asset",
        "market_file",
        "market_value_type",
        "horizon_months",
        "indicator_code",
    ]

    grouped_rows: list[pd.DataFrame] = []

    for dimension in HYPOTHESIS_DIMENSIONS:
        group_columns = grouping_columns + [dimension]

        summary = (
            details.groupby(group_columns, dropna=False)
            .agg(
                observations=("forward_return", "count"),
                mean_forward_return=("forward_return", "mean"),
                median_forward_return=("forward_return", "median"),
                positive_fraction=(
                    "forward_return",
                    lambda values: float((values > 0).mean()),
                ),
                first_evaluation_date=("evaluation_date", "min"),
                last_evaluation_date=("evaluation_date", "max"),
            )
            .reset_index()
            .rename(columns={dimension: "hypothesis_category"})
        )

        summary["hypothesis_dimension"] = dimension
        grouped_rows.append(summary)

    combined = pd.concat(grouped_rows, ignore_index=True)

    combined = combined.merge(
        baseline,
        on=[
            "asset",
            "market_file",
            "market_value_type",
            "horizon_months",
        ],
        how="left",
        validate="many_to_one",
    )

    combined["mean_return_difference"] = (
        combined["mean_forward_return"]
        - combined["baseline_mean_return"]
    )

    combined["positive_fraction_difference"] = (
        combined["positive_fraction"]
        - combined["baseline_positive_fraction"]
    )

    return combined.sort_values(
        [
            "asset",
            "horizon_months",
            "indicator_code",
            "hypothesis_dimension",
            "hypothesis_category",
        ]
    )


def run(region_code: str) -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    hypotheses = load_hypotheses(region_code)
    markets = load_market_series()

    details = calculate_forward_returns(hypotheses, markets)
    baseline = calculate_market_baseline(hypotheses, markets)
    summary = summarize_hypotheses(details, baseline)

    details_path = INPUT_DIR / "hypothesis_forward_returns.csv"
    baseline_path = INPUT_DIR / "market_baseline.csv"
    summary_path = INPUT_DIR / "summary_by_hypothesis.csv"

    details.to_csv(
        details_path,
        index=False,
        encoding="utf-8",
    )
    baseline.to_csv(
        baseline_path,
        index=False,
        encoding="utf-8",
    )
    summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8",
    )

    print("\n=== VALIDACIÓN DE HIPÓTESIS ===")
    print(f"Región: {region_code}")
    print(f"Hipótesis cargadas: {len(hypotheses):,}")
    print(f"Series de mercado: {len(markets)}")
    print(f"Retornos calculados: {len(details):,}")
    print(f"Filas de resumen: {len(summary):,}")

    print("\nArchivos generados:")
    print(f"- {details_path}")
    print(f"- {summary_path}")
    print(f"- {baseline_path}")

    print(
        "\nLIMITACIONES: el retorno posterior no demuestra causalidad "
        "ni capacidad predictiva. La evaluación utiliza fechas de "
        "observación, no fechas históricas de publicación, y los "
        "datos macroeconómicos pueden haber sido revisados "
        "posteriormente."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Contrasta las hipótesis históricas de Sight "
            "con retornos futuros de mercado."
        )
    )
    parser.add_argument(
        "--region",
        default="US",
        help="Código de región. Por defecto: US.",
    )

    args = parser.parse_args()
    run(args.region.strip().upper())


if __name__ == "__main__":
    main()