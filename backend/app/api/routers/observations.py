from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.observation import Observation
from app.services.catalog.observation_service import ObservationService
from app.services.catalog.query_service import QueryService

router = APIRouter(
    prefix="/observations",
    tags=["Observations"],
)


@router.get(
    "/{indicator_code}",
    response_model=list[Observation],
)
def get_observations(
    indicator_code: str,
    region: str | None = None,
):
    clean_indicator = indicator_code.strip().upper()
    clean_region = region.strip().upper() if region else None

    try:
        if clean_indicator == "TRADE":
            observations = QueryService._compute_trade_observations(
                region_code=clean_region,
            )
        else:
            observations = ObservationService.get_observations(
                clean_indicator,
                clean_region,
            )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e

    if not observations:
        target = f" en {clean_region}" if clean_region else ""
        raise HTTPException(
            status_code=404,
            detail=f"No existen observaciones para {clean_indicator}{target}",
        )

    return observations
