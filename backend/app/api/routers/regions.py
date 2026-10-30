from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.region import Region
from app.services.catalog.region_service import RegionService

router = APIRouter(
    prefix="/regions",
    tags=["Regions"],
)


@router.get("", response_model=list[Region])
@router.get("/", response_model=list[Region], include_in_schema=False)
def get_regions():
    return RegionService.get_regions()


@router.get("/{code}", response_model=Region)
def get_region(code: str):
    try:
        return RegionService.get_region(code)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e
