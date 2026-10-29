from fastapi import APIRouter

from app.responses.region_response import RegionResponse
from app.responses.indicator_response import IndicatorResponse

from app.services.catalog.query_service import QueryService


router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


@router.get(
    "/region/{region_code}",
    response_model=RegionResponse
)
def get_by_region(region_code: str):
    """
    Devuelve todas las observaciones de una región.
    """

    return QueryService.get_by_region(
        region_code.upper()
    )


@router.get(
    "/indicator/{indicator_code}",
    response_model=IndicatorResponse
)
def get_by_indicator(indicator_code: str):
    """
    Devuelve todas las observaciones de un indicador.
    """

    return QueryService.get_by_indicator(
        indicator_code.upper()
    )


@router.get(
    "/region/{region_code}/indicator/{indicator_code}",
    response_model=RegionResponse
)
def get_by_region_and_indicator(
    region_code: str,
    indicator_code: str
):
    """
    Devuelve una serie temporal concreta.
    """

    return QueryService.get_by_region_and_indicator(
        region_code.upper(),
        indicator_code.upper()
    )


@router.get("/compare")
def compare(
    indicator: str,
    regions: str
):
    print("INDICATOR:", indicator)
    print("REGIONS:", regions)

    region_list = [
        region.strip().upper()
        for region in regions.split(",")
    ]

    return QueryService.compare_regions(
        indicator.upper(),
        region_list
    )