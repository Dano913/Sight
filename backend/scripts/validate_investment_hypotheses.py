from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

import pandas as pd

from app.services.analysis.analysis_service import AnalysisService
from app.services.analysis.investment.investment_analysis_service import (
    InvestmentAnalysisService,
)
from app.services.catalog.observation_service import ObservationService


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "validation" / "investment_hypotheses"

DEFAULT_INDICATORS = [
    "GDP",
    "INFLATION",
    "UNEMPLOYMENT",
    "INDUSTRIAL_PRODUCTION",
    "RETAIL_SALES",
    "HOUSE_PRICE_INDEX",
]

START_DATE = date(1975, 1, 1)
END_DATE = date(2015, 12, 31)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def json_value(value):
    """Convierte resultados del análisis a valores serializables."""
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]

    if isinstance(value, (date, pd.Timestamp)):
        return value.isoformat()

    if hasattr(value, "item"):
        return json_value(value.item())

    if pd.isna(value):
        return None

    return value


def load_observations(region_code: str) -> dict[str, list]:
    """Carga las observaciones de los indicadores disponibles."""
    observations_by_indicator = {}

    for indicator_code in DEFAULT_INDICATORS:
        try:
            observations = ObservationService.get_observations(
                indicator_code=indicator_code,
                region_code=region_code,
            )
        except (ValueError, KeyError) as exc:
            logger.warning(
                "No se pudieron cargar %s: %s",
                indicator_code,
                exc,
            )
            continue

        observations = [
            observation
            for observation in observations
            if START_DATE <= observation.date <= END_DATE
        ]

        observations.sort(key=lambda observation: observation.date)

        if observations:
            observations_by_indicator[indicator_code] = observations
            logger.info(
                "%s: %s observaciones",
                indicator_code,
                len(observations),
            )
        else:
            logger.warning(
                "%s: no hay observaciones en el periodo",
                indicator_code,
            )

    return observations_by_indicator


def build_evaluation_dates() -> list[date]:
    """Genera las fechas mensuales de evaluación."""
    return [
        timestamp.date()
        for timestamp in pd.date_range(
            start=START_DATE,
            end=END_DATE,
            freq="ME",
        )
    ]


def analyze_indicator(
    indicator_code: str,
    observations: list,
    cutoff_date: date,
) -> dict | None:
    """
    Analiza un indicador usando exclusivamente observaciones
    cuya fecha sea igual o anterior a la fecha de evaluación.
    """
    historical_observations = [
        observation
        for observation in observations
        if observation.date <= cutoff_date
    ]

    if not historical_observations:
        return None

    try:
        analysis = AnalysisService.analyze(historical_observations)

        investment_interpretation = analysis.get(
            "investment_interpretation"
        )

        if not investment_interpretation:
            return None

        investment_result = InvestmentAnalysisService.analyze(
            investment_interpretation
        )

        return {
            "analysis": analysis,
            "investment_interpretation": investment_interpretation,
            "investment_result": investment_result,
            "observations_used": len(historical_observations),
            "last_observation_date": max(
                observation.date
                for observation in historical_observations
            ),
        }

    except Exception:
        logger.exception(
            "Error analizando %s hasta %s",
            indicator_code,
            cutoff_date,
        )
        return None


def run_backtest(region_code: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    observations_by_indicator = load_observations(region_code)

    if not observations_by_indicator:
        raise RuntimeError(
            f"No hay observaciones disponibles para {region_code}."
        )

    evaluation_dates = build_evaluation_dates()
    hypothesis_rows = []
    error_count = 0

    total = len(evaluation_dates) * len(observations_by_indicator)
    completed = 0

    for cutoff_date in evaluation_dates:
        for indicator_code, observations in observations_by_indicator.items():
            completed += 1

            if completed % 100 == 0:
                logger.info(
                    "Progreso: %s/%s análisis",
                    completed,
                    total,
                )

            result = analyze_indicator(
                indicator_code=indicator_code,
                observations=observations,
                cutoff_date=cutoff_date,
            )

            if result is None:
                error_count += 1
                continue

            hypothesis_rows.append(
                {
                    "evaluation_date": cutoff_date.isoformat(),
                    "region_code": region_code,
                    "indicator_code": indicator_code,
                    "last_observation_date": (
                        result["last_observation_date"].isoformat()
                    ),
                    "observations_used": result["observations_used"],
                    "investment_interpretation": json.dumps(
                        json_value(result["investment_interpretation"]),
                        ensure_ascii=False,
                    ),
                    "investment_result": json.dumps(
                        json_value(result["investment_result"]),
                        ensure_ascii=False,
                    ),
                }
            )

    hypotheses_path = OUTPUT_DIR / "investment_hypotheses.csv"

    hypotheses_df = pd.DataFrame(hypothesis_rows)

    if hypotheses_df.empty:
        raise RuntimeError(
            "No se generaron hipótesis. Revisa las observaciones "
            "y los errores registrados."
        )

    hypotheses_df.to_csv(
        hypotheses_path,
        index=False,
        encoding="utf-8",
    )

    logger.info("Backtest finalizado.")
    logger.info("Análisis realizados: %s", len(hypotheses_df))
    logger.info("Análisis sin resultado: %s", error_count)
    logger.info("Hipótesis guardadas en: %s", hypotheses_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Valida históricamente las hipótesis de inversión de Sight."
        )
    )
    parser.add_argument(
        "--region",
        default="US",
        help="Código de región. Por defecto: US.",
    )
    args = parser.parse_args()

    run_backtest(args.region.upper())


if __name__ == "__main__":
    main()