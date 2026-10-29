from fastapi import APIRouter

from app.models.source import Source
from app.services.catalog.source_service import SourceService

router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


@router.get("/", response_model=list[Source])
def get_sources():
    return SourceService.get_sources()