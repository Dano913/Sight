from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.analysis.analysis_service import AnalysisService
from app.services.catalog.observation_service import ObservationService

router = APIRouter(
    prefix="/investment",
    tags=["Investment"],
)

INVESTMENT_INDICATORS = [
    "GDP",
    "INFLATION",
    "UNEMPLOYMENT",
    "INDUSTRIAL_PRODUCTION",
    "RETAIL_SALES",
    "HOUSE_PRICE_INDEX",
]


@router.get("/{region_code}")
def get_investment_analysis(
    region_code: str,
    as_of_date: str | None = None,
    max_lag_days: int | None = 180,
):
    try:
        clean_region = region_code.strip().upper()
        observations = []

        for indicator_code in INVESTMENT_INDICATORS:
            try:
                observations.extend(
                    ObservationService.get_observations(
                        indicator_code=indicator_code,
                        region_code=clean_region,
                    )
                )
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
