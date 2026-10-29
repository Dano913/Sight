from fastapi import APIRouter, HTTPException

import pandas as pd

from app.models.cycle_analysis import CycleAnalysisResult
from app.models.feature_analysis import FeatureAnalysisResult
from app.services.analysis.cycle.cycle_analysis_service import CycleAnalysisService
from app.services.features.feature_engine import FeatureEngine
from app.services.catalog.observation_service import ObservationService
from app.services.catalog.indicator_service import IndicatorService
from app.services.analysis.analysis_service import AnalysisService
from app.services.analysis.investment.investment_analysis_service import (
    InvestmentAnalysisService,
)

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


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
        observations = ObservationService.get_observations(
            indicator_code=indicator_code,
            region_code=region_code,
        )

        if not observations:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No hay observaciones para "
                    f"{indicator_code} en {region_code}"
                ),
            )

        result = CycleAnalysisService.analyze(observations)

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


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
        observations = ObservationService.get_observations(
            indicator_code=indicator_code,
            region_code=region_code,
        )

        if not observations:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No hay observaciones para "
                    f"{indicator_code} en {region_code}"
                ),
            )

        # Obtener metadatos del indicador
        indicator = IndicatorService.get_indicator(indicator_code)

        if not indicator:
            raise HTTPException(
                status_code=404,
                detail=f"Indicador no encontrado: {indicator_code}",
            )

        frequency = indicator.frequency.value

        # --------------------------------------------------
        # Convertir observaciones a serie temporal
        # --------------------------------------------------

        series = pd.Series(
            data=[observation.value for observation in observations],
            index=pd.to_datetime(
                [observation.date for observation in observations]
            ),
            dtype="float64",
        )

        series = series.sort_index()

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
            "indicator_code": indicator_code.upper(),
            "region_code": region_code.upper(),
            "observations": feature_observations,
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

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
                    region_code=region_code,
                )

                observations.extend(indicator_observations)

            except ValueError as e:
                print(
                    f"[{indicator_code}] No disponible: {e}"
                )

        if not observations:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No hay observaciones disponibles "
                    f"para {region_code}"
                ),
            )

        result = AnalysisService.analyze_multiple(
            observations,
            as_of_date=as_of_date,
            max_lag_days=max_lag_days,
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
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
        observations = ObservationService.get_observations(
            indicator_code=indicator_code,
            region_code=region_code,
        )

        if not observations:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No hay observaciones para "
                    f"{indicator_code} en {region_code}"
                ),
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
        )

    except Exception as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )