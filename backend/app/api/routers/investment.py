from fastapi import APIRouter

from app.services.analysis.analysis_service import AnalysisService
from app.services.catalog.observation_service import ObservationService


router = APIRouter(
    prefix="/investment",
    tags=["investment"],
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
    observations = []

    for indicator_code in INVESTMENT_INDICATORS:
        observations.extend(
            ObservationService.get_observations(
                indicator_code=indicator_code,
                region_code=region_code.upper(),
            )
        )

    return AnalysisService.analyze_multiple(
        observations,
        as_of_date=as_of_date,
        max_lag_days=max_lag_days,
    )