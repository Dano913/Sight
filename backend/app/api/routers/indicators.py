from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.indicator import Indicator
from app.services.catalog.indicator_service import IndicatorService

router = APIRouter(
    prefix="/indicators",
    tags=["Indicators"],
)


@router.get("", response_model=list[Indicator])
@router.get("/", response_model=list[Indicator], include_in_schema=False)
def get_indicators():
    return IndicatorService.get_indicators()


@router.get("/{code}", response_model=Indicator)
def get_indicator(code: str):
    try:
        return IndicatorService.get_indicator(code)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e
