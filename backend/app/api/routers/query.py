from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.responses.indicator_response import IndicatorResponse
from app.responses.region_response import RegionResponse
from app.services.catalog.query_service import QueryService

router = APIRouter(
    prefix="/query",
    tags=["Query"],
)


@router.get(
    "/region/{region_code}",
    response_model=RegionResponse,
)
def get_by_region(region_code: str):
    """
    Devuelve todas las observaciones de una región.
    """
    try:
        return QueryService.get_by_region(
            region_code.strip().upper()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e


@router.get(
    "/indicator/{indicator_code}",
    response_model=IndicatorResponse,
)
def get_by_indicator(indicator_code: str):
    """
    Devuelve todas las observaciones de un indicador.
    """
    try:
        return QueryService.get_by_indicator(
            indicator_code.strip().upper()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e


@router.get(
    "/region/{region_code}/indicator/{indicator_code}",
    response_model=RegionResponse,
)
def get_by_region_and_indicator(
    region_code: str,
    indicator_code: str,
):
    """
    Devuelve una serie temporal concreta.
    """
    try:
        return QueryService.get_by_region_and_indicator(
            region_code.strip().upper(),
            indicator_code.strip().upper(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e


@router.get(
    "/compare",
    response_model=list[RegionResponse],
)
def compare(
    indicator: str,
    regions: str,
):
    """
    Compara las observaciones de un indicador entre múltiples regiones.
    """
    clean_indicator = indicator.strip().upper()
    region_list = [
        region.strip().upper()
        for region in regions.split(",")
        if region.strip()
    ]

    if not clean_indicator or not region_list:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar un indicador y al menos una región.",
        )

    try:
        return QueryService.compare_regions(
            clean_indicator,
            region_list,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e
