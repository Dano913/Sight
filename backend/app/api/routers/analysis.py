from __future__ import annotations

from fastapi import APIRouter, HTTPException
import pandas as pd

from app.models.cycle_analysis import CycleAnalysisResult
from app.models.feature_analysis import FeatureAnalysisResult
from app.models.indicator import Indicator
from app.models.observation import Observation
from app.services.analysis.analysis_service import AnalysisService
from app.services.analysis.cycle.cycle_analysis_service import (
    CycleAnalysisService,
)
from app.services.analysis.investment.investment_analysis_service import (
    InvestmentAnalysisService,
)
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.observation_service import ObservationService
from app.services.catalog.query_service import QueryService
from app.services.features.feature_engine import FeatureEngine

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


def _get_observations_for_analysis(
    indicator_code: str,
    region_code: str,
) -> tuple[Indicator, list[Observation]]:
    """
    Valida el indicador y recupera sus observaciones (incluyendo el
    indicador sintético TRADE) para la región solicitada.
    """
    clean_indicator = indicator_code.strip().upper()
    clean_region = region_code.strip().upper()

    try:
        indicator = IndicatorService.get_indicator(clean_indicator)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e

    try:
        if clean_indicator == "TRADE":
            observations = QueryService._compute_trade_observations(
                region_code=clean_region,
            )
        else:
            observations = ObservationService.get_observations(
                indicator_code=clean_indicator,
                region_code=clean_region,
            )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e

    if not observations:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No hay observaciones para "
                f"{clean_indicator} en {clean_region}"
            ),
        )

    return indicator, observations


# ======================================================
# CYCLE ANALYSIS
# ======================================================

@router.get(
    "/cycle/{indicator_code}/{region_code}",
    response_model=CycleAnalysisResult,
)
def get_cycle_analysis(
    indicator_code: str,
    region_code: str,
):
    try:
        _, observations = _get_observations_for_analysis(
            indicator_code=indicator_code,
            region_code=region_code,
        )

        return CycleAnalysisService.analyze(observations)

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        ) from e


# ======================================================
# FEATURE ANALYSIS
# ======================================================

@router.get(
    "/features/{indicator_code}/{region_code}",
    response_model=FeatureAnalysisResult,
)
def get_feature_analysis(
    indicator_code: str,
    region_code: str,
):
    try:
        indicator, observations = _get_observations_for_analysis(
            indicator_code=indicator_code,
            region_code=region_code,
        )

        frequency = indicator.frequency.value

        # --------------------------------------------------
        # Convertir observaciones a serie temporal única y ordenada
        # --------------------------------------------------

        series = pd.Series(
            data=[observation.value for observation in observations],
            index=pd.to_datetime(
                [observation.date for observation in observations]
            ),
            dtype="float64",
        )

        series = series.sort_index().groupby(level=0).last()

        # --------------------------------------------------
        # Generar features
        # --------------------------------------------------

        features = FeatureEngine.compute(
            series=series,
            frequency=frequency,
            growth_method=indicator.growth_method,
        )

        # --------------------------------------------------
        # Serializar resultado
        # --------------------------------------------------

        feature_observations = []

        for index, row in features.iterrows():
            values = {}

            for column, value in row.items():
                if pd.isna(value):
                    values[column] = None

                elif hasattr(value, "item"):
                    values[column] = value.item()

                else:
                    values[column] = value

            feature_observations.append(
                {
                    "date": str(index),
                    "features": values,
                }
            )

        return {
            "indicator_code": indicator_code.strip().upper(),
            "region_code": region_code.strip().upper(),
            "observations": feature_observations,
        }

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        ) from e


# ======================================================
# MACRO REGIME
# ======================================================

@router.get("/regime/{region_code}")
def get_macro_regime(
    region_code: str,
    as_of_date: str | None = None,
    max_lag_days: int | None = 180,
):
    try:
        clean_region = region_code.strip().upper()
        indicator_codes = [
            "GDP",
            "INFLATION",
            "UNEMPLOYMENT",
            "INDUSTRIAL_PRODUCTION",
            "RETAIL_SALES",
            "HOUSE_PRICE_INDEX",
        ]

        observations = []

        for indicator_code in indicator_codes:
            try:
                indicator_observations = ObservationService.get_observations(
                    indicator_code=indicator_code,
                    region_code=clean_region,
                )

                observations.extend(indicator_observations)

            except ValueError:
                continue

        if not observations:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No hay observaciones disponibles "
                    f"para {clean_region}"
                ),
            )

        return AnalysisService.analyze_multiple(
            observations,
            as_of_date=as_of_date,
            max_lag_days=max_lag_days,
        )

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        ) from e


# ======================================================
# INVESTMENT THESIS
# ======================================================

@router.get(
    "/investment/{indicator_code}/{region_code}",
)
def get_investment_analysis(
    indicator_code: str,
    region_code: str,
):
    try:
        _, observations = _get_observations_for_analysis(
            indicator_code=indicator_code,
            region_code=region_code,
        )

        analysis = AnalysisService.analyze(
            observations,
        )

        result = analysis.get("investment_analysis")
        if not result:
            investment_interpretation = analysis.get(
                "investment_interpretation"
            )
            if not investment_interpretation:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "No se pudo generar la interpretación "
                        "de inversión."
                    ),
                )
            result = InvestmentAnalysisService.analyze(
                investment_interpretation
            )

        return result

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        ) from e
