from fastapi import APIRouter
from app.services.catalog.region_service import RegionService
from app.models.region import Region

router = APIRouter(
    prefix="/regions",
    tags=["Regions"]
)

@router.get("/", response_model=list[Region])
def get_regions():
    return RegionService.get_regions()