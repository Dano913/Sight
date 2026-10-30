from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.source import Source
from app.services.catalog.source_service import SourceService

router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


@router.get("", response_model=list[Source])
@router.get("/", response_model=list[Source], include_in_schema=False)
def get_sources():
    return SourceService.get_sources()


@router.get("/{code}", response_model=Source)
def get_source(code: str):
    try:
        return SourceService.get_by_code(code)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e
